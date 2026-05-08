# My Digital Album

My Digital Album is a local web app for creating a digital photo album from pictures on your device.

It runs on your computer and opens in your browser. You can choose an album style, upload photos into page slots, add titles, dates, memory text, and decorate pages with cute built-in stickers.

## Features

- Create an album from a setup page.
- Choose album orientation: vertical or horizontal.
- Choose the paper color.
- Choose the outside cover color.
- Pick how many photos each page should contain, from 1 to 4.
- Pick a frame style: no frame, simple frame, photo corners, or polaroid.
- Upload pictures from your device into page spaces.
- Add a main album title.
- Add page titles.
- Add dates.
- Add picture captions.
- Add free text memories on each page.
- Add cute custom stickers drawn inside the app.
- Move and resize stickers on the album page.
- Drag photos between page slots.
- Drag image files from your device directly onto photo slots.
- Choose album templates: travel, family, birthday, graduation, or wedding.
- Choose page background patterns.
- Use crop controls for each photo frame.
- Manage multiple albums from the library page.
- Add an optional 4 digit password lock.
- Add and delete pages.
- Print or save the album as PDF from the browser.
- Export the current album as a single HTML file.
- Save the album locally in browser storage.

## How It Works

The app starts a tiny local web server on:

```text
http://127.0.0.1:8790
```

Run it with:

```bash
python3 my_digital_album.py
```

Then open the local URL above.

## Photo Access

The app can access your pictures only when you choose them through the browser file picker.

It does not scan your device or read folders by itself. Uploaded photos are converted into local browser data and saved in your browser's local storage.

## Privacy

Your album is local to your computer and browser profile.

Important caveats:

- The album is not uploaded anywhere by the app.
- The optional password is a local app lock. It helps during normal use, but it does not encrypt album data.
- Exported HTML files include the album content and uploaded images inside the file.
- Clearing browser data can erase the saved album.
- Large photo files can fill browser storage quickly.
- A different browser profile will have different saved albums.
- Anyone with access to your computer/browser profile may be able to see the album.

## Project Structure

```text
.
├── my_digital_album.py
├── README.md
└── .gitignore
```
