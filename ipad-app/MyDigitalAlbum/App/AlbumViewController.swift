import PhotosUI
import UIKit
import UniformTypeIdentifiers
import WebKit

final class AlbumViewController: UIViewController, WKScriptMessageHandler, PHPickerViewControllerDelegate {
    private var webView: WKWebView!
    private var pendingMediaPageIndex = 0

    private lazy var appSupportURL: URL = {
        let base = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
        return base.appendingPathComponent("My Digital Album", isDirectory: true)
    }()

    private lazy var libraryURL: URL = {
        appSupportURL.appendingPathComponent("library.json")
    }()

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemBackground
        ensureApplicationSupportFolder()
        configureWebView()
        loadAlbumInterface()
    }

    private func configureWebView() {
        let contentController = WKUserContentController()
        contentController.add(self, name: "albumNative")

        let bootstrap = WKUserScript(
            source: nativeBootstrapScript(),
            injectionTime: .atDocumentStart,
            forMainFrameOnly: true
        )
        contentController.addUserScript(bootstrap)

        let configuration = WKWebViewConfiguration()
        configuration.userContentController = contentController
        configuration.websiteDataStore = .default()
        configuration.defaultWebpagePreferences.allowsContentJavaScript = true
        configuration.allowsInlineMediaPlayback = true
        configuration.mediaTypesRequiringUserActionForPlayback = []

        webView = WKWebView(frame: .zero, configuration: configuration)
        webView.translatesAutoresizingMaskIntoConstraints = false
        webView.scrollView.keyboardDismissMode = .interactive
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        webView.allowsBackForwardNavigationGestures = false

        if #available(iOS 16.4, *) {
            webView.isInspectable = true
        }

        view.addSubview(webView)
        NSLayoutConstraint.activate([
            webView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            webView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            webView.topAnchor.constraint(equalTo: view.topAnchor),
            webView.bottomAnchor.constraint(equalTo: view.bottomAnchor)
        ])
    }

    private func loadAlbumInterface() {
        guard let htmlURL = Bundle.main.url(forResource: "index", withExtension: "html") else {
            assertionFailure("Missing index.html in iPad app bundle")
            return
        }
        webView.loadFileURL(htmlURL, allowingReadAccessTo: htmlURL.deletingLastPathComponent())
    }

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard message.name == "albumNative",
              let body = message.body as? [String: Any],
              let type = body["type"] as? String
        else {
            return
        }

        switch type {
        case "save":
            guard let payload = body["payload"] as? String else { return }
            saveLibrary(payload)
        case "selectMedia":
            pendingMediaPageIndex = body["pageIndex"] as? Int ?? 0
            presentPhotoPicker()
        default:
            break
        }
    }

    private func saveLibrary(_ payload: String) {
        ensureApplicationSupportFolder()
        do {
            try payload.write(to: libraryURL, atomically: true, encoding: .utf8)
        } catch {
            NSLog("My Digital Album iPad save failed: \(error.localizedDescription)")
        }
    }

    private func presentPhotoPicker() {
        var configuration = PHPickerConfiguration(photoLibrary: .shared())
        configuration.filter = .any(of: [.images, .videos])
        configuration.selectionLimit = 0
        configuration.preferredAssetRepresentationMode = .compatible

        let picker = PHPickerViewController(configuration: configuration)
        picker.delegate = self
        picker.modalPresentationStyle = .formSheet
        present(picker, animated: true)
    }

    func picker(_ picker: PHPickerViewController, didFinishPicking results: [PHPickerResult]) {
        picker.dismiss(animated: true)
        guard !results.isEmpty else { return }

        let group = DispatchGroup()
        let lock = NSLock()
        var files: [[String: String]] = []

        for result in results {
            let provider = result.itemProvider
            if provider.hasItemConformingToTypeIdentifier(UTType.movie.identifier) {
                group.enter()
                loadVideo(from: provider) { item in
                    if let item {
                        lock.lock()
                        files.append(item)
                        lock.unlock()
                    }
                    group.leave()
                }
            } else if provider.canLoadObject(ofClass: UIImage.self) {
                group.enter()
                loadImage(from: provider) { item in
                    if let item {
                        lock.lock()
                        files.append(item)
                        lock.unlock()
                    }
                    group.leave()
                }
            }
        }

        group.notify(queue: .main) { [weak self] in
            self?.sendMediaFilesToWeb(files)
        }
    }

    private func loadImage(from provider: NSItemProvider, completion: @escaping ([String: String]?) -> Void) {
        provider.loadObject(ofClass: UIImage.self) { object, _ in
            guard let image = object as? UIImage,
                  let data = image.jpegData(compressionQuality: 0.86)
            else {
                completion(nil)
                return
            }

            let name = provider.suggestedName.map { "\($0).jpg" } ?? "photo.jpg"
            completion([
                "name": name,
                "type": "image/jpeg",
                "mediaType": "image",
                "src": "data:image/jpeg;base64,\(data.base64EncodedString())"
            ])
        }
    }

    private func loadVideo(from provider: NSItemProvider, completion: @escaping ([String: String]?) -> Void) {
        provider.loadFileRepresentation(forTypeIdentifier: UTType.movie.identifier) { url, _ in
            guard let url else {
                completion(nil)
                return
            }

            do {
                let ext = url.pathExtension.isEmpty ? "mov" : url.pathExtension
                let temporaryURL = FileManager.default.temporaryDirectory
                    .appendingPathComponent(UUID().uuidString)
                    .appendingPathExtension(ext)
                try FileManager.default.copyItem(at: url, to: temporaryURL)
                let data = try Data(contentsOf: temporaryURL)
                try? FileManager.default.removeItem(at: temporaryURL)

                let mimeType = Self.mimeType(forExtension: ext)
                let name = provider.suggestedName.map { "\($0).\(ext)" } ?? "video.\(ext)"
                completion([
                    "name": name,
                    "type": mimeType,
                    "mediaType": "video",
                    "src": "data:\(mimeType);base64,\(data.base64EncodedString())"
                ])
            } catch {
                NSLog("My Digital Album iPad video import failed: \(error.localizedDescription)")
                completion(nil)
            }
        }
    }

    private func sendMediaFilesToWeb(_ files: [[String: String]]) {
        guard !files.isEmpty,
              let data = try? JSONSerialization.data(withJSONObject: files),
              let json = String(data: data, encoding: .utf8)
        else {
            return
        }

        let script = "window.__receiveNativeMediaFiles && window.__receiveNativeMediaFiles(\(json), \(pendingMediaPageIndex));"
        webView.evaluateJavaScript(script)
    }

    private func ensureApplicationSupportFolder() {
        do {
            try FileManager.default.createDirectory(at: appSupportURL, withIntermediateDirectories: true)
        } catch {
            NSLog("My Digital Album iPad could not create Application Support folder: \(error.localizedDescription)")
        }
    }

    private func nativeBootstrapScript() -> String {
        let storedLibrary = (try? String(contentsOf: libraryURL, encoding: .utf8)) ?? ""
        return """
        window.__MY_DIGITAL_ALBUM_NATIVE__ = true;
        window.__MY_DIGITAL_ALBUM_TOUCH__ = true;
        window.__NATIVE_ALBUM_DATA__ = \(Self.javaScriptStringLiteral(storedLibrary));
        window.__MY_DIGITAL_ALBUM_STORAGE_PATH__ = \(Self.javaScriptStringLiteral(libraryURL.path));
        """
    }

    private static func javaScriptStringLiteral(_ value: String) -> String {
        guard let data = try? JSONSerialization.data(withJSONObject: [value]),
              let arrayLiteral = String(data: data, encoding: .utf8),
              arrayLiteral.count >= 2
        else {
            return "\"\""
        }
        return String(arrayLiteral.dropFirst().dropLast())
    }

    private static func mimeType(forExtension ext: String) -> String {
        switch ext.lowercased() {
        case "mp4":
            return "video/mp4"
        case "m4v":
            return "video/x-m4v"
        case "mov":
            return "video/quicktime"
        default:
            return "video/quicktime"
        }
    }
}
