#import <Cocoa/Cocoa.h>
#import <WebKit/WebKit.h>
#import <UniformTypeIdentifiers/UniformTypeIdentifiers.h>

@interface AppDelegate : NSObject <NSApplicationDelegate, WKScriptMessageHandler>
@property (strong) NSWindow *window;
@property (strong) WKWebView *webView;
@property (strong) NSURL *appSupportURL;
@property (strong) NSURL *libraryURL;
- (void)start;
@end

@implementation AppDelegate

- (instancetype)init {
    self = [super init];
    if (self) {
        NSURL *baseURL = [[[NSFileManager defaultManager] URLsForDirectory:NSApplicationSupportDirectory inDomains:NSUserDomainMask] firstObject];
        _appSupportURL = [baseURL URLByAppendingPathComponent:@"My Digital Album" isDirectory:YES];
        _libraryURL = [_appSupportURL URLByAppendingPathComponent:@"library.json"];
    }
    return self;
}

- (void)applicationDidFinishLaunching:(NSNotification *)notification {
}

- (void)start {
    [NSApp setActivationPolicy:NSApplicationActivationPolicyRegular];
    [self ensureApplicationSupportFolder];

    WKUserContentController *contentController = [[WKUserContentController alloc] init];
    [contentController addScriptMessageHandler:self name:@"albumNative"];
    WKUserScript *bootstrap = [[WKUserScript alloc] initWithSource:[self nativeBootstrapScript]
                                                     injectionTime:WKUserScriptInjectionTimeAtDocumentStart
                                                  forMainFrameOnly:YES];
    [contentController addUserScript:bootstrap];

    WKWebViewConfiguration *configuration = [[WKWebViewConfiguration alloc] init];
    configuration.userContentController = contentController;
    configuration.websiteDataStore = [WKWebsiteDataStore defaultDataStore];
    configuration.preferences.javaScriptCanOpenWindowsAutomatically = YES;

    self.webView = [[WKWebView alloc] initWithFrame:NSZeroRect configuration:configuration];
    self.webView.allowsMagnification = YES;

    NSRect frame = NSMakeRect(0, 0, 1320, 860);
    self.window = [[NSWindow alloc] initWithContentRect:frame
                                              styleMask:NSWindowStyleMaskTitled | NSWindowStyleMaskClosable | NSWindowStyleMaskMiniaturizable | NSWindowStyleMaskResizable | NSWindowStyleMaskFullSizeContentView
                                                backing:NSBackingStoreBuffered
                                                  defer:NO];
    self.window.title = @"My Digital Album";
    self.window.minSize = NSMakeSize(980, 680);
    self.window.contentView = self.webView;
    [self.window center];
    [self.window makeKeyAndOrderFront:nil];
    [NSApp activateIgnoringOtherApps:YES];

    [self loadAlbumInterface];
}

- (BOOL)applicationShouldTerminateAfterLastWindowClosed:(NSApplication *)sender {
    return YES;
}

- (void)userContentController:(WKUserContentController *)userContentController didReceiveScriptMessage:(WKScriptMessage *)message {
    if (![message.name isEqualToString:@"albumNative"] || ![message.body isKindOfClass:[NSDictionary class]]) {
        return;
    }

    NSDictionary *body = (NSDictionary *)message.body;
    NSString *type = body[@"type"];
    if ([type isEqualToString:@"selectMedia"]) {
        NSNumber *pageIndex = [body[@"pageIndex"] isKindOfClass:[NSNumber class]] ? body[@"pageIndex"] : @(0);
        [self selectMediaForPageIndex:pageIndex.integerValue];
        return;
    }

    if (![type isEqualToString:@"save"] || ![body[@"payload"] isKindOfClass:[NSString class]]) {
        return;
    }

    [self ensureApplicationSupportFolder];
    NSError *error = nil;
    [body[@"payload"] writeToURL:self.libraryURL atomically:YES encoding:NSUTF8StringEncoding error:&error];
    if (error) {
        NSLog(@"My Digital Album save failed: %@", error.localizedDescription);
    }
}

