# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import Join


class FbCrawlItem(scrapy.Item):
    source = scrapy.Field()
    date = scrapy.Field()
    text = scrapy.Field(
        output_processor=Join(separator=u'')
    )
    comments = scrapy.Field()
    reactions = scrapy.Field()
    likes = scrapy.Field()
    ahah = scrapy.Field()
    love = scrapy.Field()
    wow = scrapy.Field()
    sigh = scrapy.Field()
    grrr = scrapy.Field()
    share = scrapy.Field()
    url = scrapy.Field()
    post_id = scrapy.Field()
    shared_from = scrapy.Field()
