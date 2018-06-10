def parse_page1(self, response): 
    item = MyItem() 
    item['main_url'] = response.url 
    request = scrapy.Request("http://www.example.com/some_page.html", callback=self.parse_page2) 
    request.meta['item'] = item 
    return request 
def parse_page2(self, response): 
    item = response.meta['item'] 
    item['other_url'] = response.url 
    return item