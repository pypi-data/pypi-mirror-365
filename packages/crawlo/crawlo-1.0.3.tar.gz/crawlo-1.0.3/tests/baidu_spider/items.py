#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2025-05-11 13:35
# @Author  :   oscar
# @Desc    :   None
"""
from crawlo.items import Field
from crawlo.items.items import Item


class BauDuItem(Item):
    url = Field()
    title = Field()


class ArticleItem(Item):
    article_id = Field()
    title = Field()
    digest = Field()
    short = Field()
    url = Field()
    tag = Field()
    ctime = Field()
    source = Field()
