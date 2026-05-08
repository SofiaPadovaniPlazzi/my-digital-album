from http.server import BaseHTTPRequestHandler, HTTPServer
from socket import error as SocketError
from socketserver import ThreadingMixIn
import webbrowser


APP_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>My Digital Album</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f6f1ea;
      --paper: #fff8ec;
      --cover: #d9a6a6;
      --ink: #302822;
      --muted: #7b7068;
      --line: rgba(58, 42, 31, 0.18);
      --field: rgba(255, 255, 255, 0.72);
      --accent: #b96f6b;
      --accent-ink: #fffaf5;
      --shadow: 0 18px 50px rgba(67, 43, 25, 0.14);
      --radius: 8px;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--ink);
    }

    button, input, select, textarea {
      font: inherit;
    }

    button {
      border: 0;
      cursor: pointer;
    }

    .app {
      min-height: 100vh;
      display: grid;
      grid-template-columns: 340px minmax(0, 1fr);
    }

    aside {
      border-right: 1px solid var(--line);
      padding: 22px;
      background: rgba(255, 255, 255, 0.42);
      backdrop-filter: blur(18px);
      overflow: auto;
    }

    main {
      padding: 22px;
      overflow: auto;
    }

    h1, h2, h3, p {
      margin-top: 0;
    }

    h1 {
      font-size: 28px;
      line-height: 1.05;
      margin-bottom: 8px;
    }

    h2 {
      font-size: 17px;
      margin-bottom: 12px;
    }

    p {
      color: var(--muted);
      line-height: 1.5;
    }

    .brand {
      margin-bottom: 22px;
    }

    .brand p {
      margin-bottom: 0;
      font-size: 14px;
    }

    .panel {
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: rgba(255, 255, 255, 0.58);
      box-shadow: var(--shadow);
      padding: 16px;
      margin-bottom: 14px;
    }

    .field {
      display: grid;
      gap: 7px;
      margin-bottom: 13px;
    }

    label {
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.02em;
    }

    input, select, textarea {
      width: 100%;
      min-height: 40px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--field);
      color: var(--ink);
      padding: 9px 10px;
      outline: none;
    }

    textarea {
      min-height: 86px;
      resize: vertical;
    }

    input[type="color"] {
      height: 42px;
      padding: 4px;
    }

    .segmented {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 6px;
    }

    .segmented.three {
      grid-template-columns: repeat(3, 1fr);
    }

    .choice, .icon-button, .primary, .secondary, .danger {
      min-height: 40px;
      border-radius: 8px;
      font-weight: 900;
    }

    .choice {
      border: 1px solid var(--line);
      background: var(--field);
      color: var(--ink);
    }

    .choice.active {
      border-color: var(--accent);
      box-shadow: inset 0 -3px 0 var(--accent);
    }

    .primary {
      width: 100%;
      background: var(--accent);
      color: var(--accent-ink);
    }

    .secondary, .icon-button {
      border: 1px solid var(--line);
      background: var(--field);
      color: var(--ink);
    }

    .danger {
      border: 1px solid rgba(186, 66, 66, 0.3);
      background: rgba(255, 255, 255, 0.5);
      color: #b84242;
    }

    .row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }

    .toolbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 18px;
    }

    .toolbar-actions {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }

    .top-tabs {
      display: flex;
      gap: 8px;
      margin-bottom: 16px;
    }

    .top-tab {
      min-height: 38px;
      padding: 0 14px;
      border-radius: 8px;
      border: 1px solid var(--line);
      background: var(--field);
      color: var(--ink);
      font-weight: 900;
    }

    .top-tab.active {
      background: var(--ink);
      color: var(--bg);
    }

    .view {
      display: none;
    }

    .view.active {
      display: block;
    }

    .library-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      gap: 18px;
      width: min(980px, 100%);
    }

    .library-card {
      display: grid;
      gap: 12px;
      min-height: 280px;
      padding: 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.58);
      box-shadow: var(--shadow);
      text-align: left;
    }

    .book-cover {
      position: relative;
      min-height: 210px;
      border-radius: 8px;
      overflow: hidden;
      background: var(--book-cover, #d9a6a6);
      color: rgba(255, 255, 255, 0.94);
      box-shadow: inset 12px 0 18px rgba(64, 35, 22, 0.16), 0 12px 24px rgba(64, 35, 22, 0.16);
    }

    .book-cover::before {
      content: "";
      position: absolute;
      inset: 0;
      background: var(--book-art);
      opacity: 0.95;
    }

    .book-cover::after {
      content: "";
      position: absolute;
      top: 0;
      bottom: 0;
      left: 18px;
      width: 1px;
      background: rgba(255, 255, 255, 0.38);
      box-shadow: 2px 0 10px rgba(50, 28, 16, 0.22);
    }

    .book-cover-title {
      position: absolute;
      left: 34px;
      right: 18px;
      bottom: 22px;
      font-size: 19px;
      line-height: 1.08;
      font-weight: 950;
      text-shadow: 0 2px 10px rgba(34, 20, 14, 0.26);
    }

    .book-cover-meta {
      color: var(--muted);
      font-size: 13px;
      font-weight: 800;
    }

    .template-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
    }

    .template-card {
      display: grid;
      gap: 6px;
      padding: 8px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--field);
      color: var(--ink);
      text-align: left;
    }

    .template-card.active {
      border-color: var(--accent);
      box-shadow: inset 0 -3px 0 var(--accent);
    }

    .template-card .book-cover {
      min-height: 92px;
      border-radius: 7px;
    }

    .template-card span {
      font-size: 12px;
      font-weight: 900;
    }

    .album-stage {
      display: grid;
      place-items: start center;
      min-height: calc(100vh - 96px);
      padding: 18px;
      border: 1px dashed var(--line);
      border-radius: 8px;
      background:
        linear-gradient(90deg, rgba(255,255,255,0.26) 1px, transparent 1px),
        linear-gradient(rgba(255,255,255,0.26) 1px, transparent 1px);
      background-size: 34px 34px;
    }

    .album {
      width: min(100%, var(--album-width));
      border-radius: 8px;
      background: var(--cover);
      padding: 18px 18px 24px;
      box-shadow: var(--shadow);
      position: relative;
    }

    .album::before {
      content: "";
      position: absolute;
      top: 70px;
      bottom: 24px;
      left: 24px;
      width: 11px;
      border-radius: 99px;
      background: rgba(255, 255, 255, 0.26);
      box-shadow: inset -3px 0 6px rgba(60, 33, 19, 0.16);
    }

    .album.vertical {
      --album-width: 720px;
    }

    .album.horizontal {
      --album-width: 920px;
    }

    .cover-title {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 12px;
      align-items: center;
      margin-bottom: 14px;
      color: rgba(255, 255, 255, 0.9);
    }

    .cover-title input {
      border-color: rgba(255, 255, 255, 0.34);
      background: rgba(255, 255, 255, 0.2);
      color: inherit;
      font-size: 18px;
      font-weight: 900;
    }

    .page-tabs {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
      margin-bottom: 12px;
    }

    .page-tab {
      min-height: 34px;
      padding: 0 12px;
      border-radius: 7px;
      border: 1px solid rgba(255, 255, 255, 0.34);
      background: rgba(255, 255, 255, 0.18);
      color: rgba(255, 255, 255, 0.92);
      font-weight: 900;
    }

    .page-tab.active {
      background: rgba(255, 255, 255, 0.85);
      color: var(--ink);
    }

    .album-page {
      position: relative;
      min-height: var(--page-height);
      border-radius: 8px;
      background: var(--paper);
      padding: 24px;
      overflow: hidden;
      box-shadow:
        inset 0 0 0 1px rgba(69, 49, 32, 0.12),
        inset 18px 0 28px rgba(66, 42, 24, 0.08),
        8px 8px 0 rgba(255, 255, 255, 0.26);
    }

    .album-page::before {
      content: "";
      position: absolute;
      inset: 0;
      z-index: 0;
      pointer-events: none;
      background: var(--page-pattern);
      opacity: 0.88;
    }

    .album-page::after {
      content: "";
      position: absolute;
      top: 72px;
      bottom: 72px;
      left: 12px;
      width: 9px;
      border-radius: 99px;
      background:
        radial-gradient(circle at center, rgba(84, 58, 38, 0.28) 0 3px, transparent 4px) 0 0 / 9px 64px;
      pointer-events: none;
    }

    .album-page > * {
      position: relative;
      z-index: 1;
    }

    .album.vertical .album-page {
      --page-height: 780px;
    }

    .album.horizontal .album-page {
      --page-height: 560px;
    }

    .page-heading {
      display: grid;
      grid-template-columns: 1fr 170px;
      gap: 12px;
      margin-bottom: 16px;
    }

    .photo-grid {
      display: grid;
      gap: 14px;
      min-height: 390px;
    }

    .slots-1 {
      grid-template-columns: 1fr;
    }

    .slots-2 {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .slots-3 {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .slots-3 .photo-slot:first-child {
      grid-row: span 2;
    }

    .slots-4 {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .photo-slot {
      position: relative;
      display: grid;
      grid-template-rows: minmax(160px, 1fr) auto;
      gap: 8px;
      min-height: 214px;
      padding: 9px;
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.34);
      border: 1px solid rgba(80, 58, 41, 0.14);
    }

    .photo-frame {
      position: relative;
      display: grid;
      place-items: center;
      min-height: 160px;
      overflow: hidden;
      background: rgba(255, 255, 255, 0.58);
      border-radius: 8px;
      cursor: pointer;
    }

    .photo-slot.selected {
      outline: 3px solid rgba(185, 111, 107, 0.45);
      outline-offset: 2px;
    }

    .frame-none .photo-frame {
      background: transparent;
    }

    .frame-simple .photo-frame {
      border: 9px solid #fff;
      box-shadow: 0 8px 18px rgba(61, 42, 26, 0.14);
    }

    .frame-corners .photo-frame::before,
    .frame-corners .photo-frame::after,
    .frame-corners .photo-slot::before,
    .frame-corners .photo-slot::after {
      content: "";
      position: absolute;
      z-index: 3;
      width: 24px;
      height: 24px;
      border-color: rgba(78, 56, 39, 0.48);
      pointer-events: none;
    }

    .frame-corners .photo-frame::before {
      top: 8px;
      left: 8px;
      border-top: 3px solid;
      border-left: 3px solid;
    }

    .frame-corners .photo-frame::after {
      top: 8px;
      right: 8px;
      border-top: 3px solid;
      border-right: 3px solid;
    }

    .frame-corners .photo-slot::before {
      bottom: 46px;
      left: 17px;
      border-bottom: 3px solid;
      border-left: 3px solid;
    }

    .frame-corners .photo-slot::after {
      bottom: 46px;
      right: 17px;
      border-bottom: 3px solid;
      border-right: 3px solid;
    }

    .frame-polaroid .photo-slot {
      background: #fffaf2;
      box-shadow: 0 8px 18px rgba(61, 42, 26, 0.13);
    }

    .photo-frame img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      transform-origin: center;
    }

    .photo-actions {
      position: absolute;
      z-index: 4;
      top: 8px;
      right: 8px;
      display: flex;
      gap: 6px;
    }

    .mini-button {
      min-width: 32px;
      min-height: 30px;
      border-radius: 7px;
      border: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.84);
      color: var(--ink);
      font-weight: 950;
    }

    .upload-prompt {
      display: grid;
      gap: 10px;
      justify-items: center;
      color: var(--muted);
      text-align: center;
      padding: 20px;
    }

    .upload-prompt strong {
      color: var(--ink);
    }

    .photo-caption {
      min-height: 38px;
      background: transparent;
    }

    .page-note {
      margin-top: 14px;
      min-height: 78px;
    }

    .sticker-tray {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 8px;
    }

    .sticker-button {
      min-height: 48px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--field);
      display: grid;
      place-items: center;
    }

    .page-sticker {
      position: absolute;
      z-index: 5;
      width: var(--sticker-size);
      height: var(--sticker-size);
      transform: rotate(var(--tilt));
      text-shadow: 0 4px 10px rgba(70, 45, 26, 0.12);
      cursor: grab;
      touch-action: none;
    }

    .page-sticker.selected {
      outline: 2px dashed var(--accent);
      outline-offset: 4px;
      border-radius: 8px;
    }

    .sticker-svg {
      width: 36px;
      height: 36px;
      display: block;
      filter: drop-shadow(0 4px 5px rgba(70, 45, 26, 0.1));
    }

    .page-sticker .sticker-svg {
      width: 100%;
      height: 100%;
    }

    .pin-overlay {
      position: fixed;
      inset: 0;
      z-index: 50;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 24px;
      background: rgba(246, 241, 234, 0.78);
      backdrop-filter: blur(12px);
    }

    .pin-overlay.visible {
      display: flex;
    }

    .pin-card {
      width: min(360px, 100%);
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--paper);
      box-shadow: var(--shadow);
      padding: 20px;
    }

    .pin-dots {
      display: flex;
      justify-content: center;
      gap: 10px;
      margin: 16px 0;
    }

    .pin-dot {
      width: 14px;
      height: 14px;
      border: 2px solid var(--line);
      border-radius: 99px;
    }

    .pin-dot.filled {
      background: var(--accent);
      border-color: var(--accent);
    }

    .pin-pad {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
    }

    .pin-key {
      min-height: 54px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--field);
      color: var(--ink);
      font-size: 20px;
      font-weight: 950;
    }

    .pin-message {
      min-height: 20px;
      margin: 10px 0 0;
      color: #b84242;
      text-align: center;
      font-size: 13px;
      font-weight: 850;
    }

    .hidden {
      display: none;
    }

    @media (max-width: 900px) {
      .app {
        grid-template-columns: 1fr;
      }

      aside {
        border-right: 0;
        border-bottom: 1px solid var(--line);
      }

      .toolbar, .cover-title, .page-heading {
        grid-template-columns: 1fr;
        align-items: stretch;
      }
    }

    @media print {
      aside, .toolbar, .top-tabs, .page-tabs, .cover-title button {
        display: none;
      }

      .app, main, .album-stage {
        display: block;
        padding: 0;
        border: 0;
        background: white;
      }

      .album {
        box-shadow: none;
        width: 100%;
      }
    }
  </style>
