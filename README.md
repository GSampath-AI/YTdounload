# YTdounload
🎥 Python-based YouTube downloader — download videos in MP4 or extract audio as MP3 with a simple CLI.


<h1 align="center">🎥 YouTube Video Downloader</h1>

<p align="center">
  A simple, fast Python tool to download YouTube videos and audio from the command line.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/PRs-Welcome-blue?style=for-the-badge"/>
</p>

---

## 📖 About

This is a lightweight Python application that lets you download YouTube videos in multiple formats and resolutions — or extract just the audio as MP3 — directly from your terminal. Built as a clean, no-frills alternative to bloated downloader websites full of ads and popups.

Perfect for:
- 📚 Saving educational content for offline viewing
- 🎵 Building your music library from YouTube audio
- 🎬 Archiving your own content
- 🧑‍💻 Learning how video/audio extraction works in Python

---

## ✨ Features

- 📥 Download YouTube videos in **MP4** format
- 🎵 Extract audio as **MP3**
- 🎯 Choose video quality (144p, 360p, 720p, 1080p, and higher)
- ⚡ Fast and lightweight — no bloat, no ads
- 💻 Simple command-line interface
- 📁 Custom output folder support
- 🔓 100% free and open source

---

## 📸 Demo

> _Add a screenshot or GIF of the tool running here — this massively increases stars._

```
$ python downloader.py

🎥 YouTube Video Downloader
---------------------------
Enter YouTube URL: https://www.youtube.com/watch?v=...
Choose format:
  1) MP4 (Video)
  2) MP3 (Audio only)
> 1

Choose quality:
  1) 1080p
  2) 720p
  3) 480p
> 2

✅ Downloading... Done!
📁 Saved to: ./downloads/video_title.mp4
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- FFmpeg (required for MP3 conversion)

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/sampath-pegasus/youtube-downloader.git
cd youtube-downloader
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Install FFmpeg** (only needed for MP3 extraction)

- **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
- **macOS:** `brew install ffmpeg`
- **Linux:** `sudo apt install ffmpeg`

---

## 💻 Usage

### Basic usage

```bash
python downloader.py
```

You'll be prompted to enter the YouTube URL and choose your preferred format and quality.

### Direct URL (optional)

```bash
python downloader.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Audio only

```bash
python downloader.py "URL" --audio
```

### Custom output folder

```bash
python downloader.py "URL" --output ./my-videos
```

---

## 🛠️ Built With

- **[Python 3](https://www.python.org/)** — core language
- **[pytube](https://pytube.io/)** / **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** — YouTube video extraction
- **[FFmpeg](https://ffmpeg.org/)** — audio conversion to MP3
- **[tqdm](https://github.com/tqdm/tqdm)** — progress bar

---

## 📂 Project Structure

```
youtube-downloader/
├── downloader.py         # Main script
├── requirements.txt      # Python dependencies
├── README.md             # You are here
├── LICENSE               # MIT license
└── downloads/            # Default output folder
```

---

## 📋 Roadmap

- [ ] Add GUI version (Tkinter / PyQt)
- [ ] Playlist download support
- [ ] Batch downloads from a `.txt` file of URLs
- [ ] Resume interrupted downloads
- [ ] Subtitle download support
- [ ] Cross-platform `.exe` and `.app` builds

---

## 🐛 Known Issues

- YouTube occasionally updates its backend, which may break `pytube`. If downloads fail, update with: `pip install --upgrade pytube`
- Some age-restricted videos may not be downloadable without authentication

Found a bug? [Open an issue](https://github.com/sampath-pegasus/youtube-downloader/issues).

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## ⚖️ Disclaimer

This tool is intended for **personal and educational use only**. Please respect YouTube's [Terms of Service](https://www.youtube.com/t/terms) and copyright laws. Only download content that you have the right to download, such as your own videos, Creative Commons content, or videos with explicit permission from the creator.

The author is not responsible for any misuse of this tool.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 👤 Author

**Sampath**

- GitHub: [@sampath-pegasus](https://github.com/sampath-pegasus)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/your-profile)
- Email: your.email@example.com

---

## 🙏 Acknowledgments

- The [pytube](https://pytube.io/) team for the excellent library
- The open-source community for inspiration and tools
- Everyone who stars and contributes to this project ❤️

---

<p align="center">
  ⭐ <b>If you found this project useful, please consider giving it a star!</b> ⭐<br><br>
  Built with ☕ and Python by <a href="https://github.com/sampath-pegasus">Sampath</a>
</p>
