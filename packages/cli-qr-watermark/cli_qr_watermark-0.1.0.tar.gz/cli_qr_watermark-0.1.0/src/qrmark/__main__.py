import os
import sys
import glob
import click
from pathlib import Path
from PIL import Image
import qrcode
from rich.console import Console

console = Console()

@click.command()
@click.argument("pattern")
@click.option("--url", default="https://example.com", help="Ссылка в QR-коде")
@click.option("--opacity", default=0.4, help="Прозрачность 0-1")
@click.option("--size", default=128, help="Размер QR-кода в px")
@click.option("--output", default="./ready", help="Папка для результатов")
@click.option("--pro", is_flag=True, help="Отключает лимит в 50 файлов")
def cli(pattern, url, opacity, size, output, pro):
    """Накладывает QR-код на пачку картинок."""
    files = glob.glob(pattern)
    if not files:
        console.print("[red]❌ Файлы не найдены[/]")
        sys.exit(1)

    if len(files) > 50 and not pro and not os.getenv("QRMARK_PRO"):
        console.print("[yellow]🎁 Free tier: 50 файлов максимум.[/]")
        console.print("☕ Поддержи автора: https://buymeacoffee.com/ВАШ_НИК")
        sys.exit(0)

    Path(output).mkdir(exist_ok=True)

    # Генерируем QR-код с прозрачностью
    qr = qrcode.make(url).resize((size, size)).convert("RGBA")
    alpha = qr.getchannel("A").point(lambda p: int(p * opacity))
    qr.putalpha(alpha)

    for file in files:
        img = Image.open(file).convert("RGBA")
        x = img.width - size - 20
        y = img.height - size - 20
        img.alpha_composite(qr, dest=(x, y))
        out_path = Path(output) / (Path(file).stem + "_qr.png")
        img.save(out_path)
        console.print(f"[green]✅[/] {out_path}")

if __name__ == "__main__":
    cli()