# encoding: utf-8

import re
import mimetypes
from typing import List, Optional, Tuple
from zcbot_io_sdk.utils import b64 as b64_utils

mime = mimetypes.MimeTypes()


def process_single_image(img: str, size: str = "w800_h800", format: str = "jpeg", plat_code: str = "") -> Optional[str]:
    """
    会过滤掉gif
    :param img_list: 图片列表
    :param size: 尺寸，主图 "w800_h800"， 详图 "w790_h"、"w750_h"
    :param format: 图片格式，默认保存成jpg
    :param plat_code: 平台编码，针对不同平台单独处理
    :return: new_image_link, None
    """
    result = process_images([img], size, format, plat_code)
    if result:
        return result[0]
    return None


def process_images(img_list: List[str], size: str = "w800_h800", format: str = "jpeg", plat_code: str = "") -> List[str]:
    """
    :param img_list: 图片列表
    :param size: 尺寸，主图 "w800_h800"， 详图 "w790_h"、"w750_h"
    :param format: 图片格式，默认保存成jpg
    :param plat_code: 平台编码，针对不同平台单独处理
    :return: img_list: 图片列表
    """
    width, height = extract_width_height(size)
    if plat_code == "jd":
        return process_jd_images(img_list, width, height)
    elif plat_code == "suning":
        return process_suning_images(img_list, size, width, height, format)
    else:
        return process_common_images(img_list, size, format, plat_code)


def extract_width_height(size: str = "w800_h800") -> Tuple[int, int]:
    width = 800
    height = 0
    if size and "_" in size:
        try:
            w_width, h_height = size.split("_")
            width = w_width.replace("w", "")
            width = int(width)
            height = h_height.replace("h", "")
            if height in ["0", ""]:
                height = 0
            else:
                try:
                    height = int(height)
                except Exception as e:
                    print(e)
                    height = 0

        except Exception as e:
            print(e)

    return (width, height)


def process_common_images(img_list: List[str], size: str = "", format: str = "jpeg", plat_code: str = "") -> List[str]:
    if not img_list:
        return img_list
    temp_list = []
    img_url_end = f"&size={size}&format={format}"
    if not plat_code:
        plat_code = "common"
    for img in img_list:
        new_image = b64_utils.encode_single_img(img, plat_code) + img_url_end
        temp_list.append(new_image)

    return temp_list


def fix_single_image(url: str) -> str:
    if not url:
        return url
    pattern = "/s\d+x\d+_jfs/"
    repl = "/jfs/"
    result = re.sub(pattern, repl, url)
    return result


def process_jd_images(img_list: List[str], width: int = 800, height: int = 800) -> List[str]:
    if width == 0:
        return img_list

    temp_list = []
    repl_string = f"/s{width}x{height}_jfs/"
    for img in img_list:
        img = fix_single_image(img)
        new_image = img.replace("/jfs/", repl_string)
        img_type = mime.guess_type(img)[0]
        if img_type == "image/gif":
            continue
        if img_type != "image/jpeg":
            new_image = new_image + ".jpg"
        temp_list.append(new_image)

    return temp_list


def process_suning_images(img_list: List[str], size: str = "", width: int = 800, height: int = 800, _format: str = "jpeg") -> List[str]:
    if width == 0:
        return img_list
    temp_list = []
    img_url_end = f"&size={size}&format={_format}"

    if height == 0:
        sn_url_end = f"jpg_{width}w_4e"
    else:
        sn_url_end = f"jpg_{width}w_{height}h_4e"
    for img in img_list:
        img_type = mime.guess_type(img)[0]
        if img_type == "image/gif":
            continue
        if img_type != "image/jpeg":
            new_image = b64_utils.encode_single_img(img, "suning") + img_url_end
            temp_list.append(new_image)
            continue
        if img_type == "image/jpeg":
            if img.endswith(".jpg"):
                # new_image = new_image.replace("jpg", sn_url_end)
                new_image = img + f'?width={width}&crop=0'
            else:
                if height == 0:
                    new_image = re.sub(r"jpg_\d+w_\de", sn_url_end, img)
                else:
                    new_image = re.sub(r"jpg_\d+w_\d+h_\de", sn_url_end, img)

            temp_list.append(new_image)
            continue

    return temp_list
