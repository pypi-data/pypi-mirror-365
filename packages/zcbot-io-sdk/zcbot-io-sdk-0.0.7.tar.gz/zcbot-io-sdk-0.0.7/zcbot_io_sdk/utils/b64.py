# -*- coding: utf-8

import base64
import mimetypes
from typing import List

mime = mimetypes.MimeTypes()

# 标准码表
STANDARD_ALPHABET = b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
# 魔改码表
CUSTOM_ALPHABET = b'qiJXaYOe5jSNTEt1r0mHsVlckdDnG7Ko6bhwxWgACp4Z3Lf2vMR8PFBuyzQUI9,!'
ENCODE_TRANS = bytes.maketrans(STANDARD_ALPHABET, CUSTOM_ALPHABET)
DECODE_TRANS = bytes.maketrans(CUSTOM_ALPHABET, STANDARD_ALPHABET)


def encode(inputs):
    try:
        return base64.b64encode(inputs).translate(ENCODE_TRANS).decode()
    except Exception:
        return None


def decode(inputs):
    try:
        return base64.b64decode(inputs.translate(DECODE_TRANS)).decode()
    except Exception:
        return None


def fill_link(url, base=''):
    try:
        if url and url.startswith('//'):
            return 'http:' + url.strip()
        elif url and url.startswith('/') and base:
            return base + url.strip()
        elif not url.startswith('/') and not url.startswith('http'):
            return 'http://' + url.strip()
        return url.strip()
    except ValueError:
        return url.strip()


def encode_single_img(img_path: str, plat_code: str = "common") -> str:
    base_url = f"https://io.zcbot.cn/images/wmc/{plat_code}?src_url="
    return base_url + encode(fill_link(img_path).encode())


def encode_plat_code_img(img_list: List[str], plat_code) -> List[str]:
    if not img_list:
        return img_list
    temp = []
    base_url = f"https://io.zcbot.cn/images/wmc/{plat_code}?src_url="
    for img in img_list:
        img_type = mime.guess_type(img)[0]
        if img_type == "image/gif":
            continue
        temp.append(base_url + encode(fill_link(img).encode()))

    return temp


if __name__ == '__main__':
    url = "De0PGeTQNR9pnlG8TJy8Ewih7cWpnlGfkB9LNuEZ7m98E8xvKXioDgd8NurMN8aPtHqBTRI8TmIFE8azN8a8THavEmIFdwEwdH0gExsvkw6PtHGvkR9bEBk8kl5utHqPdHqBEgs8Ngpvdv=="
    result = decode(url)
    print(result)
