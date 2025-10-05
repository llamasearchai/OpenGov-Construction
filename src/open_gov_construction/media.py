from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from PIL import Image, ImageOps

@dataclass(frozen=True)
class ImageInfo:
    path: str
    width: int
    height: int
    brightness: float
    phash: int

def _phash(image: Image.Image, hash_size: int = 8) -> int:
    """
    Simple perceptual hash: resize -> DCT-like via FFT of grayscale -> compare to median magnitude.
    """
    img = ImageOps.grayscale(image.resize((hash_size * 4, hash_size * 4)))
    arr = np.asarray(img, dtype=np.float32)
    # 2D DCT via FFT trick: real FFT magnitude approximates; good enough for duplicate screening
    F = np.fft.rfft2(arr)
    mag = np.abs(F)[:hash_size, :hash_size]
    med = np.median(mag)
    bits = (mag > med).astype(np.uint8)
    h = 0
    for b in bits.flatten():
        h = (h << 1) | int(b)
    return int(h)

def _brightness(image: Image.Image) -> float:
    g = ImageOps.grayscale(image)
    arr = np.asarray(g, dtype=np.float32)
    return float(np.mean(arr) / 255.0)

def scan_images(folder: Path) -> List[ImageInfo]:
    infos: List[ImageInfo] = []
    for p in sorted(Path(folder).glob("*")):
        if p.suffix.lower() not in (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"):
            continue
        with Image.open(p) as im:
            im.load()
            info = ImageInfo(
                path=str(p),
                width=im.width,
                height=im.height,
                brightness=_brightness(im),
                phash=_phash(im),
            )
            infos.append(info)
    return infos

def hamming(a: int, b: int) -> int:
    return int(bin(a ^ b).count("1"))

def find_duplicates(infos: List[ImageInfo], max_distance: int = 5) -> List[Tuple[ImageInfo, ImageInfo, int]]:
    """
    Return pairs of images with perceptual hash Hamming distance <= max_distance.
    """
    pairs: List[Tuple[ImageInfo, ImageInfo, int]] = []
    for i in range(len(infos)):
        for j in range(i + 1, len(infos)):
            d = hamming(infos[i].phash, infos[j].phash)
            if d <= max_distance:
                pairs.append((infos[i], infos[j], d))
    return pairs

