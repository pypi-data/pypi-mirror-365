from pathlib import Path
from PIL import Image
import subprocess

def test_cli():
    subprocess.run([
        "qrmark", "examples/*.png", "--url", "https://test.com"
    ], check=True)
    assert list(Path("ready").glob("*_qr.png"))