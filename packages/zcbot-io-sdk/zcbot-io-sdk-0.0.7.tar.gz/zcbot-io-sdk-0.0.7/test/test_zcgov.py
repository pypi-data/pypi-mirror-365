# encoding: utf-8

from zcbot_io_sdk.images import processor

img_list = ['https://itemcdn.zcycdn.com/2018050710312619017758.jpg',
            'https://itemcdn.zcycdn.com/2018050710300656182860.jpg',
            'https://itemcdn.zcycdn.com/2018050710300655368671.jpg']

size = "w800_h800"
# size = "w790_h0"


result = processor.process_images(img_list, size, plat_code="zcgov")

print(result)
