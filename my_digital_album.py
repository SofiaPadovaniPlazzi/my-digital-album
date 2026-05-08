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
      padding: 18px;
      box-shadow: var(--shadow);
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
      box-shadow: inset 0 0 0 1px rgba(69, 49, 32, 0.12);
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
      width: 52px;
      height: 52px;
      transform: rotate(var(--tilt));
      text-shadow: 0 4px 10px rgba(70, 45, 26, 0.12);
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

    .suggestions {
      display: grid;
      gap: 9px;
      margin: 0;
      padding-left: 18px;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.42;
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
      aside, .toolbar, .page-tabs, .cover-title button {
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
        <button class="primary" id="createAlbum" type="button">Create album</button>
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
        <div class="row">
          <button class="secondary" id="addPage" type="button">Add page</button>
          <button class="danger" id="deletePage" type="button">Delete page</button>
        </div>
      </section>

      <section class="panel">
        <h2>Suggestions</h2>
        <ul class="suggestions">
          <li>Create one album per trip, season, friendship, or year.</li>
          <li>Use one page title for a little chapter, then captions for each photo.</li>
          <li>Try 1 photo pages for special memories and 4 photo pages for busy days.</li>
          <li>Use the cover color like the outside cover of a real album.</li>
          <li>Print to PDF when you want to save or share a finished version.</li>
        </ul>
      </section>
    </aside>

    <main>
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
    </main>
  </div>

  <script>
    const storageKey = "my-digital-album-v1";
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
    const defaultAlbum = {
      title: "My Digital Album",
      orientation: "vertical",
      paperColor: "#fff8ec",
      coverColor: "#d9a6a6",
      photosPerPage: 2,
      frameStyle: "simple",
      pages: [blankPage()]
    };

    let album = loadAlbum();
    let activePageIndex = 0;

    const albumEl = document.getElementById("album");
    const albumPage = document.getElementById("albumPage");
    const pageTabs = document.getElementById("pageTabs");
    const stickerTray = document.getElementById("stickerTray");
    const albumTitle = document.getElementById("albumTitle");
    const coverTitle = document.getElementById("coverTitle");
    const paperColor = document.getElementById("paperColor");
    const coverColor = document.getElementById("coverColor");
    const photosPerPage = document.getElementById("photosPerPage");
    const frameStyle = document.getElementById("frameStyle");
    const pageTitle = document.getElementById("pageTitle");
    const pageDate = document.getElementById("pageDate");
    const pageText = document.getElementById("pageText");

    document.getElementById("createAlbum").addEventListener("click", createAlbumFromOptions);
    document.getElementById("addPage").addEventListener("click", addPage);
    document.getElementById("deletePage").addEventListener("click", deletePage);
    document.getElementById("saveButton").addEventListener("click", saveAlbum);
    document.getElementById("exportButton").addEventListener("click", () => window.print());
    document.getElementById("resetButton").addEventListener("click", resetAlbum);

    coverTitle.addEventListener("input", () => {
      album.title = coverTitle.value || "My Digital Album";
      albumTitle.value = album.title;
      saveAlbum();
      renderTabs();
    });

    [albumTitle, paperColor, coverColor, photosPerPage, frameStyle].forEach((input) => {
      input.addEventListener("input", updateAlbumOptions);
      input.addEventListener("change", updateAlbumOptions);
    });

    [pageTitle, pageDate, pageText].forEach((input) => {
      input.addEventListener("input", updatePageText);
    });

    document.querySelectorAll("[data-orientation]").forEach((button) => {
      button.addEventListener("click", () => {
        album.orientation = button.dataset.orientation;
        saveAlbum();
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

    function loadAlbum() {
      const stored = localStorage.getItem(storageKey);
      if (!stored) return structuredClone(defaultAlbum);
      try {
        const saved = JSON.parse(stored);
        return {
          ...defaultAlbum,
          ...saved,
          pages: saved.pages?.length ? saved.pages.map((page) => ({
            ...blankPage(),
            ...page,
            photos: page.photos ?? [],
            stickers: page.stickers ?? []
          })) : [blankPage()]
        };
      } catch {
        return structuredClone(defaultAlbum);
      }
    }

    function saveAlbum() {
      localStorage.setItem(storageKey, JSON.stringify(album));
    }

    function createAlbumFromOptions() {
      const confirmed = album.pages.some((page) => page.photos.length || page.title || page.text)
        ? window.confirm("Create a new album and replace the current one?")
        : true;
      if (!confirmed) return;
      album = {
        title: albumTitle.value || "My Digital Album",
        orientation: album.orientation,
        paperColor: paperColor.value,
        coverColor: coverColor.value,
        photosPerPage: Number(photosPerPage.value),
        frameStyle: frameStyle.value,
        pages: [blankPage()]
      };
      activePageIndex = 0;
      saveAlbum();
      render();
    }

    function updateAlbumOptions() {
      album.title = albumTitle.value || "My Digital Album";
      album.paperColor = paperColor.value;
      album.coverColor = coverColor.value;
      album.photosPerPage = Number(photosPerPage.value);
      album.frameStyle = frameStyle.value;
      coverTitle.value = album.title;
      trimExtraPhotos();
      saveAlbum();
      render();
    }

    function updatePageText() {
      const page = currentPage();
      page.title = pageTitle.value;
      page.date = pageDate.value;
      page.text = pageText.value;
      saveAlbum();
      renderPage();
      renderTabs();
    }

    function currentPage() {
      return album.pages[activePageIndex] ?? album.pages[0];
    }

    function addPage() {
      album.pages.push(blankPage());
      activePageIndex = album.pages.length - 1;
      saveAlbum();
      render();
    }

    function deletePage() {
      if (album.pages.length === 1) {
        album.pages = [blankPage()];
      } else {
        album.pages.splice(activePageIndex, 1);
        activePageIndex = Math.max(0, activePageIndex - 1);
      }
      saveAlbum();
      render();
    }

    function resetAlbum() {
      const confirmed = window.confirm("Reset the whole album? This removes uploaded photos, text, dates, and stickers.");
      if (!confirmed) return;
      localStorage.removeItem(storageKey);
      album = structuredClone(defaultAlbum);
      activePageIndex = 0;
      render();
    }

    function trimExtraPhotos() {
      album.pages.forEach((page) => {
        page.photos = page.photos.slice(0, album.photosPerPage);
      });
    }

    function render() {
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
      albumPage.innerHTML = `
        <div class="page-heading">
          <input class="page-title-inline" type="text" value="${escapeAttribute(page.title)}" placeholder="Page title" data-page-field="title">
          <input type="date" value="${escapeAttribute(page.date)}" data-page-field="date">
        </div>
        <div class="photo-grid slots-${album.photosPerPage}">
          ${slots.map((photo, index) => photoSlotMarkup(photo, index)).join("")}
        </div>
        <textarea class="page-note" placeholder="Write a little memory here..." data-page-field="text">${escapeHtml(page.text)}</textarea>
        ${page.stickers.map((sticker) => `
          <span class="page-sticker" style="left:${sticker.x}%; top:${sticker.y}%; --tilt:${sticker.tilt}deg">${stickerArt(sticker.id)}</span>
        `).join("")}
      `;

      albumPage.querySelectorAll("[data-page-field]").forEach((input) => {
        input.addEventListener("input", () => {
          const field = input.dataset.pageField;
          currentPage()[field] = input.value;
          saveAlbum();
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
          saveAlbum();
        });
      });
    }

    function photoSlotMarkup(photo, index) {
      return `
        <div class="photo-slot">
          <label class="photo-frame">
            ${photo ? `<img src="${photo.src}" alt="${escapeAttribute(photo.caption || "Album photo")}">` : `
              <span class="upload-prompt">
                <strong>Upload photo</strong>
                <span>Choose from your device</span>
              </span>
            `}
            <input class="hidden" type="file" accept="image/*" data-upload="${index}">
          </label>
          <input class="photo-caption" type="text" value="${escapeAttribute(photo?.caption ?? "")}" placeholder="Picture title or caption" data-caption="${index}">
        </div>
      `;
    }

    function handlePhotoUpload(input) {
      const file = input.files?.[0];
      if (!file) return;
      const index = Number(input.dataset.upload);
      const reader = new FileReader();
      reader.onload = () => {
        const page = currentPage();
        page.photos[index] = {
          src: reader.result,
          caption: page.photos[index]?.caption ?? "",
          name: file.name
        };
        saveAlbum();
        renderPage();
      };
      reader.readAsDataURL(file);
    }

    function addSticker(value) {
      const page = currentPage();
      const count = page.stickers.length;
      page.stickers.push({
        id: value,
        x: 10 + ((count * 17) % 72),
        y: 12 + ((count * 23) % 68),
        tilt: [-10, 8, -4, 12][count % 4]
      });
      saveAlbum();
      renderPage();
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

    render();
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