</head>
<body>
  <div class="app">
    <aside>
      <div class="brand">
        <h1>My Digital Album</h1>
        <p>Build a sweet photo album from your own pictures, with paper choices, frames, dates, captions, notes, and stickers.</p>
      </div>

      <section class="panel">
        <h2>Album Setup</h2>
        <div class="field">
          <label for="albumTitle">Album title</label>
          <input id="albumTitle" type="text" placeholder="Summer in Italy">
        </div>
        <div class="field">
          <label>Cover template</label>
          <div class="template-grid" id="templateGrid"></div>
        </div>
        <div class="field">
          <label>Orientation</label>
          <div class="segmented">
            <button class="choice active" type="button" data-orientation="vertical">Vertical</button>
            <button class="choice" type="button" data-orientation="horizontal">Horizontal</button>
          </div>
        </div>
        <div class="row">
          <div class="field">
            <label for="paperColor">Paper color</label>
            <input id="paperColor" type="color" value="#fff8ec">
          </div>
          <div class="field">
            <label for="coverColor">Cover color</label>
            <input id="coverColor" type="color" value="#d9a6a6">
          </div>
        </div>
        <div class="field">
          <label for="photosPerPage">Photos per page</label>
          <select id="photosPerPage">
            <option value="1">1 large photo</option>
            <option value="2">2 photos</option>
            <option value="3">3 photos</option>
            <option value="4">4 photos</option>
          </select>
        </div>
        <div class="field">
          <label for="frameStyle">Frames</label>
          <select id="frameStyle">
            <option value="none">No frame</option>
            <option value="simple">Simple frame</option>
            <option value="corners">Photo corners</option>
            <option value="polaroid">Polaroid</option>
          </select>
        </div>
        <div class="field">
          <label for="pagePattern">Page pattern</label>
          <select id="pagePattern">
            <option value="plain">Plain paper</option>
            <option value="dots">Tiny dots</option>
            <option value="grid">Soft grid</option>
            <option value="hearts">Little hearts</option>
            <option value="pressed">Pressed flowers</option>
          </select>
        </div>
        <div class="row">
          <button class="primary" id="createAlbum" type="button">New album</button>
          <button class="secondary" id="duplicateAlbum" type="button">Duplicate</button>
        </div>
      </section>

      <section class="panel">
        <h2>Page Tools</h2>
        <div class="field">
          <label for="pageTitle">Page title</label>
          <input id="pageTitle" type="text" placeholder="A soft morning">
        </div>
        <div class="field">
          <label for="pageDate">Date</label>
          <input id="pageDate" type="date">
        </div>
        <div class="field">
          <label for="pageText">Random text / memory</label>
          <textarea id="pageText" placeholder="Write a memory, a quote, or something tiny from that day."></textarea>
        </div>
        <div class="field">
          <label>Cute stickers</label>
          <div class="sticker-tray" id="stickerTray"></div>
        </div>
        <div class="field">
          <label for="stickerSize">Sticker size</label>
          <input id="stickerSize" type="range" min="30" max="120" value="52">
        </div>
        <div class="row">
          <button class="secondary" id="addPage" type="button">Add page</button>
          <button class="danger" id="deletePage" type="button">Delete page</button>
        </div>
      </section>

      <section class="panel" id="cropPanel">
        <h2>Selected Photo</h2>
        <div class="field">
          <label for="cropZoom">Zoom</label>
          <input id="cropZoom" type="range" min="1" max="2.4" step="0.05" value="1">
        </div>
        <div class="row">
          <div class="field">
            <label for="cropX">Move X</label>
            <input id="cropX" type="range" min="0" max="100" value="50">
          </div>
          <div class="field">
            <label for="cropY">Move Y</label>
            <input id="cropY" type="range" min="0" max="100" value="50">
          </div>
        </div>
        <button class="secondary" id="removePhoto" type="button">Remove photo</button>
      </section>

      <section class="panel">
        <h2>Privacy</h2>
        <div class="row">
          <button class="secondary" id="passwordButton" type="button">Password</button>
          <button class="secondary" id="exportHtmlButton" type="button">Export HTML</button>
        </div>
      </section>
    </aside>

    <main>
      <div class="top-tabs">
        <button class="top-tab active" id="libraryTab" type="button">Library</button>
        <button class="top-tab" id="editorTab" type="button">Editor</button>
      </div>
      <div class="toolbar">
        <div>
          <h2 id="modeTitle">Album preview</h2>
          <p id="helperText">Create an album, then upload pictures into each page slot.</p>
        </div>
        <div class="toolbar-actions">
          <button class="secondary" id="exportButton" type="button">Print / Save PDF</button>
          <button class="danger" id="resetButton" type="button">Reset</button>
        </div>
      </div>

      <div class="view active" id="libraryView">
        <div class="album-stage">
          <div class="library-grid" id="libraryGrid"></div>
        </div>
      </div>

      <div class="view" id="editorView">
      <div class="album-stage">
        <section class="album vertical frame-none" id="album">
          <div class="cover-title">
            <input id="coverTitle" type="text" value="My Digital Album" aria-label="Album cover title">
            <button class="secondary" id="saveButton" type="button">Save</button>
          </div>
          <div class="page-tabs" id="pageTabs"></div>
          <article class="album-page" id="albumPage"></article>
        </section>
      </div>
      </div>
    </main>
  </div>

  <div class="pin-overlay" id="pinOverlay" aria-modal="true" role="dialog"></div>

  <script>
    const legacyStorageKey = "my-digital-album-v1";
    const storageKey = "my-digital-album-library-v2";
    const sessionKey = "my-digital-album-unlocked";
    const templates = [
      {
        id: "travel",
        name: "Travel",
        coverColor: "#6fa8b5",
        paperColor: "#fff7e6",
        pattern: "pressed",
        art: "radial-gradient(circle at 72% 18%, rgba(255,255,255,.72) 0 9px, transparent 10px), linear-gradient(135deg, transparent 0 46%, rgba(255,255,255,.28) 47% 53%, transparent 54%), radial-gradient(circle at 22% 72%, rgba(255,217,128,.78) 0 24px, transparent 25px)"
      },
      {
        id: "family",
        name: "Family",
        coverColor: "#d79ca8",
        paperColor: "#fff6f2",
        pattern: "hearts",
        art: "radial-gradient(circle at 30% 24%, rgba(255,255,255,.72) 0 18px, transparent 19px), radial-gradient(circle at 62% 64%, rgba(255,238,196,.85) 0 26px, transparent 27px), linear-gradient(45deg, transparent 0 70%, rgba(255,255,255,.25) 71%)"
      },
      {
        id: "birthday",
        name: "Birthday",
        coverColor: "#f0b45d",
        paperColor: "#fff9df",
        pattern: "dots",
        art: "radial-gradient(circle at 24% 22%, rgba(255,255,255,.75) 0 7px, transparent 8px), radial-gradient(circle at 70% 38%, rgba(255,126,159,.7) 0 11px, transparent 12px), radial-gradient(circle at 46% 72%, rgba(126,214,196,.75) 0 12px, transparent 13px)"
      },
      {
        id: "graduation",
        name: "Graduation",
        coverColor: "#52627e",
        paperColor: "#fbf7ef",
        pattern: "grid",
        art: "linear-gradient(135deg, rgba(255,255,255,.35) 0 18%, transparent 19%), radial-gradient(circle at 72% 24%, rgba(246,196,83,.9) 0 15px, transparent 16px), linear-gradient(90deg, transparent 0 18px, rgba(255,255,255,.2) 19px 20px, transparent 21px)"
      },
      {
        id: "wedding",
        name: "Wedding",
        coverColor: "#c7b7a6",
        paperColor: "#fffaf3",
        pattern: "pressed",
        art: "radial-gradient(circle at 28% 28%, rgba(255,255,255,.8) 0 22px, transparent 23px), radial-gradient(circle at 70% 68%, rgba(255,235,226,.86) 0 30px, transparent 31px), linear-gradient(120deg, transparent 0 58%, rgba(255,255,255,.28) 59%)"
      }
    ];
    const pagePatterns = {
      plain: "linear-gradient(transparent, transparent)",
      dots: "radial-gradient(circle, rgba(91,67,45,.14) 0 1px, transparent 1.5px) 0 0 / 18px 18px",
      grid: "linear-gradient(rgba(91,67,45,.09) 1px, transparent 1px), linear-gradient(90deg, rgba(91,67,45,.09) 1px, transparent 1px)",
      hearts: "radial-gradient(circle at 40% 42%, rgba(255,154,174,.22) 0 5px, transparent 6px), radial-gradient(circle at 60% 42%, rgba(255,154,174,.22) 0 5px, transparent 6px), linear-gradient(45deg, transparent 43%, rgba(255,154,174,.2) 44% 56%, transparent 57%)",
      pressed: "radial-gradient(ellipse at 18% 22%, rgba(126,190,143,.18) 0 18px, transparent 19px), radial-gradient(ellipse at 82% 76%, rgba(255,155,193,.14) 0 20px, transparent 21px)"
    };
    const stickers = [
      {
        id: "flower",
        label: "Flower",
        art: `<svg class="sticker-svg" viewBox="0 0 64 64" aria-hidden="true"><circle cx="32" cy="32" r="8" fill="#ffd76a"/><ellipse cx="32" cy="15" rx="9" ry="13" fill="#ff9bc1"/><ellipse cx="32" cy="49" rx="9" ry="13" fill="#ff9bc1"/><ellipse cx="15" cy="32" rx="13" ry="9" fill="#ff9bc1"/><ellipse cx="49" cy="32" rx="13" ry="9" fill="#ff9bc1"/><circle cx="32" cy="32" r="5" fill="#fff4a3"/></svg>`
      },
      {
        id: "sparkle",
        label: "Sparkle",
        art: `<svg class="sticker-svg" viewBox="0 0 64 64" aria-hidden="true"><path d="M31 7 37 25 55 31 37 38 31 57 24 38 7 31 24 25Z" fill="#ffd45f" stroke="#b77621" stroke-width="2" stroke-linejoin="round"/><path d="M50 7 52 14 59 16 52 19 50 26 47 19 41 16 47 14Z" fill="#fff0a7"/></svg>`
      },
      {
        id: "letter",
        label: "Love note",
        art: `<svg class="sticker-svg" viewBox="0 0 64 64" aria-hidden="true"><rect x="10" y="17" width="44" height="32" rx="6" fill="#fff7ef" stroke="#c98c7b" stroke-width="2"/><path d="m13 22 19 16 19-16" fill="none" stroke="#c98c7b" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/><path d="M32 44c-7-4-11-8-11-12a5 5 0 0 1 9-3 5 5 0 0 1 9 3c0 4-4 8-7 12Z" fill="#ff8aa6"/></svg>`
      },
      {
        id: "moon",
        label: "Moon",
        art: `<svg class="sticker-svg" viewBox="0 0 64 64" aria-hidden="true"><path d="M42 8A25 25 0 1 0 55 45 22 22 0 1 1 42 8Z" fill="#c9b7ff" stroke="#7b64c7" stroke-width="2"/><circle cx="21" cy="18" r="3" fill="#ffe28a"/><circle cx="49" cy="15" r="2.5" fill="#ffe28a"/></svg>`
      },
      {
        id: "berry",
        label: "Berry",
        art: `<svg class="sticker-svg" viewBox="0 0 64 64" aria-hidden="true"><path d="M32 16c11 0 19 8 19 19 0 12-9 22-19 22S13 47 13 35c0-11 8-19 19-19Z" fill="#ff6f91" stroke="#b8425d" stroke-width="2"/><path d="M25 17c1-7 6-10 13-10-1 7-5 10-13 10Z" fill="#73c88f"/><path d="M32 16c-4-5-9-6-14-4 3 5 7 7 14 4Z" fill="#8bd69d"/><circle cx="25" cy="33" r="2" fill="#ffe0e8"/><circle cx="36" cy="38" r="2" fill="#ffe0e8"/><circle cx="31" cy="48" r="2" fill="#ffe0e8"/></svg>`
      },
      {
        id: "ribbon",
        label: "Ribbon",
        art: `<svg class="sticker-svg" viewBox="0 0 64 64" aria-hidden="true"><path d="M30 24C22 12 11 13 8 24c3 11 14 12 22 0Z" fill="#ff9ccf" stroke="#b85d92" stroke-width="2" stroke-linejoin="round"/><path d="M34 24c8-12 19-11 22 0-3 11-14 12-22 0Z" fill="#ff9ccf" stroke="#b85d92" stroke-width="2" stroke-linejoin="round"/><rect x="25" y="20" width="14" height="14" rx="5" fill="#ffe1ef" stroke="#b85d92" stroke-width="2"/></svg>`
      },
      {
        id: "cloud",
        label: "Cloud",
        art: `<svg class="sticker-svg" viewBox="0 0 64 64" aria-hidden="true"><path d="M18 45a10 10 0 0 1 1-20 15 15 0 0 1 28 5 8 8 0 0 1-2 15Z" fill="#dbefff" stroke="#7aa6cc" stroke-width="2" stroke-linejoin="round"/><path d="M25 47c0 4-4 8-4 8s-4-4-4-8a4 4 0 0 1 8 0ZM42 47c0 4-4 8-4 8s-4-4-4-8a4 4 0 0 1 8 0Z" fill="#9fc7ff"/></svg>`
      },
      {
        id: "star",
        label: "Star",
        art: `<svg class="sticker-svg" viewBox="0 0 64 64" aria-hidden="true"><path d="m32 7 7 16 17 2-13 11 4 17-15-9-15 9 4-17L8 25l17-2Z" fill="#ffcf6a" stroke="#bf7c24" stroke-width="2" stroke-linejoin="round"/><path d="M24 31c4 4 12 4 16 0" fill="none" stroke="#8b5b24" stroke-width="2" stroke-linecap="round"/></svg>`
      }
    ];
    const defaultLibrary = {
      activeAlbumId: "",
      security: { pinHash: "" },
      albums: []
    };

    let library = loadLibrary();
    let album = activeAlbum();
    let activeView = "library";
    let activePageIndex = 0;
    let selectedPhotoIndex = null;
    let selectedStickerId = null;
    let draggingSticker = null;
    let pinMode = "unlock";
    let pinBuffer = "";
    let pinMessage = "";
    let pendingPin = "";

    const albumEl = document.getElementById("album");
    const albumPage = document.getElementById("albumPage");
    const pageTabs = document.getElementById("pageTabs");
    const libraryGrid = document.getElementById("libraryGrid");
    const templateGrid = document.getElementById("templateGrid");
    const stickerTray = document.getElementById("stickerTray");
    const albumTitle = document.getElementById("albumTitle");
    const coverTitle = document.getElementById("coverTitle");
    const paperColor = document.getElementById("paperColor");
    const coverColor = document.getElementById("coverColor");
    const photosPerPage = document.getElementById("photosPerPage");
    const frameStyle = document.getElementById("frameStyle");
    const pagePattern = document.getElementById("pagePattern");
    const pageTitle = document.getElementById("pageTitle");
    const pageDate = document.getElementById("pageDate");
    const pageText = document.getElementById("pageText");
    const stickerSize = document.getElementById("stickerSize");
    const cropPanel = document.getElementById("cropPanel");
    const cropZoom = document.getElementById("cropZoom");
    const cropX = document.getElementById("cropX");
    const cropY = document.getElementById("cropY");
    const libraryTab = document.getElementById("libraryTab");
    const editorTab = document.getElementById("editorTab");
    const libraryView = document.getElementById("libraryView");
    const editorView = document.getElementById("editorView");
    const pinOverlay = document.getElementById("pinOverlay");

    document.getElementById("createAlbum").addEventListener("click", createAlbumFromOptions);
    document.getElementById("duplicateAlbum").addEventListener("click", duplicateAlbum);
    document.getElementById("addPage").addEventListener("click", addPage);
    document.getElementById("deletePage").addEventListener("click", deletePage);
    document.getElementById("saveButton").addEventListener("click", saveLibrary);
    document.getElementById("exportButton").addEventListener("click", () => window.print());
    document.getElementById("exportHtmlButton").addEventListener("click", exportSingleHtml);
    document.getElementById("resetButton").addEventListener("click", resetAlbum);
    document.getElementById("passwordButton").addEventListener("click", openPasswordSettings);
    document.getElementById("removePhoto").addEventListener("click", removeSelectedPhoto);
    libraryTab.addEventListener("click", () => setView("library"));
    editorTab.addEventListener("click", () => setView("editor"));

    coverTitle.addEventListener("input", () => {
      album.title = coverTitle.value || "My Digital Album";
      albumTitle.value = album.title;
      saveLibrary();
      renderLibrary();
      renderTabs();
    });

    [albumTitle, paperColor, coverColor, photosPerPage, frameStyle, pagePattern].forEach((input) => {
      input.addEventListener("input", updateAlbumOptions);
      input.addEventListener("change", updateAlbumOptions);
    });

    [pageTitle, pageDate, pageText].forEach((input) => {
      input.addEventListener("input", updatePageText);
    });

    [cropZoom, cropX, cropY].forEach((input) => {
      input.addEventListener("input", updateSelectedPhotoCrop);
    });

    stickerSize.addEventListener("input", () => {
      const sticker = selectedSticker();
      if (!sticker) return;
      sticker.size = Number(stickerSize.value);
      saveLibrary();
      renderPage();
    });

    document.querySelectorAll("[data-orientation]").forEach((button) => {
      button.addEventListener("click", () => {
        album.orientation = button.dataset.orientation;
        saveLibrary();
        render();
      });
    });

    function blankPage() {
      return {
        title: "",
        date: "",
        text: "",
        photos: [],
        stickers: []
      };
    }

    function blankAlbum(templateId = "family", title = "") {
      const template = templates.find((item) => item.id === templateId) ?? templates[0];
      return {
        id: crypto.randomUUID(),
        title: title || `${template.name} Album`,
        template: template.id,
        orientation: "vertical",
        paperColor: template.paperColor,
        coverColor: template.coverColor,
        photosPerPage: 2,
        frameStyle: "simple",
        pagePattern: template.pattern,
        pages: [blankPage()]
      };
    }

    function normalizeAlbum(saved) {
      const fallback = blankAlbum(saved?.template ?? "family", saved?.title);
      return {
        ...fallback,
        ...saved,
        id: saved?.id ?? crypto.randomUUID(),
        pagePattern: saved?.pagePattern ?? fallback.pagePattern,
        pages: saved?.pages?.length ? saved.pages.map((page) => ({
          ...blankPage(),
          ...page,
          photos: (page.photos ?? []).map((photo) => photo ? ({
            ...photo,
            cropX: photo.cropX ?? 50,
            cropY: photo.cropY ?? 50,
            zoom: photo.zoom ?? 1
          }) : null),
          stickers: (page.stickers ?? []).map((sticker) => ({
            id: sticker.id ?? sticker.value,
            x: sticker.x ?? 12,
            y: sticker.y ?? 12,
            tilt: sticker.tilt ?? 0,
            size: sticker.size ?? 52
          }))
        })) : [blankPage()]
      };
    }

    function loadLibrary() {
      const stored = localStorage.getItem(storageKey);
      if (stored) {
        try {
          const saved = JSON.parse(stored);
          const albums = saved.albums?.length ? saved.albums.map(normalizeAlbum) : [blankAlbum()];
          return {
            ...defaultLibrary,
            ...saved,
            albums,
            activeAlbumId: saved.activeAlbumId && albums.some((item) => item.id === saved.activeAlbumId) ? saved.activeAlbumId : albums[0].id,
            security: { pinHash: saved.security?.pinHash ?? "" }
          };
        } catch {}
      }

      const legacy = localStorage.getItem(legacyStorageKey);
      if (legacy) {
        try {
          const migrated = normalizeAlbum(JSON.parse(legacy));
          return { ...defaultLibrary, activeAlbumId: migrated.id, albums: [migrated] };
        } catch {}
      }

      const first = blankAlbum("family", "My Digital Album");
      return { ...defaultLibrary, activeAlbumId: first.id, albums: [first] };
    }

    function activeAlbum() {
      return library.albums.find((item) => item.id === library.activeAlbumId) ?? library.albums[0];
    }

    function saveLibrary() {
      localStorage.setItem(storageKey, JSON.stringify(library));
    }

    function createAlbumFromOptions() {
      const templateId = album?.template ?? "family";
      const next = blankAlbum(templateId, albumTitle.value || "");
      next.orientation = album.orientation;
      next.paperColor = paperColor.value;
      next.coverColor = coverColor.value;
      next.photosPerPage = Number(photosPerPage.value);
      next.frameStyle = frameStyle.value;
      next.pagePattern = pagePattern.value;
      library.albums.push(next);
      library.activeAlbumId = next.id;
      album = next;
      activePageIndex = 0;
      selectedPhotoIndex = null;
      selectedStickerId = null;
      setView("editor", false);
      saveLibrary();
      render();
    }

    function duplicateAlbum() {
      const copy = normalizeAlbum(JSON.parse(JSON.stringify(album)));
      copy.id = crypto.randomUUID();
      copy.title = `${album.title} Copy`;
      library.albums.push(copy);
      library.activeAlbumId = copy.id;
      album = copy;
      activePageIndex = 0;
      saveLibrary();
      render();
    }

    function updateAlbumOptions() {
      album.title = albumTitle.value || "My Digital Album";
      album.paperColor = paperColor.value;
      album.coverColor = coverColor.value;
      album.photosPerPage = Number(photosPerPage.value);
      album.frameStyle = frameStyle.value;
      album.pagePattern = pagePattern.value;
      coverTitle.value = album.title;
      trimExtraPhotos();
      saveLibrary();
      render();
    }

    function applyTemplate(templateId) {
      const template = templates.find((item) => item.id === templateId);
      if (!template) return;
      album.template = template.id;
      album.coverColor = template.coverColor;
      album.paperColor = template.paperColor;
      album.pagePattern = template.pattern;
      saveLibrary();
      render();
    }

    function setView(view, shouldRender = true) {
      activeView = view;
      libraryTab.classList.toggle("active", view === "library");
      editorTab.classList.toggle("active", view === "editor");
      libraryView.classList.toggle("active", view === "library");
      editorView.classList.toggle("active", view === "editor");
      document.getElementById("modeTitle").textContent = view === "library" ? "Album library" : "Album editor";
      document.getElementById("helperText").textContent = view === "library" ? "Choose a cover to open an album, or create a new one." : "Edit pages, photos, captions, stickers, and album style.";
      if (shouldRender) render();
    }

    function updatePageText() {
      const page = currentPage();
      page.title = pageTitle.value;
      page.date = pageDate.value;
      page.text = pageText.value;
      saveLibrary();
      renderPage();
      renderTabs();
    }

    function currentPage() {
      return album.pages[activePageIndex] ?? album.pages[0];
    }

    function addPage() {
      album.pages.push(blankPage());
      activePageIndex = album.pages.length - 1;
      selectedPhotoIndex = null;
      selectedStickerId = null;
      saveLibrary();
      render();
    }

    function deletePage() {
      if (album.pages.length === 1) {
        album.pages = [blankPage()];
      } else {
        album.pages.splice(activePageIndex, 1);
        activePageIndex = Math.max(0, activePageIndex - 1);
      }
      selectedPhotoIndex = null;
      selectedStickerId = null;
      saveLibrary();
      render();
    }

    function resetAlbum() {
      const confirmed = window.confirm("Delete this album from the library?");
      if (!confirmed) return;
      library.albums = library.albums.filter((item) => item.id !== album.id);
      if (!library.albums.length) library.albums.push(blankAlbum("family", "My Digital Album"));
      library.activeAlbumId = library.albums[0].id;
      album = activeAlbum();
      activePageIndex = 0;
      setView("library", false);
      saveLibrary();
      render();
    }

    function trimExtraPhotos() {
      album.pages.forEach((page) => {
        page.photos = page.photos.slice(0, album.photosPerPage);
      });
    }

    function render() {
      album = activeAlbum();
      activePageIndex = Math.min(activePageIndex, album.pages.length - 1);
      renderTemplateGrid();
      renderLibrary();
      renderEditor();
      renderCropPanel();
    }

    function renderTemplateGrid() {
      templateGrid.innerHTML = templates.map((template) => `
        <button class="template-card ${album.template === template.id ? "active" : ""}" type="button" data-template="${template.id}">
          ${coverMarkup({ ...album, title: template.name, coverColor: template.coverColor, template: template.id }, false)}
          <span>${template.name}</span>
        </button>
      `).join("");
      templateGrid.querySelectorAll("[data-template]").forEach((button) => {
        button.addEventListener("click", () => applyTemplate(button.dataset.template));
      });
    }

    function renderLibrary() {
      libraryGrid.innerHTML = library.albums.map((item) => `
        <button class="library-card" type="button" data-open-album="${item.id}">
          ${coverMarkup(item, true)}
          <span class="book-cover-meta">${item.pages.length} page${item.pages.length === 1 ? "" : "s"} · ${templateName(item.template)}</span>
        </button>
      `).join("");
      libraryGrid.querySelectorAll("[data-open-album]").forEach((button) => {
        button.addEventListener("click", () => {
          library.activeAlbumId = button.dataset.openAlbum;
          album = activeAlbum();
          activePageIndex = 0;
          selectedPhotoIndex = null;
          selectedStickerId = null;
          setView("editor", false);
          saveLibrary();
          render();
        });
      });
    }

    function coverMarkup(item, showTitle) {
      const template = templates.find((entry) => entry.id === item.template) ?? templates[0];
      return `
        <span class="book-cover" style="--book-cover:${item.coverColor}; --book-art:${template.art}">
          ${showTitle ? `<span class="book-cover-title">${escapeHtml(item.title)}</span>` : ""}
        </span>
      `;
    }

    function templateName(id) {
      return templates.find((template) => template.id === id)?.name ?? "Album";
    }

    function renderEditor() {
      albumEl.className = `album ${album.orientation} frame-${album.frameStyle}`;
      albumEl.style.setProperty("--paper", album.paperColor);
      albumEl.style.setProperty("--cover", album.coverColor);
      document.documentElement.style.setProperty("--paper", album.paperColor);
      document.documentElement.style.setProperty("--cover", album.coverColor);
      albumTitle.value = album.title;
      coverTitle.value = album.title;
      paperColor.value = album.paperColor;
      coverColor.value = album.coverColor;
      photosPerPage.value = String(album.photosPerPage);
      frameStyle.value = album.frameStyle;
      pagePattern.value = album.pagePattern;
      document.querySelectorAll("[data-orientation]").forEach((button) => {
        button.classList.toggle("active", button.dataset.orientation === album.orientation);
      });
      renderStickerTray();
      renderTabs();
      renderPageControls();
      renderPage();
    }

    function renderTabs() {
      pageTabs.innerHTML = album.pages.map((page, index) => `
        <button class="page-tab ${index === activePageIndex ? "active" : ""}" type="button" data-page="${index}">
          ${page.title ? escapeHtml(page.title) : `Page ${index + 1}`}
        </button>
      `).join("");
      pageTabs.querySelectorAll("[data-page]").forEach((button) => {
        button.addEventListener("click", () => {
          activePageIndex = Number(button.dataset.page);
          selectedPhotoIndex = null;
          selectedStickerId = null;
          render();
        });
      });
    }

    function renderPageControls() {
      const page = currentPage();
      pageTitle.value = page.title;
      pageDate.value = page.date;
      pageText.value = page.text;
    }

    function renderStickerTray() {
      stickerTray.innerHTML = stickers.map((sticker) => `
        <button class="sticker-button" type="button" data-sticker="${sticker.id}" title="Add ${sticker.label}">${sticker.art}</button>
      `).join("");
      stickerTray.querySelectorAll("[data-sticker]").forEach((button) => {
        button.addEventListener("click", () => addSticker(button.dataset.sticker));
      });
    }

    function renderPage() {
      const page = currentPage();
      const slots = Array.from({ length: album.photosPerPage }, (_, index) => page.photos[index] ?? null);
      albumPage.style.setProperty("--page-pattern", pagePatterns[album.pagePattern] ?? pagePatterns.plain);
      albumPage.innerHTML = `
        <div class="page-heading">
          <input class="page-title-inline" type="text" value="${escapeAttribute(page.title)}" placeholder="Page title" data-page-field="title">
          <input type="date" value="${escapeAttribute(page.date)}" data-page-field="date">
        </div>
        <div class="photo-grid slots-${album.photosPerPage}">
          ${slots.map((photo, index) => photoSlotMarkup(photo, index)).join("")}
        </div>
        <textarea class="page-note" placeholder="Write a little memory here..." data-page-field="text">${escapeHtml(page.text)}</textarea>
        ${page.stickers.map((sticker, index) => `
          <span class="page-sticker ${selectedStickerId === index ? "selected" : ""}" data-sticker-index="${index}" style="left:${sticker.x}%; top:${sticker.y}%; --tilt:${sticker.tilt}deg; --sticker-size:${sticker.size ?? 52}px">${stickerArt(sticker.id)}</span>
        `).join("")}
      `;

      albumPage.querySelectorAll("[data-page-field]").forEach((input) => {
        input.addEventListener("input", () => {
          const field = input.dataset.pageField;
          currentPage()[field] = input.value;
          saveLibrary();
          renderPageControls();
          renderTabs();
        });
      });

      albumPage.querySelectorAll("[data-upload]").forEach((input) => {
        input.addEventListener("change", () => handlePhotoUpload(input));
      });

      albumPage.querySelectorAll("[data-caption]").forEach((input) => {
        input.addEventListener("input", () => {
          const index = Number(input.dataset.caption);
          currentPage().photos[index].caption = input.value;
          saveLibrary();
        });
      });

      albumPage.querySelectorAll("[data-photo-slot]").forEach((slot) => {
        slot.addEventListener("click", (event) => {
          if (event.target.matches("input")) return;
          selectedPhotoIndex = Number(slot.dataset.photoSlot);
          selectedStickerId = null;
          render();
        });
        slot.addEventListener("dragstart", (event) => {
          event.dataTransfer.setData("text/plain", slot.dataset.photoSlot);
        });
        slot.addEventListener("dragover", (event) => event.preventDefault());
        slot.addEventListener("drop", (event) => {
          event.preventDefault();
          const to = Number(slot.dataset.photoSlot);
          const file = event.dataTransfer.files?.[0];
          if (file?.type?.startsWith("image/")) {
            readPhotoFile(file, to);
            return;
          }
          const from = Number(event.dataTransfer.getData("text/plain"));
          swapPhotos(from, to);
        });
      });

      albumPage.querySelectorAll("[data-remove-photo]").forEach((button) => {
        button.addEventListener("click", (event) => {
          event.stopPropagation();
          selectedPhotoIndex = Number(button.dataset.removePhoto);
          removeSelectedPhoto();
        });
      });

      albumPage.querySelectorAll("[data-sticker-index]").forEach((sticker) => {
        sticker.addEventListener("pointerdown", startStickerDrag);
        sticker.addEventListener("click", (event) => {
          event.stopPropagation();
          selectedStickerId = Number(sticker.dataset.stickerIndex);
          selectedPhotoIndex = null;
          renderCropPanel();
          renderPage();
        });
      });
      renderCropPanel();
    }

    function photoSlotMarkup(photo, index) {
      const selected = selectedPhotoIndex === index ? "selected" : "";
      const image = photo ? `
        <img
          src="${photo.src}"
          alt="${escapeAttribute(photo.caption || "Album photo")}"
          style="object-position:${photo.cropX ?? 50}% ${photo.cropY ?? 50}%; transform:scale(${photo.zoom ?? 1})"
        >
        <span class="photo-actions"><button class="mini-button" type="button" data-remove-photo="${index}">x</button></span>
      ` : `
        <span class="upload-prompt">
          <strong>Upload photo</strong>
          <span>Choose or drag here</span>
        </span>
      `;
      return `
        <div class="photo-slot ${selected}" data-photo-slot="${index}" draggable="${photo ? "true" : "false"}">
          <label class="photo-frame">
            ${image}
            <input class="hidden" type="file" accept="image/*" data-upload="${index}">
          </label>
          <input class="photo-caption" type="text" value="${escapeAttribute(photo?.caption ?? "")}" placeholder="Picture title or caption" data-caption="${index}" ${photo ? "" : "disabled"}>
        </div>
      `;
    }

    function handlePhotoUpload(input) {
      const file = input.files?.[0];
      if (!file) return;
      const index = Number(input.dataset.upload);
      readPhotoFile(file, index);
    }

    function readPhotoFile(file, index) {
      const reader = new FileReader();
      reader.onload = () => {
        const page = currentPage();
        page.photos[index] = {
          src: reader.result,
          caption: page.photos[index]?.caption ?? "",
          name: file.name,
          cropX: 50,
          cropY: 50,
          zoom: 1
        };
        selectedPhotoIndex = index;
        saveLibrary();
        renderPage();
      };
      reader.readAsDataURL(file);
    }

    function swapPhotos(from, to) {
      if (Number.isNaN(from) || Number.isNaN(to) || from === to) return;
      const photos = currentPage().photos;
      [photos[from], photos[to]] = [photos[to], photos[from]];
      selectedPhotoIndex = to;
      saveLibrary();
      renderPage();
    }

    function selectedPhoto() {
      return selectedPhotoIndex === null ? null : currentPage().photos[selectedPhotoIndex];
    }

    function updateSelectedPhotoCrop() {
      const photo = selectedPhoto();
      if (!photo) return;
      photo.zoom = Number(cropZoom.value);
      photo.cropX = Number(cropX.value);
      photo.cropY = Number(cropY.value);
      saveLibrary();
      renderPage();
    }

    function removeSelectedPhoto() {
      if (selectedPhotoIndex === null) return;
      currentPage().photos[selectedPhotoIndex] = null;
      selectedPhotoIndex = null;
      saveLibrary();
      renderPage();
    }

    function renderCropPanel() {
      const photo = selectedPhoto();
      const sticker = selectedSticker();
      cropPanel.style.opacity = photo ? "1" : "0.52";
      cropZoom.disabled = !photo;
      cropX.disabled = !photo;
      cropY.disabled = !photo;
      if (photo) {
        cropZoom.value = photo.zoom ?? 1;
        cropX.value = photo.cropX ?? 50;
        cropY.value = photo.cropY ?? 50;
      }
      stickerSize.disabled = !sticker;
      stickerSize.value = sticker?.size ?? 52;
    }

    function addSticker(value) {
      const page = currentPage();
      const count = page.stickers.length;
      page.stickers.push({
        id: value,
        x: 10 + ((count * 17) % 72),
        y: 12 + ((count * 23) % 68),
        tilt: [-10, 8, -4, 12][count % 4],
        size: 52
      });
      selectedStickerId = page.stickers.length - 1;
      selectedPhotoIndex = null;
      saveLibrary();
      renderPage();
    }

    function selectedSticker() {
      return selectedStickerId === null ? null : currentPage().stickers[selectedStickerId];
    }

    function startStickerDrag(event) {
      const index = Number(event.currentTarget.dataset.stickerIndex);
      selectedStickerId = index;
      selectedPhotoIndex = null;
      const rect = albumPage.getBoundingClientRect();
      draggingSticker = { index, rect };
      event.currentTarget.setPointerCapture(event.pointerId);
      event.currentTarget.addEventListener("pointermove", moveSticker);
      event.currentTarget.addEventListener("pointerup", endStickerDrag, { once: true });
    }

    function moveSticker(event) {
      if (!draggingSticker) return;
      const sticker = currentPage().stickers[draggingSticker.index];
      sticker.x = clamp(((event.clientX - draggingSticker.rect.left) / draggingSticker.rect.width) * 100, 0, 92);
      sticker.y = clamp(((event.clientY - draggingSticker.rect.top) / draggingSticker.rect.height) * 100, 0, 92);
      event.currentTarget.style.left = `${sticker.x}%`;
      event.currentTarget.style.top = `${sticker.y}%`;
    }

    function endStickerDrag(event) {
      event.currentTarget.removeEventListener("pointermove", moveSticker);
      draggingSticker = null;
      saveLibrary();
      renderPage();
    }

    function exportSingleHtml() {
      const html = `<!doctype html><html><head><meta charset="utf-8"><title>${escapeHtml(album.title)}</title><style>${document.querySelector("style").textContent}</style></head><body><main style="padding:24px">${exportAlbumMarkup()}</main></body></html>`;
      const blob = new Blob([html], { type: "text/html" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = `${slugify(album.title)}.html`;
      link.click();
      URL.revokeObjectURL(link.href);
    }

    function exportAlbumMarkup() {
      const savedIndex = activePageIndex;
      const markup = album.pages.map((page, index) => {
        activePageIndex = index;
        const slots = Array.from({ length: album.photosPerPage }, (_, slotIndex) => page.photos[slotIndex] ?? null);
        return `<section class="album ${album.orientation} frame-${album.frameStyle}" style="--paper:${album.paperColor}; --cover:${album.coverColor}; margin:0 auto 24px"><article class="album-page" style="--page-pattern:${pagePatterns[album.pagePattern] ?? pagePatterns.plain}">${staticPageMarkup(page, slots)}</article></section>`;
      }).join("");
      activePageIndex = savedIndex;
      return markup;
    }

    function staticPageMarkup(page, slots) {
      return `
        <div class="page-heading"><h2>${escapeHtml(page.title)}</h2><strong>${escapeHtml(page.date)}</strong></div>
        <div class="photo-grid slots-${album.photosPerPage}">
          ${slots.map((photo) => `<div class="photo-slot"><div class="photo-frame">${photo ? `<img src="${photo.src}" style="object-position:${photo.cropX ?? 50}% ${photo.cropY ?? 50}%; transform:scale(${photo.zoom ?? 1})">` : ""}</div><p>${escapeHtml(photo?.caption ?? "")}</p></div>`).join("")}
        </div>
        <p class="page-note">${escapeHtml(page.text)}</p>
        ${page.stickers.map((sticker) => `<span class="page-sticker" style="left:${sticker.x}%; top:${sticker.y}%; --tilt:${sticker.tilt}deg; --sticker-size:${sticker.size ?? 52}px">${stickerArt(sticker.id)}</span>`).join("")}
      `;
    }

    function passwordIsEnabled() {
      return Boolean(library.security?.pinHash);
    }

    function passwordIsUnlocked() {
      return !passwordIsEnabled() || sessionStorage.getItem(sessionKey) === "true";
    }

    async function hashPin(pin) {
      if (!window.crypto?.subtle) return `plain:${pin}`;
      const data = new TextEncoder().encode(`my-digital-album:${pin}`);
      const digest = await crypto.subtle.digest("SHA-256", data);
      return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
    }

    function openPasswordSettings() {
      openPinModal(passwordIsEnabled() ? "manage" : "setup");
    }

    function openPinModal(mode, message = "") {
      pinMode = mode;
      pinBuffer = "";
      pinMessage = message;
      if (mode !== "confirm_setup") pendingPin = "";
      pinOverlay.classList.add("visible");
      renderPinModal();
    }

    function closePinModal() {
      if (pinMode === "unlock" && !passwordIsUnlocked()) return;
      pinOverlay.classList.remove("visible");
    }

    function renderPinModal() {
      const manage = pinMode === "manage";
      const locked = pinMode === "unlock";
      const title = { unlock: "Enter Password", setup: "Choose Password", confirm_setup: "Confirm Password", manage: "Password" }[pinMode];
      pinOverlay.innerHTML = `
        <section class="pin-card">
          <h2>${title}</h2>
          <p>${manage ? "A 4 digit code is active." : "Use the number pad to enter a 4 digit code."}</p>
          ${locked ? "" : `<button class="secondary" id="pinClose" type="button">Close</button>`}
          ${manage ? `<div class="row"><button class="primary" data-pin-action="change" type="button">Change</button><button class="danger" data-pin-action="disable" type="button">Disable</button></div>` : pinPadMarkup()}
          <p class="pin-message">${pinMessage}</p>
        </section>
      `;
      document.getElementById("pinClose")?.addEventListener("click", closePinModal);
      pinOverlay.querySelectorAll("[data-pin-key]").forEach((button) => button.addEventListener("click", () => handlePinKey(button.dataset.pinKey)));
      pinOverlay.querySelectorAll("[data-pin-action]").forEach((button) => button.addEventListener("click", () => handlePinAction(button.dataset.pinAction)));
    }

    function pinPadMarkup() {
      return `
        <div class="pin-dots">${[0,1,2,3].map((index) => `<span class="pin-dot ${index < pinBuffer.length ? "filled" : ""}"></span>`).join("")}</div>
        <div class="pin-pad">
          ${["1","2","3","4","5","6","7","8","9","back","0","clear"].map((key) => `<button class="pin-key" data-pin-key="${key}" type="button">${key === "back" ? "⌫" : key === "clear" ? "Clear" : key}</button>`).join("")}
        </div>
      `;
    }

    async function handlePinKey(key) {
      if (key === "clear") pinBuffer = "";
      else if (key === "back") pinBuffer = pinBuffer.slice(0, -1);
      else if (pinBuffer.length < 4) pinBuffer += key;
      pinMessage = "";
      if (pinBuffer.length === 4) await submitPin(pinBuffer);
      else renderPinModal();
    }

    async function submitPin(pin) {
      if (pinMode === "unlock") {
        if (await hashPin(pin) === library.security.pinHash) {
          sessionStorage.setItem(sessionKey, "true");
          closePinModal();
        } else {
          openPinModal("unlock", "Wrong code. Try again.");
        }
        return;
      }
      if (pinMode === "setup") {
        pendingPin = pin;
        openPinModal("confirm_setup");
        return;
      }
      if (pinMode === "confirm_setup") {
        if (pin !== pendingPin) {
          openPinModal("setup", "Codes did not match. Start again.");
          return;
        }
        library.security = { pinHash: await hashPin(pin) };
        sessionStorage.setItem(sessionKey, "true");
        saveLibrary();
        closePinModal();
      }
    }

    function handlePinAction(action) {
      if (action === "change") openPinModal("setup");
      if (action === "disable") {
        library.security = { pinHash: "" };
        sessionStorage.removeItem(sessionKey);
        saveLibrary();
        closePinModal();
      }
    }

    function initPasswordGate() {
      if (passwordIsEnabled() && !passwordIsUnlocked()) openPinModal("unlock");
    }

    function clamp(value, min, max) {
      return Math.min(max, Math.max(min, value));
    }

    function slugify(value) {
      return String(value || "album").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "album";
    }

    function stickerArt(id) {
      return stickers.find((sticker) => sticker.id === id)?.art ?? "";
    }

    function escapeHtml(value) {
      return String(value ?? "").replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
      })[char]);
    }

    function escapeAttribute(value) {
      return escapeHtml(value).replace(/`/g, "&#096;");
    }

    setView("library", false);
    saveLibrary();
    render();
    initPasswordGate();

  </script>
</body>
</html>
"""


class AlbumHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/", "/index.html"):
            self.send_error(404)
            return
        body = APP_HTML.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8790
    url = f"http://{host}:{port}"
    try:
        server = ThreadedHTTPServer((host, port), AlbumHandler)
    except SocketError:
        print(f"My Digital Album appears to already be running at {url}")
        webbrowser.open(url)
        raise SystemExit(0)
    print(f"My Digital Album running at {url}")
    webbrowser.open(url)
    server.serve_forever()
