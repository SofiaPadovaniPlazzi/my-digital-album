# My Digital Album for iPad

This folder contains a native iPad app wrapper for My Digital Album.

The iPad app uses `WKWebView` to run the same album interface locally, plus a Swift bridge for:

- local save/load on the iPad;
- native photo and video selection through the iPad photo picker;
- touch-friendly drag, resize, and rotate gestures from the web interface.

## Open in Xcode

1. Run the sync script whenever `my_digital_album.py` changes:

   ```bash
   ./ipad-app/sync_web_asset.sh
   ```

2. Open the project:

   ```text
   ipad-app/MyDigitalAlbum.xcodeproj
   ```

3. Choose an iPad simulator or your iPad.

4. Press Run in Xcode.

Album data is saved locally inside the iPad app container as `Library/Application Support/My Digital Album/library.json`.

## Notes

- Xcode is required to build or install the iPad app.
- A real iPad install requires signing with an Apple ID in Xcode.
- The app asks for photo library access only when you choose photos/videos.
- The local password feature is an app lock, not encryption.
