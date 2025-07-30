# encoding: utf-8

from zcbot_io_sdk.images import processor

img_list = ['https://private.zkh.com/PRODUCT/BIG/BIG_AQ6327_01.jpg?x-oss-process=style/common_style_100&timestamp=1713107226000',
            'https://private.zkh.com/PRODUCT/BIG/BIG_AQ6327_02.jpg?x-oss-process=style/common_style_100&timestamp=1713107226000',
            'https://private.zkh.com/PRODUCT/BIG/BIG_AQ6327_03.jpg?x-oss-process=style/common_style_100&timestamp=1713107226000']

# size = "w800_h800"
size = "w790_h0"

result = processor.process_images(img_list, size, plat_code="zkh")

print(result)
