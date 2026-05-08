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

    .app.library-mode {
      grid-template-columns: 1fr;
    }

    .app.setup-mode {
      grid-template-columns: 340px minmax(0, 1fr);
    }

    .app.library-mode aside {
      display: none;
    }

    .app.setup-mode aside .editor-panel,
    .app.library-mode aside .editor-panel {
      display: none;
    }

    .app.editor-mode aside .setup-only {
      display: none;
    }

    .app.editor-mode.setup-hidden {
      grid-template-columns: 1fr;
    }

    .app.editor-mode.setup-hidden aside {
      display: none;
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

    .floating-setup-toggle {
      position: fixed;
      left: 18px;
      bottom: 18px;
      z-index: 20;
      min-height: 40px;
      padding: 0 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--field);
      color: var(--ink);
      box-shadow: var(--shadow);
      font-weight: 900;
      display: none;
    }

    .app.editor-mode.setup-hidden .floating-setup-toggle {
      display: block;
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

    .home-head {
      width: min(980px, 100%);
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 16px;
      align-items: end;
      margin-bottom: 22px;
    }

    .home-head h1 {
      font-size: 42px;
      line-height: 1;
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

    .new-album-card {
      place-items: center;
      text-align: center;
      border-style: dashed;
    }

    .plus-mark {
      display: grid;
      place-items: center;
      width: 82px;
      height: 82px;
      border-radius: 50%;
      background: var(--accent);
      color: var(--accent-ink);
      font-size: 46px;
      line-height: 1;
      font-weight: 500;
      box-shadow: var(--shadow);
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

    .book-cover.large {
      width: min(300px, 72vw);
      height: 410px;
      min-height: 0;
      transform: perspective(900px) rotateY(-14deg);
      transform-origin: left center;
      box-shadow:
        inset 18px 0 24px rgba(64, 35, 22, 0.18),
        18px 20px 36px rgba(64, 35, 22, 0.18);
    }

    .book-cover.large::after {
      left: 28px;
      width: 2px;
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
      max-height: 360px;
      overflow: auto;
      padding-right: 4px;
    }

    .pattern-group-title {
      grid-column: 1 / -1;
      margin-top: 6px;
      color: var(--muted);
      font-size: 11px;
      font-weight: 900;
      text-transform: uppercase;
      letter-spacing: 0.04em;
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

    .setup-preview {
      display: grid;
      grid-template-columns: minmax(260px, 360px) minmax(260px, 420px);
      gap: 34px;
      align-items: center;
      width: min(920px, 100%);
      padding: 26px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.54);
      box-shadow: var(--shadow);
    }

    .setup-copy {
      display: grid;
      gap: 12px;
    }

    .setup-copy h1 {
      font-size: 38px;
      line-height: 1;
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

    .album.opening {
      animation: bookOpen 700ms ease both;
    }

    @keyframes bookOpen {
      0% {
        transform: perspective(1200px) rotateY(-22deg) scale(0.92);
        opacity: 0.15;
      }
      100% {
        transform: perspective(1200px) rotateY(0deg) scale(1);
        opacity: 1;
      }
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
      background: color-mix(in srgb, var(--cover) 18%, var(--paper));
      padding: 18px;
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

    .book-spread {
      position: relative;
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      gap: 0;
      min-height: calc(var(--page-height) - 36px);
      perspective: 1200px;
    }

    .book-spread::before {
      content: "";
      position: absolute;
      top: 0;
      bottom: 0;
      left: calc(50% - 8px);
      z-index: 3;
      width: 16px;
      background:
        linear-gradient(90deg, rgba(64, 42, 28, 0.16), rgba(255, 255, 255, 0.48), rgba(64, 42, 28, 0.18));
      box-shadow: 0 0 20px rgba(64, 42, 28, 0.14);
      pointer-events: none;
    }

    .book-page {
      position: relative;
      min-width: 0;
      padding: 22px;
      background: var(--paper);
      overflow: hidden;
      box-shadow: inset 0 0 0 1px rgba(69, 49, 32, 0.1);
    }

    .book-page::before {
      content: "";
      position: absolute;
      inset: 0;
      background: var(--page-pattern);
      opacity: 0.9;
      pointer-events: none;
    }

    .book-page > * {
      position: relative;
      z-index: 1;
    }

    .book-page.left {
      border-radius: 8px 0 0 8px;
      transform-origin: right center;
    }

    .book-page.right {
      border-radius: 0 8px 8px 0;
      box-shadow:
        inset 16px 0 24px rgba(66, 42, 24, 0.08),
        inset 0 0 0 1px rgba(69, 49, 32, 0.1);
    }

    .book-page.empty-page {
      display: grid;
      place-items: center;
      color: var(--muted);
      text-align: center;
      font-weight: 800;
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
      min-height: 320px;
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

      .setup-preview,
      .home-head,
      .book-spread {
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
  <div class="app" id="app">
    <aside>
      <div class="brand">
        <h1>My Digital Album</h1>
        <p>Build a sweet photo album from your own pictures, with paper choices, frames, dates, captions, notes, and stickers.</p>
      </div>

      <section class="panel setup-panel">
        <div class="toolbar">
          <h2>Album Setup</h2>
          <button class="secondary" id="hideSetupButton" type="button">Hide</button>
        </div>
        <div class="field">
          <label for="albumTitle">Album title</label>
          <input id="albumTitle" type="text" placeholder="Summer in Italy">
        </div>
        <div class="field">
          <label>Cover pattern</label>
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
          <label for="patternColor">Pattern color</label>
          <input id="patternColor" type="color" value="#fff4df">
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
        <div class="row setup-only">
          <button class="primary" id="createAlbum" type="button">Open album</button>
          <button class="secondary" id="duplicateAlbum" type="button">Duplicate</button>
        </div>
      </section>

      <section class="panel editor-panel">
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

      <section class="panel editor-panel" id="cropPanel">
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

      <section class="panel editor-panel">
        <h2>Privacy</h2>
        <div class="row">
          <button class="secondary" id="passwordButton" type="button">Password</button>
          <button class="secondary" id="exportHtmlButton" type="button">Export HTML</button>
        </div>
      </section>
    </aside>

    <main>
      <div class="top-tabs">
        <button class="top-tab active" id="libraryTab" type="button">Home</button>
        <button class="top-tab" id="setupTab" type="button">Setup</button>
        <button class="top-tab" id="editorTab" type="button">Album</button>
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
          <div class="home-head">
            <div>
              <h1>My Digital Album</h1>
              <p>Choose an album from your library or create a new book from scratch.</p>
            </div>
          </div>
          <div class="library-grid" id="libraryGrid"></div>
        </div>
      </div>

      <div class="view" id="setupView">
        <div class="album-stage">
          <section class="setup-preview">
            <div id="setupBookPreview"></div>
            <div class="setup-copy">
              <h1>Design your album</h1>
              <p>Choose the cover, paper, orientation, page pattern, frames, and how many photos each page can hold. Then open the album like a book.</p>
              <button class="primary" id="openAlbumButton" type="button">Open album</button>
              <button class="secondary" id="backHomeButton" type="button">Back to home</button>
            </div>
          </section>
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
    <button class="floating-setup-toggle" id="showSetupButton" type="button">Show setup</button>
  </div>

  <div class="pin-overlay" id="pinOverlay" aria-modal="true" role="dialog"></div>

  <script>
    const legacyStorageKey = "my-digital-album-v1";
    const storageKey = "my-digital-album-library-v2";
    const sessionKey = "my-digital-album-unlocked";
    const coverPatterns = [
      {
        id: "cloth",
        name: "Book cloth",
        group: "Real book textures",
        coverColor: "#8e6f5d",
        patternColor: "#f7eee2",
        paperColor: "#fff8ec",
        pagePattern: "plain",
        art: "repeating-linear-gradient(0deg, color-mix(in srgb, var(--pattern-color) 32%, transparent) 0 1px, transparent 1px 5px), repeating-linear-gradient(90deg, color-mix(in srgb, var(--pattern-color) 24%, transparent) 0 1px, transparent 1px 6px)"
      },
      {
        id: "leather",
        name: "Soft leather",
        group: "Real book textures",
        coverColor: "#7a4737",
        patternColor: "#f3c79a",
        paperColor: "#fff7e6",
        pagePattern: "plain",
        art: "radial-gradient(circle at 20% 24%, color-mix(in srgb, var(--pattern-color) 20%, transparent) 0 2px, transparent 3px), radial-gradient(circle at 72% 62%, color-mix(in srgb, var(--pattern-color) 16%, transparent) 0 3px, transparent 4px), repeating-linear-gradient(35deg, transparent 0 12px, color-mix(in srgb, var(--pattern-color) 12%, transparent) 13px 15px)"
      },
      {
        id: "linen",
        name: "Fine linen",
        group: "Real book textures",
        coverColor: "#b9a58e",
        patternColor: "#fff8ec",
        paperColor: "#fffaf3",
        pagePattern: "pressed",
        art: "repeating-linear-gradient(0deg, color-mix(in srgb, var(--pattern-color) 34%, transparent) 0 1px, transparent 1px 3px), repeating-linear-gradient(90deg, color-mix(in srgb, var(--pattern-color) 28%, transparent) 0 1px, transparent 1px 4px)"
      },
      {
        id: "pinstripes",
        name: "Pinstripes",
        group: "Simple patterns",
        coverColor: "#6fa8b5",
        patternColor: "#fff7e6",
        paperColor: "#fff7e6",
        pagePattern: "grid",
        art: "repeating-linear-gradient(90deg, transparent 0 13px, var(--pattern-color) 14px 15px)"
      },
      {
        id: "dots",
        name: "Pois",
        group: "Simple patterns",
        coverColor: "#d79ca8",
        patternColor: "#fff4df",
        paperColor: "#fff6f2",
        pagePattern: "dots",
        art: "radial-gradient(circle, var(--pattern-color) 0 4px, transparent 5px) 0 0 / 28px 28px"
      },
      {
        id: "gingham",
        name: "Gingham",
        group: "Simple patterns",
        coverColor: "#91b99b",
        patternColor: "#fffaf0",
        paperColor: "#fbf7ef",
        pagePattern: "grid",
        art: "repeating-linear-gradient(0deg, color-mix(in srgb, var(--pattern-color) 38%, transparent) 0 12px, transparent 12px 24px), repeating-linear-gradient(90deg, color-mix(in srgb, var(--pattern-color) 38%, transparent) 0 12px, transparent 12px 24px)"
      },
      {
        id: "diagonal",
        name: "Diagonal lines",
        group: "Simple patterns",
        coverColor: "#c49ab8",
        patternColor: "#fff5d6",
        paperColor: "#fff8ec",
        pagePattern: "plain",
        art: "repeating-linear-gradient(135deg, transparent 0 12px, var(--pattern-color) 13px 15px, transparent 16px 26px)"
      },
      {
        id: "waves",
        name: "Soft waves",
        group: "Simple patterns",
        coverColor: "#7897c0",
        patternColor: "#e9f6ff",
        paperColor: "#fffaf3",
        pagePattern: "dots",
        art: "radial-gradient(ellipse at 50% 100%, transparent 0 16px, var(--pattern-color) 17px 19px, transparent 20px) 0 0 / 42px 24px"
      },
      {
        id: "sea",
        name: "Sea horizon",
        group: "Scenarios",
        coverColor: "#5f9aaa",
        patternColor: "#fff1b8",
        paperColor: "#fff7e6",
        pagePattern: "pressed",
        svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 320"><rect width="240" height="320" fill="none"/><circle cx="184" cy="58" r="23" fill="PATTERN" opacity=".92"/><path d="M0 190c32-17 64-17 96 0s64 17 96 0 48-17 48-17v147H0Z" fill="PATTERN" opacity=".28"/><path d="M0 220c34-13 68-13 102 0s68 13 102 0 36-12 36-12" fill="none" stroke="PATTERN" stroke-width="8" opacity=".7"/><path d="M109 159v58" stroke="PATTERN" stroke-width="5" stroke-linecap="round"/><path d="M113 164 165 207h-52Z" fill="PATTERN" opacity=".72"/><path d="M105 175 72 210h33Z" fill="PATTERN" opacity=".54"/><path d="M67 219h111l-16 15H83Z" fill="PATTERN" opacity=".82"/></svg>`
      },
      {
        id: "mountains",
        name: "Mountains",
        group: "Scenarios",
        coverColor: "#6f7f68",
        patternColor: "#f5ead6",
        paperColor: "#fbf7ef",
        pagePattern: "grid",
        svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 320"><rect width="240" height="320" fill="none"/><circle cx="54" cy="58" r="17" fill="PATTERN" opacity=".72"/><path d="M0 236 54 142l34 50 38-70 76 114Z" fill="PATTERN" opacity=".44"/><path d="M60 154 88 192l14-25 24-45 76 114H93Z" fill="PATTERN" opacity=".66"/><path d="M0 252h240v68H0Z" fill="PATTERN" opacity=".22"/><path d="M126 122 108 157l23-12 19 17Z" fill="PATTERN" opacity=".95"/></svg>`
      },
      {
        id: "sunset",
        name: "Sunset",
        group: "Scenarios",
        coverColor: "#c98265",
        patternColor: "#ffe2a1",
        paperColor: "#fff6f2",
        pagePattern: "plain",
        svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 320"><rect width="240" height="320" fill="none"/><circle cx="120" cy="132" r="47" fill="PATTERN" opacity=".9"/><path d="M0 166h240" stroke="PATTERN" stroke-width="8" opacity=".75"/><path d="M36 196h168M18 224h204M52 252h136" stroke="PATTERN" stroke-width="8" stroke-linecap="round" opacity=".45"/><path d="M0 269c42-13 78-13 120 0s78 13 120 0v51H0Z" fill="PATTERN" opacity=".28"/></svg>`
      },
      {
        id: "city",
        name: "City night",
        group: "Scenarios",
        coverColor: "#52627e",
        patternColor: "#f7d778",
        paperColor: "#fbf7ef",
        pagePattern: "grid",
        svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 320"><rect width="240" height="320" fill="none"/><path d="M0 166h28v-38h35v69h27v-92h47v57h29v-42h38v76h36v124H0Z" fill="PATTERN" opacity=".48"/><g fill="PATTERN" opacity=".95"><rect x="39" y="146" width="7" height="10"/><rect x="52" y="146" width="7" height="10"/><rect x="103" y="126" width="8" height="11"/><rect x="120" y="126" width="8" height="11"/><rect x="177" y="140" width="7" height="10"/><rect x="190" y="140" width="7" height="10"/><circle cx="38" cy="66" r="2"/><circle cx="75" cy="42" r="2"/><circle cx="169" cy="70" r="2"/><circle cx="203" cy="48" r="2"/></g></svg>`
      },
      {
        id: "forest",
        name: "Trees",
        group: "Silhouettes",
        coverColor: "#557461",
        patternColor: "#e8f0cf",
        paperColor: "#fffaf3",
        pagePattern: "pressed",
        svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 320"><rect width="240" height="320" fill="none"/><g fill="PATTERN" opacity=".72"><path d="M24 232 50 172l26 60H57v55H43v-55Z"/><path d="M92 244 124 154l32 90h-24v58h-16v-58Z"/><path d="M160 235 190 166l30 69h-22v57h-15v-57Z"/></g><path d="M0 276h240v44H0Z" fill="PATTERN" opacity=".25"/></svg>`
      },
      {
        id: "birds",
        name: "Birds",
        group: "Silhouettes",
        coverColor: "#8fa7c6",
        patternColor: "#fff8e5",
        paperColor: "#fff7e6",
        pagePattern: "dots",
        svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 320"><rect width="240" height="320" fill="none"/><g fill="none" stroke="PATTERN" stroke-width="7" stroke-linecap="round" opacity=".82"><path d="M42 96c18-18 34-18 52 0 18-18 34-18 52 0"/><path d="M26 184c14-14 28-14 42 0 14-14 28-14 42 0"/><path d="M126 154c16-16 31-16 47 0 16-16 31-16 47 0"/><path d="M88 246c13-13 26-13 39 0 13-13 26-13 39 0"/></g></svg>`
      },
      {
        id: "cats",
        name: "Cats",
        group: "Silhouettes",
        coverColor: "#a67878",
        patternColor: "#fff1dc",
        paperColor: "#fff8ec",
        pagePattern: "hearts",
        svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 320"><rect width="240" height="320" fill="none"/><g fill="PATTERN" opacity=".72"><path d="M57 211c0-31 18-50 44-50s44 19 44 50v33H57Z"/><path d="M66 170 75 130l25 30 25-30 10 40Z"/><circle cx="101" cy="210" r="48"/><path d="M143 226c24 0 39-13 44-34 6 26-8 58-44 58Z"/><path d="M150 112c0-20 12-33 30-33s30 13 30 33v22h-60Z" opacity=".58"/><path d="M156 86 164 61l16 20 17-20 7 25Z" opacity=".58"/></g></svg>`
      },
      {
        id: "butterflies",
        name: "Butterflies",
        group: "Silhouettes",
        coverColor: "#b48ac2",
        patternColor: "#fff0bd",
        paperColor: "#fff6f2",
        pagePattern: "pressed",
        svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 320"><rect width="240" height="320" fill="none"/><g fill="PATTERN" opacity=".75"><path d="M78 96c-31-34-68-15-50 25 15 32 42 26 52 4 10 22 37 28 52-4 18-40-19-59-50-25Z"/><rect x="76" y="91" width="8" height="54" rx="4"/><path d="M160 215c-26-29-58-13-43 21 13 27 36 22 45 3 9 19 32 24 45-3 15-34-17-50-43-21Z" opacity=".68"/><rect x="158" y="211" width="7" height="45" rx="4" opacity=".68"/></g></svg>`
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
    let draftAlbum = null;
    let setupHidden = localStorage.getItem(`${storageKey}-setup-hidden`) === "true";
    let activePageIndex = 0;
    let selectedPhotoIndex = null;
    let selectedStickerId = null;
    let draggingSticker = null;
    let pinMode = "unlock";
    let pinBuffer = "";
    let pinMessage = "";
    let pendingPin = "";

    const app = document.getElementById("app");
    const albumEl = document.getElementById("album");
    const albumPage = document.getElementById("albumPage");
    const pageTabs = document.getElementById("pageTabs");
    const libraryGrid = document.getElementById("libraryGrid");
    const setupBookPreview = document.getElementById("setupBookPreview");
    const templateGrid = document.getElementById("templateGrid");
    const stickerTray = document.getElementById("stickerTray");
    const albumTitle = document.getElementById("albumTitle");
    const coverTitle = document.getElementById("coverTitle");
    const paperColor = document.getElementById("paperColor");
    const coverColor = document.getElementById("coverColor");
    const patternColor = document.getElementById("patternColor");
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
    const setupTab = document.getElementById("setupTab");
    const editorTab = document.getElementById("editorTab");
    const libraryView = document.getElementById("libraryView");
    const setupView = document.getElementById("setupView");
    const editorView = document.getElementById("editorView");
    const pinOverlay = document.getElementById("pinOverlay");

    document.getElementById("createAlbum").addEventListener("click", openAlbumFromSetup);
    document.getElementById("openAlbumButton").addEventListener("click", openAlbumFromSetup);
    document.getElementById("backHomeButton").addEventListener("click", () => setView("library"));
    document.getElementById("duplicateAlbum").addEventListener("click", duplicateAlbum);
    document.getElementById("addPage").addEventListener("click", addPage);
    document.getElementById("deletePage").addEventListener("click", deletePage);
    document.getElementById("saveButton").addEventListener("click", saveLibrary);
    document.getElementById("exportButton").addEventListener("click", () => window.print());
    document.getElementById("exportHtmlButton").addEventListener("click", exportSingleHtml);
    document.getElementById("resetButton").addEventListener("click", resetAlbum);
    document.getElementById("passwordButton").addEventListener("click", openPasswordSettings);
    document.getElementById("removePhoto").addEventListener("click", removeSelectedPhoto);
    document.getElementById("hideSetupButton").addEventListener("click", () => setSetupHidden(true));
    document.getElementById("showSetupButton").addEventListener("click", () => setSetupHidden(false));
    libraryTab.addEventListener("click", () => setView("library"));
    setupTab.addEventListener("click", () => startNewAlbum());
    editorTab.addEventListener("click", () => draftAlbum ? openAlbumFromSetup() : setView("editor"));

    coverTitle.addEventListener("input", () => {
      album.title = coverTitle.value || "My Digital Album";
      albumTitle.value = album.title;
      saveLibrary();
      renderLibrary();
      renderTabs();
    });

    [albumTitle, paperColor, coverColor, patternColor, photosPerPage, frameStyle, pagePattern].forEach((input) => {
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

    function normalizeCoverPatternId(value) {
      const legacy = {
        travel: "sea",
        family: "dots",
        birthday: "sunset",
        graduation: "city",
        wedding: "linen"
      };
      const id = legacy[value] ?? value ?? "cloth";
      return coverPatterns.some((pattern) => pattern.id === id) ? id : "cloth";
    }

    function blankAlbum(patternId = "cloth", title = "") {
      patternId = normalizeCoverPatternId(patternId);
      const pattern = coverPatterns.find((item) => item.id === patternId) ?? coverPatterns[0];
      return {
        id: crypto.randomUUID(),
        title: title || `${pattern.name} Album`,
        coverPattern: pattern.id,
        orientation: "vertical",
        paperColor: pattern.paperColor,
        coverColor: pattern.coverColor,
        patternColor: pattern.patternColor,
        photosPerPage: 2,
        frameStyle: "simple",
        pagePattern: pattern.pagePattern,
        pages: [blankPage()]
      };
    }

    function normalizeAlbum(saved) {
      const coverPattern = normalizeCoverPatternId(saved?.coverPattern ?? saved?.template ?? "cloth");
      const fallback = blankAlbum(coverPattern, saved?.title);
      return {
        ...fallback,
        ...saved,
        id: saved?.id ?? crypto.randomUUID(),
        coverPattern,
        patternColor: saved?.patternColor ?? fallback.patternColor,
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

      const first = blankAlbum("cloth", "My Digital Album");
      return { ...defaultLibrary, activeAlbumId: first.id, albums: [first] };
    }

    function activeAlbum() {
      return library.albums.find((item) => item.id === library.activeAlbumId) ?? library.albums[0];
    }

    function saveLibrary() {
      localStorage.setItem(storageKey, JSON.stringify(library));
    }

    function startNewAlbum(patternId = "cloth") {
      draftAlbum = blankAlbum(patternId, "New Album");
      album = draftAlbum;
      activePageIndex = 0;
      selectedPhotoIndex = null;
      selectedStickerId = null;
      setView("setup", false);
      render();
    }

    function openAlbumFromSetup() {
      if (draftAlbum) {
        library.albums.push(draftAlbum);
        library.activeAlbumId = draftAlbum.id;
        album = draftAlbum;
        draftAlbum = null;
      }
      setView("editor", false);
      saveLibrary();
      render();
      albumEl.classList.add("opening");
      setTimeout(() => albumEl.classList.remove("opening"), 760);
    }

    function duplicateAlbum() {
      const copy = normalizeAlbum(JSON.parse(JSON.stringify(album)));
      copy.id = crypto.randomUUID();
      copy.title = `${album.title} Copy`;
      library.albums.push(copy);
      library.activeAlbumId = copy.id;
      draftAlbum = null;
      album = copy;
      activePageIndex = 0;
      saveLibrary();
      setView("setup", false);
      render();
    }

    function updateAlbumOptions() {
      album.title = albumTitle.value || "My Digital Album";
      album.paperColor = paperColor.value;
      album.coverColor = coverColor.value;
      album.patternColor = patternColor.value;
      album.photosPerPage = Number(photosPerPage.value);
      album.frameStyle = frameStyle.value;
      album.pagePattern = pagePattern.value;
      coverTitle.value = album.title;
      trimExtraPhotos();
      if (!draftAlbum) saveLibrary();
      render();
    }

    function applyCoverPattern(patternId) {
      const pattern = coverPatterns.find((item) => item.id === patternId);
      if (!pattern) return;
      album.coverPattern = pattern.id;
      album.coverColor = pattern.coverColor;
      album.patternColor = pattern.patternColor;
      album.paperColor = pattern.paperColor;
      album.pagePattern = pattern.pagePattern;
      if (!draftAlbum) saveLibrary();
      render();
    }

    function setView(view, shouldRender = true) {
      activeView = view;
      app.className = `app ${view}-mode`;
      app.classList.toggle("setup-hidden", setupHidden && view === "editor");
      libraryTab.classList.toggle("active", view === "library");
      setupTab.classList.toggle("active", view === "setup");
      editorTab.classList.toggle("active", view === "editor");
      libraryView.classList.toggle("active", view === "library");
      setupView.classList.toggle("active", view === "setup");
      editorView.classList.toggle("active", view === "editor");
      document.getElementById("modeTitle").textContent = view === "library" ? "Home" : view === "setup" ? "Album setup" : "Open album";
      document.getElementById("helperText").textContent = view === "library" ? "Click + to create a new album, or open an existing cover." : view === "setup" ? "Choose the book and page details before opening it." : "Edit the open album pages.";
      if (shouldRender) render();
    }

    function setSetupHidden(hidden) {
      setupHidden = hidden;
      localStorage.setItem(`${storageKey}-setup-hidden`, String(hidden));
      setView(activeView, false);
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
      if (!library.albums.length) library.albums.push(blankAlbum("cloth", "My Digital Album"));
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
      if (!draftAlbum) album = activeAlbum();
      activePageIndex = Math.min(activePageIndex, album.pages.length - 1);
      renderTemplateGrid();
      renderLibrary();
      renderSetupPreview();
      renderEditor();
      renderCropPanel();
    }

    function renderTemplateGrid() {
      let currentGroup = "";
      templateGrid.innerHTML = coverPatterns.map((pattern) => {
        const heading = pattern.group === currentGroup ? "" : `<div class="pattern-group-title">${pattern.group}</div>`;
        currentGroup = pattern.group;
        return `
          ${heading}
          <button class="template-card ${album.coverPattern === pattern.id ? "active" : ""}" type="button" data-cover-pattern="${pattern.id}">
            ${coverMarkup({ ...album, title: pattern.name, coverColor: pattern.coverColor, patternColor: pattern.patternColor, coverPattern: pattern.id }, false)}
            <span>${pattern.name}</span>
          </button>
        `;
      }).join("");
      templateGrid.querySelectorAll("[data-cover-pattern]").forEach((button) => {
        button.addEventListener("click", () => applyCoverPattern(button.dataset.coverPattern));
      });
    }

    function renderLibrary() {
      libraryGrid.innerHTML = `
        <button class="library-card new-album-card" type="button" id="newAlbumCard">
          <span class="plus-mark">+</span>
          <strong>Create new album</strong>
          <span class="book-cover-meta">Choose a cover pattern</span>
        </button>
        ${library.albums.map((item) => `
        <button class="library-card" type="button" data-open-album="${item.id}">
          ${coverMarkup(item, true)}
          <span class="book-cover-meta">${item.pages.length} page${item.pages.length === 1 ? "" : "s"} · ${coverPatternName(item.coverPattern)}</span>
        </button>
      `).join("")}`;
      document.getElementById("newAlbumCard").addEventListener("click", () => startNewAlbum());
      libraryGrid.querySelectorAll("[data-open-album]").forEach((button) => {
        button.addEventListener("click", () => {
          library.activeAlbumId = button.dataset.openAlbum;
          draftAlbum = null;
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

    function renderSetupPreview() {
      setupBookPreview.innerHTML = coverMarkup(album, true, "large");
    }

    function coverMarkup(item, showTitle, extraClass = "") {
      const pattern = coverPatterns.find((entry) => entry.id === item.coverPattern) ?? coverPatterns[0];
      const art = pattern.svg ? svgBackground(pattern.svg, item.patternColor ?? pattern.patternColor) : pattern.art;
      return `
        <span class="book-cover ${extraClass}" style="--book-cover:${item.coverColor}; --pattern-color:${item.patternColor ?? pattern.patternColor}; --book-art:${art}">
          ${showTitle ? `<span class="book-cover-title">${escapeHtml(item.title)}</span>` : ""}
        </span>
      `;
    }

    function svgBackground(svg, color) {
      const encoded = encodeURIComponent(svg.replaceAll("PATTERN", color));
      return `url('data:image/svg+xml,${encoded}')`;
    }

    function coverPatternName(id) {
      return coverPatterns.find((pattern) => pattern.id === id)?.name ?? "Album";
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
      patternColor.value = album.patternColor;
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
      const rightPage = album.pages[activePageIndex + 1] ?? null;
      const slots = Array.from({ length: album.photosPerPage }, (_, index) => page.photos[index] ?? null);
      albumPage.style.setProperty("--page-pattern", pagePatterns[album.pagePattern] ?? pagePatterns.plain);
      albumPage.innerHTML = `
        <div class="book-spread">
          <section class="book-page left">
            ${editablePageMarkup(page, slots)}
          </section>
          <section class="book-page right ${rightPage ? "" : "empty-page"}">
            ${rightPage ? previewPageMarkup(rightPage) : "<span>Next page is waiting for your memories.</span>"}
          </section>
        </div>
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

    function editablePageMarkup(page, slots) {
      return `
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
    }

    function previewPageMarkup(page) {
      const slots = Array.from({ length: album.photosPerPage }, (_, index) => page.photos[index] ?? null);
      return `
        <div class="page-heading">
          <h2>${escapeHtml(page.title || "Untitled page")}</h2>
          <strong>${escapeHtml(page.date)}</strong>
        </div>
        <div class="photo-grid slots-${album.photosPerPage}">
          ${slots.map((photo) => `
            <div class="photo-slot">
              <div class="photo-frame">
                ${photo ? `<img src="${photo.src}" alt="${escapeAttribute(photo.caption || "Album photo")}" style="object-position:${photo.cropX ?? 50}% ${photo.cropY ?? 50}%; transform:scale(${photo.zoom ?? 1})">` : `<span class="upload-prompt"><span>Empty space</span></span>`}
              </div>
              <p class="photo-caption">${escapeHtml(photo?.caption ?? "")}</p>
            </div>
          `).join("")}
        </div>
        <p class="page-note">${escapeHtml(page.text)}</p>
        ${page.stickers.map((sticker) => `
          <span class="page-sticker" style="left:${sticker.x}%; top:${sticker.y}%; --tilt:${sticker.tilt}deg; --sticker-size:${sticker.size ?? 52}px">${stickerArt(sticker.id)}</span>
        `).join("")}
      `;
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
