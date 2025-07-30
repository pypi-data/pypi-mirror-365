# encoding: utf-8

from zcbot_io_sdk.images import processor

img_list = [
    "https://img.alicdn.com/imgextra/i1/407910984/O1CN01Mse8Xv1J8iWW4arT8_!!407910984.jpg",
    "https://img.alicdn.com/imgextra/i2/407910984/O1CN01XbDhaW1J8iWN1DLOp_!!407910984.jpg",
    "https://img.alicdn.com/imgextra/i3/407910984/O1CN01dHXgT11J8iWQ5VLmj_!!407910984.jpg",
    "https://img.alicdn.com/imgextra/i4/407910984/O1CN01UbKdq31J8iWN1DsdT_!!407910984.jpg",
    "https://img.alicdn.com/imgextra/i4/407910984/O1CN01it6bsx1J8iWQ5Vt34_!!407910984.jpg",
    "https://img.alicdn.com/imgextra/i4/407910984/O1CN01XKQMgF1J8iWXyAJtM_!!407910984.jpg",
    "https://img.alicdn.com/imgextra/i3/407910984/O1CN01kSDtKC1J8iWQ5VYGg_!!407910984.jpg",
    "https://img.alicdn.com/imgextra/i2/407910984/O1CN01pN1dj11J8iWPxDhTZ_!!407910984.jpg"
]

# size = "w800_h800"
size = "w790_h0"

result = processor.process_images(img_list, size, plat_code="tmall")

print(result)

res = ['http://io.zcbot.cn/wmc/image/common/?src_url=De0PGeTQNR9pnlGfklMpkB0fNgE2nm9pnl7WKe0Rkm9pTmIPTXGzTHqztXr2H8YXHwqMHcEWtYbBTsCyDV7cEOYRVXbo5maPTXGzTHqztXrfDAiA&size=w790_h0&format=jpeg',
       'http://io.zcbot.cn/wmc/image/common/?src_url=De0PGeTQNR9pnlGfklMpkB0fNgE2nm9pnl7WKe0Rkm9pThIPTXGzTHqztXr2H8YXHwqMlOjaDOYcTsCyDV7tTs0THuio5maPTXGzTHqztXrfDAiA&size=w790_h0&format=jpeg',
       'http://io.zcbot.cn/wmc/image/common/?src_url=De0PGeTQNR9pnlGfklMpkB0fNgE2nm9pnl7WKe0Rkm9pTRIPTXGzTHqztXr2H8YXHwqMdabkdFrMTsCyDV70EVdTnlpo5maPTXGzTHqztXrfDAiA&size=w790_h0&format=jpeg',
       'http://io.zcbot.cn/wmc/image/common/?src_url=De0PGeTQNR9pnlGfklMpkB0fNgE2nm9pnl7WKe0Rkm9pEJIPTXGzTHqztXr2H8YXHwqMVljNdea8TsCyDV7tTs08dY0o5maPTXGzTHqztXrfDAiA&size=w790_h0&format=jpeg',
       'http://io.zcbot.cn/wmc/image/common/?src_url=De0PGeTQNR9pnlGfklMpkB0fNgE2nm9pnl7WKe0Rkm9pEJIPTXGzTHqztXr2H8YXHwqMDcrBkAEyTsCyDV70EVdPT80o5maPTXGzTHqztXrfDAiA&size=w790_h0&format=jpeg',
       'http://io.zcbot.cn/wmc/image/common/?src_url=De0PGeTQNR9pnlGfklMpkB0fNgE2nm9pnl7WKe0Rkm9pEJIPTXGzTHqztXr2H8YXHwqMlaL0Hl7OTsCyDV7kKsYS7aFo5maPTXGzTHqztXrfDAiA&size=w790_h0&format=jpeg',
       'http://io.zcbot.cn/wmc/image/common/?src_url=De0PGeTQNR9pnlGfklMpkB0fNgE2nm9pnl7WKe0Rkm9pTRIPTXGzTHqztXr2H8YXHwqMDFEa7aLXTsCyDV70EVdd0B7o5maPTXGzTHqztXrfDAiA&size=w790_h0&format=jpeg',
       'http://io.zcbot.cn/wmc/image/common/?src_url=De0PGeTQNR9pnlGfklMpkB0fNgE2nm9pnl7WKe0Rkm9pThIPTXGzTHqztXr2H8YXHwqMGayMdOCMTsCyDV7rKa0CVYpo5maPTXGzTHqztXrfDAiA&size=w790_h0&format=jpeg']
