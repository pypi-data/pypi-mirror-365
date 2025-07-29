#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2025-02-05 13:12
# @Author  :   oscar
# @Desc    :   None
"""
import asyncio
from crawlo.crawler import CrawlerProcess

# from crawlo.utils import system as _
from tests.baidu_spider.spiders.bai_du import BaiDuSpider
from crawlo.utils.project import get_settings
from tests.baidu_spider.spiders.sina import SinaSpider


async def main():
    settings = get_settings()
    process = CrawlerProcess(settings)
    # await process.crawl(BaiDuSpider)
    await process.crawl(SinaSpider)

    await process.start()

if __name__ == '__main__':
    asyncio.run(main())
    # 观看到第18集
