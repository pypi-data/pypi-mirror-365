"""
电商罗盘-商品
"""

from time import sleep
from typing import Callable

from BrowserAutomationLauncher import Browser, DataPacketProcessor
from BrowserAutomationLauncher._utils.tools import DateTimeTools
from DrissionPage._pages.mix_tab import MixTab

from ._utils import pick__daterange


class Urls:
    goods_detail = (
        'https://compass.jinritemai.com/shop/product-detail?product_id={goods_id}'
    )


class DataPacketUrls:
    goods_detail = 'https://compass.jinritemai.com/compass_api/shop/product/product_detail/core_data/index_data'


class Goods:
    def __init__(self, browser: Browser):
        self._browser = browser

    def _wait__goods_detail_datapacket(
        self, page: MixTab, callback: Callable, timeout=15
    ):
        """等待商品详情数据包"""

        page.listen.start(
            targets=DataPacketUrls.goods_detail, method='GET', res_type='XHR'
        )
        callback()
        return page.listen.wait(timeout=timeout)

    def get__goods_detail(self, goods_id: str, begin_date: str, end_date: str):
        """
        获取指定商品详情

        Args:
            goods_id: 商品ID
            begin_date: 开始日期
            end_date: 结束日期
        """

        url = Urls.goods_detail.format(goods_id=goods_id)
        page = self._browser.chromium.new_tab()
        if not self._wait__goods_detail_datapacket(page, lambda: page.get(url)):
            raise TimeoutError('进入页面后获取商品详情数据包超时')

        is_yesterday = begin_date == end_date == DateTimeTools.date_yesterday()
        sleep(2)

        if is_yesterday:
            yesterday_btn = page.ele('近1天', timeout=3)
            datapacket = self._wait__goods_detail_datapacket(
                page, lambda: yesterday_btn.click(by_js=True)
            )
        else:
            datapacket = self._wait__goods_detail_datapacket(
                page, lambda: pick__daterange(page, begin_date, end_date)
            )

        if not datapacket:
            raise TimeoutError('修改日期后获取数据包超时')

        data = DataPacketProcessor(datapacket).filter(['attributes', 'data[0].metrics'])

        titles = {
            item['index_name']: item['index_display'] for item in data['attributes']
        }

        metrics = {}
        for key, data_dict in data['metrics'].items():
            if 'value' not in data_dict:
                continue

            value_dict = data_dict['value']
            if not isinstance(value_dict, dict):
                continue

            value = value_dict.get('value')
            unit = value_dict.get('unit')

            if unit == 'price' and isinstance(value, (int, float)):
                value = value / 100

            metrics[key] = value

        data_list = {name: metrics[key] for key, name in titles.items()}

        return data_list
