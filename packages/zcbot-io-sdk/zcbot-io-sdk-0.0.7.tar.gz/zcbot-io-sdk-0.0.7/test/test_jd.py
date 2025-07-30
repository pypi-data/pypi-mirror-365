# encoding: utf-8

from zcbot_io_sdk.images import processor

img_list = [
    "http://img10.360buyimg.com/imgzone/jfs/t1/53885/17/2019/205745/5cfe7afaEeb684da5/19d28a289c464bb5.jpg",
    "http://img30.360buyimg.com/popWaterMark/jfs/t1/49812/32/2138/199700/5cfe7afaE5de20c7e/8b2929d878017c46.jpg",
    "http://img30.360buyimg.com/popWaterMark/jfs/t1/72066/38/1558/256302/5cfe7681Ef11479a4/1df9d6c9b610d6da.jpg",
    "http://img30.360buyimg.com/popWaterMark/jfs/t1/79904/38/1575/294835/5cfe7681E403c630e/a4cbeeabbb0b547e.jpg",
    "http://img30.360buyimg.com/popWaterMark/jfs/t1/75227/28/1620/197213/5cfe7682E6c2eb42d/3918b6268ac55254.jpg",
    "http://img30.360buyimg.com/popWaterMark/jfs/t1/49871/19/2098/229167/5cfe7682E2187e1c6/3073312317fe580c.jpg",

]

size = "w800_h700"

result = processor.process_images(img_list, size)

print(result)
res = ['http://io.zcbot.cn/wmc/image/common/?src_url=De0PGXC2NBWLd8avNwTBTOjFKlWLdRzwnBP2DlFAKg9fdm94dAT27Xa2EHTytXs2THG2TwqMtmIRTXsuEXs2ElEgdH7bdgYYdl5BtX0xkHs2THWxTwbbTw6zk8rBEOjhEmz4GOG=&size=w800_h700&format=jpeg',
       'http://io.zcbot.cn/wmc/image/common/?src_url=De0PGXC2NBWLd8TvNwTBTOjFKlWLdRzwnBP2GO9vVBYPdcjEkcjZNBpgGR9PTmIPtH6MThI8ThIRTHTyN8aztHGvTJIFkBdWEBYgkssFdOsRTOTudmIykw5zTwWxtXGyTXauk8rBNgpvdv==&size=w800_h700&format=jpeg',
       'http://io.zcbot.cn/wmc/image/common/?src_url=De0PGXC2NBWLd8TvNwTBTOjFKlWLdRzwnBP2GO9vVBYPdcjEkcjZNBpgGR9PTmIuTwqBEhI8tJIMEHsyN85FEwTvThIFkBdWE8kyTsVgTHaPE8WbEJIMdOkzdXdwtl5BTHixEg0bNgpvdv==&size=w800_h700&format=jpeg',
       'http://io.zcbot.cn/wmc/image/common/?src_url=De0PGXC2NBWLd8TvNwTBTOjFKlWLdRzwnBP2GO9vVBYPdcjEkcjZNBpgGR9PTmIutHxvEJI8tJIMEHGFN85zEX68EmIFkBdWE8kyTssPTXEwEwTvdm9bEOEhdlVbkgjhTO5FEX7WNgpvdv==&size=w800_h700&format=jpeg',
       'http://io.zcbot.cn/wmc/image/common/?src_url=De0PGXC2NBWLd8TvNwTBTOjFKlWLdRzwnBP2GO9vVBYPdcjEkcjZNBpgGR9PTmIuEH5RERIRtJIMEw5vN8azE85MTRIFkBdWE8kyTxsBk8jWkwrRdJI8tHaykwkREwbbk8sFTwsPNgpvdv==&size=w800_h700&format=jpeg',
       'http://io.zcbot.cn/wmc/image/common/?src_url=De0PGXC2NBWLd8TvNwTBTOjFKlWLdRzwnBP2GO9vVBYPdcjEkcjZNBpgGR9PTmIPtH6uTmIMtmIRTXxyN85RtHaBERIFkBdWE8kyTxsRTH6udHYwEhI8TXG8T8aRT8audgsFtXiwNgpvdv==&size=w800_h700&format=jpeg']

