
import scrapy
import datetime
import urllib
import time
from cnkiScrapy.items import CnkiscrapyItem
from cnkiScrapy.items import CnkidetailItem

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
        # vadlid code
        # if "rurl" in str(requests_url):
        #     iden_code_url = str(requests_url).split("GET")[1].split(">")[0].strip()
        #     yield scrapy.Request(iden_code_url, meta={'cookiejar': response.meta['cookiejar']},
        #                          callback=self.handleCode, dont_filter=True)

        items = CnkiscrapyItem()
        detailItems = CnkidetailItem()
        for result in response.css('tr[bgcolor]'):
            # TODO link
            # items['title'] = result.css("td > a[class=fz14]").xpath("string(.)").extract_first()
            # items['author'] = result.css("td[class=author_flag] > a[class=KnowledgeNetLink]::text").extract()
            # items['source'] = result.css("td >a[target=_blank > font[class=Mark]]::text").extract_first()
            # # ctl00 > table > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(2) > td:nth-child(5)
            # items['publicationDate'] = result.css("td > table > tbody > tr:nth-child(2) > td:nth-child(5)::text").extract_first()
            # # ctl00 > table > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(2) > td:nth-child(6)
            # items['dateBase'] = result.css('td > table > tbody > tr:nth-child(2) > td:nth-child(6)::text').extract_first()
            # items['referenceNum'] = result.css("span[class=KnowledgeNetcont] > a::text").extract_first()
            # items['downloadNum'] = result.css("span[class=downloadCount] > a::text").extract_first()

            # items page
            # items['title'] = result.css("td > a[class=fz14]").xpath("string(.)").extract_first()
            # items['link'] = result.css("td > a[class=fz14]::attr(href)").extract_first()
            # items['author'] = result.css("td[class=author_flag] > a[class=KnowledgeNetLink]::text").extract()
            # # items['source'] = result.css("td[class=cjfdyxyz]").xpath("string(a)").extract_first()
            # # items['publicationDate'] = result.css("td[align] > a[target=_blank]::text").extract_first().split("/")[0]
            # items['referenceNum'] = result.css("span[class=KnowledgeNetcont] > a::text").extract_first()
            # items['downloadNum'] = result.css("span[class=downloadCount] > a::text").extract_first()
            # yield items

            # enter into detail page
            items['link'] = result.css("td > a[class=fz14]::attr(href)").extract_first()
            yield response.follow(items['link'], self.parse_detail)

        next_page = response.xpath("//div/a[text()='下一页']/@href").extract()
        if next_page:
            next_page = response.urljoin(next_page[0])
            yield scrapy.Request(next_page, meta={'cookiejar': response.meta['cookiejar']}, callback=self.parse,
                                 dont_filter=True)
    def parse_detail(self, response):
        def extract_with_css(query):
            return response.css(query).extract_first()
        yield {
            'title': extract_with_css('h2.title::text'),
            'author': extract_with_css('div.author span a::text'),
            'reference-title': extract_with_css('div.wxInfo > div.wxBaseinfo > p:nth-child(1)::text'),
            'sub-reference-title': extract_with_css('div.wxInfo > div.wxBaseinfo > p:nth-child(2)::text'),
            'intro': extract_with_css('#ChDivSummary::text'),
            'publicationDate': extract_with_css('div.wxInfo > div.wxBaseinfo > p:nth-child(4)::text'),
            'pdfLink': extract_with_css('#pdfDown')
        }