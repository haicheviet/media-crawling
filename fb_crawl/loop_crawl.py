self.logger.info('Scraping facebook page {}'.format(self.page))
print(self.page)
post_list = np.load("{self.page}")
for i in tqdm(post_list):
    new = ItemLoader(item=FbcrawlItem())
    new["comments"] = None
    new["date"] = i["date"]
    new["url"] = i["url_link"]
    new["post_id"] = i["post_id"]


    temp_post = i["url_link"]
    yield scrapy.Request(
            temp_post, self.parse_post, priority=self.count, meta={"item": new}
        )