- (void)selectMediaForPageIndex:(NSInteger)pageIndex {
    NSOpenPanel *panel = [NSOpenPanel openPanel];
    panel.canChooseFiles = YES;
    panel.canChooseDirectories = NO;
    panel.allowsMultipleSelection = YES;
    panel.allowedContentTypes = @[UTTypeImage, UTTypeMovie, UTTypeVideo, UTTypeAudiovisualContent];

    [panel beginSheetModalForWindow:self.window completionHandler:^(NSModalResponse result) {
        if (result != NSModalResponseOK) {
            return;
        }

        NSMutableArray *files = [NSMutableArray array];
        for (NSURL *url in panel.URLs) {
            NSData *data = [NSData dataWithContentsOfURL:url];
            if (!data) {
                continue;
            }
            NSString *mimeType = [self mimeTypeForURL:url];
            NSString *mediaType = [mimeType hasPrefix:@"video/"] ? @"video" : @"image";
            NSString *base64 = [data base64EncodedStringWithOptions:0];
            NSString *src = [NSString stringWithFormat:@"data:%@;base64,%@", mimeType, base64];
            [files addObject:@{
                @"name": url.lastPathComponent ?: @"media",
                @"type": mimeType,
                @"mediaType": mediaType,
                @"src": src
            }];
        }

        NSData *json = [NSJSONSerialization dataWithJSONObject:files options:0 error:nil];
        NSString *jsonText = [[NSString alloc] initWithData:json encoding:NSUTF8StringEncoding] ?: @"[]";
        NSString *script = [NSString stringWithFormat:@"window.__receiveNativeMediaFiles && window.__receiveNativeMediaFiles(%@, %ld);", jsonText, (long)pageIndex];
        [self.webView evaluateJavaScript:script completionHandler:nil];
    }];
}

- (NSString *)mimeTypeForURL:(NSURL *)url {
    NSString *ext = url.pathExtension.lowercaseString;
    NSDictionary *types = @{
        @"jpg": @"image/jpeg",
        @"jpeg": @"image/jpeg",
        @"png": @"image/png",
        @"gif": @"image/gif",
        @"heic": @"image/heic",
        @"webp": @"image/webp",
        @"tif": @"image/tiff",
        @"tiff": @"image/tiff",
        @"mov": @"video/quicktime",
        @"mp4": @"video/mp4",
        @"m4v": @"video/x-m4v",
        @"avi": @"video/x-msvideo"
    };
    return types[ext] ?: @"application/octet-stream";
}

- (void)loadAlbumInterface {
    NSURL *htmlURL = [[NSBundle mainBundle] URLForResource:@"index" withExtension:@"html"];
    if (!htmlURL) {
        NSLog(@"Missing index.html in app bundle");
        [NSApp terminate:nil];
        return;
    }
    [self.webView loadFileURL:htmlURL allowingReadAccessToURL:[htmlURL URLByDeletingLastPathComponent]];
}

- (void)ensureApplicationSupportFolder {
    NSError *error = nil;
    [[NSFileManager defaultManager] createDirectoryAtURL:self.appSupportURL
                             withIntermediateDirectories:YES
                                              attributes:nil
                                                   error:&error];
    if (error) {
        NSLog(@"My Digital Album could not create Application Support folder: %@", error.localizedDescription);
    }
}

- (NSString *)nativeBootstrapScript {
    NSString *storedLibrary = [NSString stringWithContentsOfURL:self.libraryURL encoding:NSUTF8StringEncoding error:nil] ?: @"";
    return [NSString stringWithFormat:
            @"window.__MY_DIGITAL_ALBUM_NATIVE__ = true;\n"
            "window.__NATIVE_ALBUM_DATA__ = %@;\n"
            "window.__MY_DIGITAL_ALBUM_STORAGE_PATH__ = %@;\n",
            [self javaScriptStringLiteral:storedLibrary],
            [self javaScriptStringLiteral:self.libraryURL.path]];
}

- (NSString *)javaScriptStringLiteral:(NSString *)value {
    NSData *data = [NSJSONSerialization dataWithJSONObject:@[value] options:0 error:nil];
    if (!data) {
        return @"\"\"";
    }
    NSString *arrayLiteral = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding] ?: @"[\"\"]";
    if (arrayLiteral.length >= 2) {
        return [arrayLiteral substringWithRange:NSMakeRange(1, arrayLiteral.length - 2)];
    }
    return @"\"\"";
}

@end

int main(int argc, const char * argv[]) {
    @autoreleasepool {
        NSApplication *application = [NSApplication sharedApplication];
        static AppDelegate *delegate;
        delegate = [[AppDelegate alloc] init];
        application.delegate = delegate;
        [delegate start];
        [application run];
        return 0;
    }
}
