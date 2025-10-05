from __future__ import annotations

from pathlib import Path

from PIL import Image
import numpy as np

from open_gov_construction.media import scan_images, find_duplicates, hamming

def test_media_scan_and_duplicates(tmp_path: Path) -> None:
    # Create two identical small images and one different
    img1 = Image.fromarray((np.ones((32, 32, 3), dtype=np.uint8) * 200))
    img2 = Image.fromarray((np.ones((32, 32, 3), dtype=np.uint8) * 200))
    img3 = Image.fromarray((np.zeros((32, 32, 3), dtype=np.uint8)))
    p1 = tmp_path / "a.png"
    p2 = tmp_path / "b.png"
    p3 = tmp_path / "c.png"
    img1.save(p1)
    img2.save(p2)
    img3.save(p3)
    infos = scan_images(tmp_path)
    assert len(infos) == 3
    dups = find_duplicates(infos, max_distance=5)
    # At least one pair (a,b) should be flagged duplicate
    assert any({d[0].path, d[1].path} == {str(p1), str(p2)} for d in dups)

def test_hamming_distance() -> None:
    assert hamming(0b1010, 0b1010) == 0
    assert hamming(0b1010, 0b0101) == 4
    assert hamming(0b1111, 0b0000) == 4
    assert hamming(0b1100, 0b1000) == 1

def test_media_scan_empty_folder(tmp_path: Path) -> None:
    empty_folder = tmp_path / "empty"
    empty_folder.mkdir()
    infos = scan_images(empty_folder)
    assert len(infos) == 0

def test_media_scan_image_properties(tmp_path: Path) -> None:
    # numpy arrays are (height, width, channels)
    img = Image.fromarray((np.ones((64, 48, 3), dtype=np.uint8) * 128))
    p = tmp_path / "test.png"
    img.save(p)
    infos = scan_images(tmp_path)
    assert len(infos) == 1
    info = infos[0]
    assert info.width == 48
    assert info.height == 64
    assert 0.0 <= info.brightness <= 1.0
    assert isinstance(info.phash, int)

