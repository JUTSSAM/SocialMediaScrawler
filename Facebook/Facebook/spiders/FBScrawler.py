# -*- coding: utf-8 -*-
from datetime import datetime

import scrapy
from scrapy.loader import ItemLoader

from Facebook.Facebook.items import FbCrawlItem


class FbscrawlerSpider(scrapy.Spider):
    name = 'FBScrawler'
    allowed_domains = ['www.facebook.com', 'mbasic.facebook.com']
    start_urls = [
        'https://mbasic.facebook.com'
    ]

    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formxpath='//form[contains(@action, "login")]',
            formdata={'email': '79263866439', 'pass': 'JbZCuwkTdu'},
            callback=self.parse_index
        )

    def parse_index(self, response):
        if response.xpath("//div/a[contains(@href,'save-device')]"):
            self.logger.info('save device checkpoint')
            return scrapy.FormRequest.from_response(
                response,
                formdata={'name_action_selected': 'dont_save'},
                callback=self.parse_index
            )

        href = response.urljoin('vincentchengwingshun')
        self.logger.info('Scrapying facebook page {}'.format(href))
        return scrapy.Request(url=href, callback=self.parse_page, meta={'index': 1})

    def parse_page(self, response):
        for post in response.xpath("//div[contains(@data-ft,'top_level_post_id')]"):
            features = post.xpath('./@data-ft').get()
            from SpiderMan.items import parse_feature
            re = parse_feature(features)
            current_time = datetime.fromtimestamp(re['publish_time']) if 'publish_time' in re.keys() else None
            print(current_time)

            new = ItemLoader(item=FbCrawlItem(), selector=post)
            # 评论
            new.add_xpath('comments', './div[2]/div[2]/a[1]/text()')
            # 发布时间
            new.add_value('date', current_time)
            # id
            new.add_xpath('post_id', './@data-ft')
            # 完整链接
            new.add_xpath('url', ".//a[contains(@href,'footer')]/@href")

            post = post.xpath(".//a[contains(@href,'footer')]/@href").extract()
            tmp_post = response.urljoin(post[0])
            yield scrapy.Request(tmp_post, self.parse_post, meta={'item': new})

            new_page = response.xpath(
                "//div[2]/a[contains(@href,'timestart=') and not(contains(text(),'ent')) and not(contains(text(),number()))]/@href").extract()
            if new_page:
                print('more', new_page)
            else:
                xpath = "//div/a[contains(@href,'time') and contains(text(),'2019')]/@href"
                new_page = response.xpath(xpath).extract()
                print('this year', new_page)

    def parse_post(self, response):
        self.log(response.meta['item'])
        new = ItemLoader(item=FbCrawlItem(), response=response, parent=response.meta['item'])
        new.add_xpath('source',
                      ".//td/div/h3/strong/a/text() | //span/strong/a/text() | //div/div/div/a[contains(@href,'post_id')]/strong/text()")
        new.add_xpath('shared_from',
                      "//div[contains(@data-ft,'top_level_post_id') and contains(@data-ft, '\"isShare\":1')]")

        new.add_xpath('text', '//div[@data-ft]//p//text() | //div[@data-ft]/div[@class]/div[@class]/text()')
        check_reactions = response.xpath("//a[contains(@href, 'reaction/profile')]/div/div/text()").get()
        if not check_reactions:
            yield new.load_item()
        else:
            new.add_xpath('reactions', "//a[contains(@href,'reaction/profile')]/div/div/text()")
            reactions = response.xpath("//div[contains(@id,'sentence')]/a[contains(@href,'reaction/profile')]/@href")
            reactions = response.urljoin(reactions[0].extract())
            yield scrapy.Request(reactions, callback=self.parse_reactions, meta={'item': new})

    def parse_reactions(self, response):
        new = ItemLoader(item=FbCrawlItem(), response=response, parent=response.meta['item'])
        new.context['lang'] = 'zh'
        new.add_xpath('likes', "//a[contains(@href, 'reaction_type=1')]/span/text()")
        new.add_xpath('ahah', "//a[contains(@href, 'reaction_type=4')]/span/text()")
        new.add_xpath('love', "//a[contains(@href, 'reaction_type=2')]/span/text()")
        new.add_xpath('wow', "//a[contains(@href, 'reaction_type=3')]/span/text()")
        new.add_xpath('sigh', "//a[contains(@href, 'reaction_type=7')]/span/text()")
        new.add_xpath('grrr', "//a[contains(@href, 'reaction_type=8')]/span/text()")
        yield new.load_item()
