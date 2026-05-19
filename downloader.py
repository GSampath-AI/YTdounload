"""Interactive YouTube downloader — URLs from urls.txt, format/quality via prompts."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError, ExtractorError


URLS_FILE = Path("urls.txt")
OUTPUT_DIR = Path("downloads")

QUALITY_HEIGHT: dict[str, int | None] = {
    "1": None,
    "2": 2160,
    "3": 1440,
    "4": 1080,
    "5": 720,
    "6": 480,
}
QUALITY_LABEL = {
    "1": "Best available",
    "2": "4K (2160p)",
    "3": "1440p",
    "4": "1080p",
    "5": "720p",
    "6": "480p",
}


def _ffmpeg_bin_dir() -> Path | None:
    """Return the directory containing ffmpeg, including common Windows install paths."""
    if found := shutil.which("ffmpeg"):
        return Path(found).parent

    if sys.platform != "win32":
        return None

    local_app = os.environ.get("LOCALAPPDATA", "")
    if not local_app:
        return None

    winget_packages = Path(local_app) / "Microsoft" / "WinGet" / "Packages"
    if winget_packages.is_dir():
        for candidate in winget_packages.glob("**/ffmpeg.exe"):
            return candidate.parent

    for candidate in (
        Path(r"C:\ffmpeg\bin"),
        Path(r"C:\Program Files\ffmpeg\bin"),
    ):
        if (candidate / "ffmpeg.exe").is_file():
            return candidate

    return None


def _try_install_ffmpeg() -> bool:
    """Attempt to install ffmpeg using the platform package manager."""
    if sys.platform == "win32":
        if not shutil.which("winget"):
            print("   winget is not available on this system.")
            return False
        print("   Running: winget install Gyan.FFmpeg …")
        cmd = [
            "winget",
            "install",
            "--id",
            "Gyan.FFmpeg",
            "-e",
            "--accept-package-agreements",
            "--accept-source-agreements",
        ]
    elif sys.platform == "darwin":
        if not shutil.which("brew"):
            print("   Homebrew is not available. Install ffmpeg manually: brew install ffmpeg")
            return False
        print("   Running: brew install ffmpeg …")
        cmd = ["brew", "install", "ffmpeg"]
    else:
        if shutil.which("apt-get"):
            print("   Running: sudo apt-get install -y ffmpeg …")
            cmd = ["sudo", "apt-get", "install", "-y", "ffmpeg"]
        elif shutil.which("dnf"):
            print("   Running: sudo dnf install -y ffmpeg …")
            cmd = ["sudo", "dnf", "install", "-y", "ffmpeg"]
        else:
            print("   No supported package manager found for automatic install.")
            return False

    try:
        result = subprocess.run(cmd, check=False)
    except OSError as exc:
        print(f"   Install command failed: {exc}")
        return False

    if result.returncode != 0 and _ffmpeg_bin_dir() is None:
        print(f"   Install exited with code {result.returncode}.")
        return False
    return True


def ensure_ffmpeg(required: bool = True) -> Path | None:
    """Use existing ffmpeg or install it when missing."""
    found = _ffmpeg_bin_dir()
    if found is not None:
        return found

    print("🔍 ffmpeg not found — installing automatically…")
    _try_install_ffmpeg()
    found = _ffmpeg_bin_dir()

    if found is not None:
        print(f"✅ ffmpeg ready ({found})")
        return found

    print("❌ ffmpeg is still not available after install.")
    if required:
        if sys.platform == "win32":
            print("   Try manually: winget install Gyan.FFmpeg")
        sys.exit(1)
    return None


def read_urls(file_path: Path) -> list[str]:
    """Read non-empty, non-comment URL lines from a text file."""
    lines = file_path.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]


def _prompt(message: str) -> str:
    try:
        return input(message).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)


def _prompt_choice(title: str, options: list[str]) -> str:
    print(title)
    for i, label in enumerate(options, start=1):
        print(f"  {i}) {label}")
    while True:
        choice = _prompt("> ")
        if choice in {str(i) for i in range(1, len(options) + 1)}:
            return choice
        print(f"Please enter 1–{len(options)}.")


def _video_format(height: int | None, ffmpeg_dir: Path | None) -> str:
    """Pick streams up to the requested height; no silent jump above the cap."""
    if height is None:
        return "bestvideo+bestaudio/best" if ffmpeg_dir else "best"
    cap = f"[height<={height}]"
    if ffmpeg_dir:
        return f"bestvideo{cap}+bestaudio/best{cap}"
    return f"best{cap}"


def _fallback_video_format(ffmpeg_dir: Path | None) -> str:
    return "bestvideo+bestaudio/best" if ffmpeg_dir else "best"


def _actual_height(info: dict) -> int | None:
    if info.get("height"):
        return int(info["height"])
    for fmt in info.get("requested_formats") or []:
        if fmt.get("vcodec") not in (None, "none") and fmt.get("height"):
            return int(fmt["height"])
    return None


def _friendly_error(exc: Exception) -> str:
    msg = str(exc).lower()
    if "private video" in msg:
        return "This video is private."
    if "video unavailable" in msg or "not available" in msg:
        return "Video is unavailable (removed, deleted, or blocked in your region)."
    if "sign in" in msg or "age" in msg:
        return "This video may be age-restricted or require sign-in."
    if "copyright" in msg or "blocked" in msg:
        return "This video cannot be downloaded (blocked or restricted)."
    if "format" in msg and "not available" in msg:
        return "No stream matched the requested quality for this video."
    return str(exc)


def _is_format_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return "requested format" in msg or (
        "format" in msg and "not available" in msg
    )


def _print_resolution_note(
    info: dict,
    quality_key: str | None,
    used_fallback: bool,
) -> None:
    actual = _actual_height(info)
    if actual is None:
        return
    requested = QUALITY_HEIGHT.get(quality_key or "4")
    label = QUALITY_LABEL.get(quality_key or "4", "")
    print(f"📺 Saved at {actual}p")
    if used_fallback:
        print(f"ℹ️  {label} was not available — used the best quality YouTube offers for this video.")
    elif requested is not None and actual < requested:
        print(f"ℹ️  {label} was not available — used the highest quality at or below that ({actual}p).")


def _build_ydl_opts(
    media: str,
    quality_key: str | None,
    output_dir: Path,
    ffmpeg_dir: Path | None,
    *,
    video_format: str | None = None,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    opts: dict = {
        "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    if ffmpeg_dir is not None:
        opts["ffmpeg_location"] = str(ffmpeg_dir)

    if media == "mp3":
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]
        return opts

    height = QUALITY_HEIGHT[quality_key or "4"]
    opts["format"] = video_format or _video_format(height, ffmpeg_dir)
    if ffmpeg_dir is not None and media != "mp3":
        opts["merge_output_format"] = "mp4"
    elif media != "mp3":
        print("⚠️  ffmpeg not found. Using best single-file format (may not be exact quality).")

    return opts


def _resolved_path(ydl: YoutubeDL, info: dict, media: str) -> Path:
    path = Path(ydl.prepare_filename(info))
    if media == "mp3":
        return path.with_suffix(".mp3")
    ext = info.get("ext") or path.suffix.lstrip(".")
    if ext and path.suffix.lower() != f".{ext}".lower():
        return path.with_suffix(f".{ext}")
    return path


def _download_url(
    ydl: YoutubeDL,
    url: str,
    media: str,
    quality_key: str | None,
    output_dir: Path,
    ffmpeg_dir: Path | None,
) -> tuple[dict | None, bool, YoutubeDL]:
    """Download one URL. Returns (info, used_quality_fallback, ydl_used)."""
    try:
        info = ydl.extract_info(url, download=True)
        return info, False, ydl
    except (DownloadError, ExtractorError) as exc:
        if media != "mp4" or not _is_format_error(exc):
            raise
        fallback_opts = _build_ydl_opts(
            media,
            quality_key,
            output_dir,
            ffmpeg_dir,
            video_format=_fallback_video_format(ffmpeg_dir),
        )
        with YoutubeDL(fallback_opts) as fallback_ydl:
            info = fallback_ydl.extract_info(url, download=True)
            return info, True, fallback_ydl


def download_all(
    urls: list[str],
    output_dir: Path,
    media: str,
    quality_key: str | None,
) -> list[Path]:
    ffmpeg_dir = ensure_ffmpeg(required=(media == "mp3"))
    ydl_opts = _build_ydl_opts(media, quality_key, output_dir, ffmpeg_dir)
    saved: list[Path] = []

    with YoutubeDL(ydl_opts) as ydl:
        for url in urls:
            print(f"\n✅ Downloading... {url}")
            try:
                info, used_fallback, used_ydl = _download_url(
                    ydl, url, media, quality_key, output_dir, ffmpeg_dir
                )
                if info is None:
                    print(f"❌ Failed: could not fetch info for {url}")
                    continue
                dest = _resolved_path(used_ydl, info, media)
                saved.append(dest)
                print("✅ Downloading... Done!")
                print(f"📁 Saved to: {dest}")
                if media == "mp4":
                    _print_resolution_note(info, quality_key, used_fallback)
            except (DownloadError, ExtractorError) as exc:
                print(f"❌ Failed for {url}: {_friendly_error(exc)}")

    return saved


def main() -> None:
    print()
    print("🎥 YouTube Video Downloader")
    print("---------------------------")

    if not URLS_FILE.exists():
        print(f"❌ URL file not found: {URLS_FILE}")
        print("   Create it with one YouTube URL per line.")
        sys.exit(1)

    urls = read_urls(URLS_FILE)
    if not urls:
        print(f"❌ No URLs found in {URLS_FILE}.")
        sys.exit(1)

    print(f"📋 Loaded {len(urls)} URL(s) from {URLS_FILE}")
    for u in urls:
        print(f"   • {u}")
    print()

    format_choice = _prompt_choice(
        "Choose format:",
        ["MP4 (Video)", "MP3 (Audio only)"],
    )

    quality_key: str | None = None
    if format_choice == "1":
        quality_key = _prompt_choice(
            "Choose quality:",
            [
                "Best available",
                "4K (2160p)",
                "1440p",
                "1080p",
                "720p",
                "480p",
            ],
        )
        print(f"\n⬇️  Format: MP4 · Quality: {QUALITY_LABEL[quality_key]}")
        print("   (If that resolution is not on YouTube, the best available quality is used.)")
    else:
        print("\n⬇️  Format: MP3 (Audio only)")

    media = "mp4" if format_choice == "1" else "mp3"
    output_dir = OUTPUT_DIR.resolve()
    print(f"📂 Output folder: {output_dir}\n")

    download_all(urls, output_dir, media, quality_key)

    if urls:
        print(f"\n🎉 Finished. Check: {output_dir}")


if __name__ == "__main__":
    main()
