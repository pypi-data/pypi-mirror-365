# encoding: utf-8

from zcbot_io_sdk.images import processor

img_list = [
    "https://img.jslink.com/FILE00661ee8c5a948ac9489d6b84cf22c5e.jpg",
    "https://img.jslink.com/FILE6a38aab58c804647ab0694ab765fc242.jpg",
    "https://img.jslink.com/FILE25e27e338275490e9929986d50e758d5.jpg",
    "https://img.jslink.com/FILE1995a88a14534308b33774c8e161e473.jpg",
    "https://img.jslink.com/FILE97568c129dc840ffb8888eb8f7c4a08f.jpg",
    "https://img.jslink.com/FILEef9786b57b054716a7428f719688a70a.jpg",
    "https://img.jslink.com/FILEaf3de846710a4c69ad690c4f7c183c8f.jpg",
    "https://img.jslink.com/FILE9792c8c4d6a84b22a685c2bc85a10991.jpg",
    "https://img.jslink.com/FILE4e3bc34d1b744c00ae6f9eb6693ac97d.jpg",
    "https://img.jslink.com/FILEc1963a31e1544f67b2c3aeecda407532.jpg"
]

size = "w800_h800"
# size = "w790_h0"


result = processor.process_images(img_list, size, plat_code="jslink")

print(result)
