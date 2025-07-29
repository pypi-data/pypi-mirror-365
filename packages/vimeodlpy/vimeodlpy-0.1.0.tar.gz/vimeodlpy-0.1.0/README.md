# vimeodlpy

> A lightweight Python library and CLI to download Vimeo videos using FFmpeg.

![PyPI](https://img.shields.io/pypi/v/vimeodlpy)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/github/license/moijesuis2enmoi/vimeodlpy)

---

## Overview

`vimeodlpy` is a minimal yet powerful tool for downloading Vimeo videos through their HLS streams, using `ffmpeg` under the hood. It supports direct and embedded Vimeo player URLs, with optional proxy and referer headers for restricted content.

You can use it as a **Python library** or via a simple **command-line interface**.

---

## ✨ Features

- ✅ Extracts HLS stream URLs automatically from Vimeo pages
- 🎞️ Downloads video using `ffmpeg` with a live progress bar
- 🌍 Supports custom proxy and referer headers
- 🐍 Usable as both CLI and Python module
- 💡 Simple and lightweight, no browser automation or login required

---

## ⚙️ Requirements

- Python **3.11 or newer**
- [FFmpeg](https://ffmpeg.org/download.html) installed and available in your system `PATH`

To verify if FFmpeg is accessible:

```bash
ffmpeg -version
````

---

## 📦 Installation

Install from [PyPI](https://pypi.org/project/vimeodlpy):

```bash
pip install vimeodlpy
```

---

## 🚀 CLI Usage

```bash
vimeodlpy download [VIDEO_URL] [OUTPUT_FILE.mp4]
```

### Example

```bash
vimeodlpy download "https://vimeo.com/123456789" output.mp4
```

### Options

- `--proxy`: Set an HTTP or HTTPS proxy (`http://127.0.0.1:8080`)
- `--referer`: Specify a referer header (for embedded videos)
- `--no-progress`: Disable the FFmpeg download progress bar
- `--check-ffmpeg`: Check if FFmpeg is installed

### Check FFmpeg availability

```bash
vimeodlpy --check-ffmpeg
```

---

## 🐍 Python Usage

```python
from vimeodlpy import downloader

downloader.download(
    url="https://vimeo.com/123456789",
    output_path="output.mp4",
    referer=None,
    proxies=None
)
```

### Parameters

- `url` (str): Vimeo video URL
- `output_path` (str): Path to save the `.mp4` file
- `referer` (str | None): Optional HTTP referer
- `proxies` (dict | None): Optional proxies (e.g., `{"http": "...", "https": "..."}`)

---

## 🛠 Development

Clone the repo and install with Poetry:

```bash
git clone https://github.com/moijesuis2enmoi/vimeodlpy.git
cd vimeodlpy
poetry install
```

---

## 🤝 Contributing

Contributions are welcome! If you have suggestions, feature requests or bug reports:

- Open an [issue](https://github.com/moijesuis2enmoi/vimeodlpy/issues)
- Or submit a pull request!

Please make sure to lint and test your code before submitting.

---

## 📄 License

This project is licensed under the **Apache License 2.0**.
See the [LICENSE](./LICENSE) file for details.

---

Made with ❤️ by [moijesuis2enmoi](https://github.com/moijesuis2enmoi)
