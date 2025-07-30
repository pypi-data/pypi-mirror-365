# encoding: utf-8


from zcbot_io_sdk.images import processor


def test_suning_transform():
    img_list = [
        "https://uimgproxy.suning.cn/uimg1/sop/commodity/lsBysxBASsdEn-qf5lZkyw.jpg",
        "https://uimgproxy.suning.cn/uimg1/sop/commodity/aUqL3sfpT9tIW2u-MUTsuw.jpg",
        "https://uimgproxy.suning.cn/uimg1/sop/commodity/e5kEZa6ROBPyVZHJQ-2TSQ.jpg",

        "https://image.suning.cn/uimg/sop/commodity/131609329115490163701094_x.jpg"
    ]

    # size = "w800_h800"
    size = "w790_h0"

    result = processor.process_images(img_list, size, plat_code="suning")

    for row in result:
        print(row)
