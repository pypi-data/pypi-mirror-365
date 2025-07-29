from pathlib import Path
import typer

from vimeodlpy.downloader import VimeoDownloader
from vimeodlpy.utils import ffmpeg_installed

app = typer.Typer(add_completion=False)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    check_ffmpeg: bool = typer.Option(
        False,
        "--check-ffmpeg",
        help="Check if FFmpeg is installed and available in the system PATH.",
    ),
):
    """
vimeodlpy, a lightweight Vimeo downloader powered by FFmpeg.

GitHub : https://github.com/moijesuis2enmoi/vimeodlpy\n
PyPI   : https://pypi.org/project/vimeodlpy\n\n

Usage:\n
    vimeodlpy download "https://vimeo.com/123456789" output.mp4\n
"""
    if check_ffmpeg:
        if ffmpeg_installed():
            typer.echo("✅ FFmpeg is installed and accessible in the system PATH.")
        else:
            typer.echo("❌ FFmpeg is missing or not accessible (not found in PATH).")
            raise typer.Exit(code=1)
    elif not ctx.invoked_subcommand:
        typer.echo(ctx.get_help())


@app.command()
def download(
    url: str = typer.Argument(
        ...,
        help="The full Vimeo video URL (e.g. https://player.vimeo.com/video/123456789).",
    ),
    output: Path = typer.Argument(
        ...,
        help="The destination path for the downloaded video. Must end with '.mp4'.",
    ),
    proxy: str = typer.Option(
        None,
        "--proxy",
        help="Optional HTTP/HTTPS proxy (e.g. 'http://127.0.0.1:8080').",
    ),
    referer: str = typer.Option(
        None,
        "--referer",
        help="Optional Referer header (useful when downloading from embedded players).",
    ),
    no_progress: bool = typer.Option(
        False,
        "--no-progress",
        is_flag=True,
        help="Disable the real-time FFmpeg download progress bar.",
    ),
):
    """
    Download a Vimeo video to a local .mp4 file using FFmpeg.

    The tool automatically extracts the HLS stream from the Vimeo page
    and pipes it into FFmpeg for efficient downloading.

    Notes:
    ------
    - FFmpeg must be installed and accessible via your system PATH.
    - You may specify a proxy or a referer header if needed.
    - Use `--no-progress` to hide the FFmpeg progress bar.
    """
    if not ffmpeg_installed():
        typer.echo("❌ FFmpeg is not installed or not found in the system PATH.")
        raise typer.Exit(code=1)

    if output.suffix.lower() != ".mp4":
        typer.echo("❌ The output path must have a '.mp4' extension.")
        raise typer.Exit(code=1)

    transformed_proxy = None
    if proxy:
        if not proxy.startswith("http://") and not proxy.startswith("https://"):
            transformed_proxy = f"http://{proxy}"
        else:
            transformed_proxy = proxy
    proxies = {"http": transformed_proxy, "https": transformed_proxy} if transformed_proxy else None

    try:
        downloader_instance = VimeoDownloader(proxies=proxies, show_progress=not no_progress)
        downloader_instance.download(url, str(output), referer=referer)
    except Exception as e:
        typer.echo(f"❌ Error: {e}")
        raise typer.Exit(code=1)
