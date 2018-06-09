
import scrapy
import datetime
import urllib
import time
from cnkiScrapy.items import CnkiscrapyItem
from cnkiScrapy.items import CnkidetailItem
import re

class CNKISipder(scrapy.Spider):
    name = "cnki"

    # create request url, schedule parameter， use get_url() get final url
    # 2. generate the first request
    def createUrls(self):

    # 1. set parameter
        year_from = '2002-1-1'
        yeat_to = '2008-12-31'
        magazine_value1 = '浙江日报'
        txt_1_value1 = '习近平'
        # time
        GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
        now = datetime.datetime.utcnow().strftime(GMT_FORMAT)

        urls = []
        search_parameters = {
            'action': '',
            'NaviCode': '*',
            'ua': '1.21',
            'PageName': 'ASP.brief_result_aspx',
            'DbPrefix': 'SCDB',
            'DbCatalog': '中国学术文献网络出版总库',
            'ConfigFile': 'SCDB.xml',
            'db_opt': 'CJFQ,CDFD,CMFD,CPFD,IPFD,CCND,CCJD',
            'magazine_value1': magazine_value1, # could change
            'magazine_special1': '%',
            'publishdate_from': year_from,
            'publishdate_to': yeat_to,
            'txt_1_sel': 'SU',
            'txt_1_value1': txt_1_value1,
            'txt_1_relation': '#CNKI_AND',
            'txt_1_special1': '=',
            'his': '0',
            '_': now
        }
        origin_url =  "http://kns.cnki.net/kns/request/SearchHandler.ashx"
        url = self.get_url(origin_url, search_parameters)
        urls.append(url)
        return urls

    # compose url
    def get_url(self, origin_url, parameters):
        act_url = origin_url + "?"
        for key in parameters.keys():
            act_url = act_url + key + "=" + urllib.request.quote(str(parameters[key])) + "&"
        act_url = act_url.strip("&")
        return act_url

    # 3. send a request
    def start_requests(self):
        headers_parameters = {
            'Host': 'kns.cnki.net',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
            'Referer': 'http://kns.cnki.net/kns/brief/result.aspx?dbprefix=scdb'
        }
        urls = self.createUrls()
        for i, url in enumerate(urls):
            # send a request; callback the second request
            # meta={'cookiejar': i} 保存的是 cookie 用于保持持久性连接
            yield scrapy.Request(url, meta={'cookiejar': i}, callback=self.result_page, headers=headers_parameters)
    # the second request with result page
    def result_page(self, response):
        KeyValue = '习近平'
        selectField = '主题'
        # time
        t = int(round(time.time() * 1000))
        result_parameters = {'pagename': 'ASP.brief_result_aspx', 'DbPreFix': 'SCDB', 'dbCatalog': '中国学术文献网络出版总库', 'ConfigFile': 'SCDB.xml', 'Research': 'off',
                             't': t,'KeyValue': KeyValue, 'S': '1',  'recordsperpage': '50', "sorttype": "(被引频次,'INTEGER') desc"}
        origin_url = "http://kns.cnki.net/kns/brief/brief.aspx"
        act_url = self.get_url(origin_url, result_parameters)
        return scrapy.Request(act_url,
                              meta={'cookiejar': response.meta['cookiejar']},
                              callback=self.parse, dont_filter=True)

    # extract data
    # 1. define Items container which was provided by Scrapy to save data some-like dictionary-like API and define words
    # 2. extract data

    def parse(self, response):
        # define list
        itemList = []

        detailItems = CnkidetailItem()
        for result in response.css('tr[bgcolor]'):
            # TODO link
            item = CnkiscrapyItem()
            # items page
            item['title'] = result.css("td:nth-child(2) > a::text").extract_first()
            item['author'] = result.css("td.author_flag > a::text").extract_first()
            item['source'] = result.css("td:nth-child(4) > a > font::text").extract_first()
            item['publicationDate'] = result.css("td:nth-child(5)::text").extract_first()
            # items['referenceNum'] = result.css("span[class=KnowledgeNetcont] > a::text").extract_first()
            # items['downloadNum'] = result.css("span[class=downloadCount] > a::text").extract_first()
            item['detailLink'] = response.urljoin(result.css("td:nth-child(9) > a::attr(href)").extract_first())

            itemList.append(item)
        # enter into detail page call back
        # 遍历items_1天津爱了所有的分类
        for item in itemList:
            # loop the list, callback parse_detail, meta将这一层的数据传递到下一层
            yield  scrapy.Request(url= item['detailLink'], meta = {'item_1': item}, callback= self.parse_detail)

        # enten next page
        next_page = response.xpath("//div/a[text()='下一页']/@href").extract()
        if next_page:
            next_page = response.urljoin(next_page[0])
            yield scrapy.Request(next_page, meta={'cookiejar': response.meta['cookiejar']}, callback=self.parse,
                                 dont_filter=True)
    # scrape detail page
    def parse_detail(self, response):
        # pdfDownLink = response.css("#mainContent > div > div.head_cdmd > div:nth-child(2) > span:nth-child(1) > a:nth-child(3)::attr(href)").extract_first()
        # print("pdfDownLink ==== >", pdfDownLink)
        # return pdfDownLink
        item = response.meta["item_1"]
        pdfDownLink = response.urljoin(response.css("#mainContent > div > div.head_cdmd > div:nth-child(2) > span:nth-child(1) > a:nth-child(3)::attr(href)").extract_first())
        item["pdfDownLink"] = pdfDownLink
        #TODO pdf convert txt
        yield item