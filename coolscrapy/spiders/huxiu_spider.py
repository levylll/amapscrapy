"""
Topic: sample
Desc :
"""
from coolscrapy.items import HuxiuItem
import scrapy

class HuxiuSpider(scrapy.Spider):
    name = "huxiu"
    allowed_domains = ["ccret.org.cn"]
    start_urls = [
        #"http://www.huxiu.com/index.php"
        "http://www.ccret.org.cn/discuz/forum.php"
    ]

    # 在所有的请求发生之前执行
    def start_requests(self):
        for url in self.start_urls:
            headers = {"User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)"}
            yield scrapy.Request(url, callback=self.parse, headers=headers)

    def parse(self, response):
        for sel in response.xpath('//div[@class="bm_c"]//td/h2'):
            try:
                tmp = sel.xpath('a/@href').extract()[0]
                url = response.urljoin(tmp)
                tmp = sel.xpath('a/text()').extract()[0]
                yield scrapy.Request(url, callback=self.parse_list)
            except:
                pass

    def parse_list(self, response):
        for sel in response.xpath('//div[@class="bm_c"]//tbody/tr/th'):
            try:
                tmp = sel.xpath('a[@class="s xst"]/@href').extract()[0]
                new_url = response.urljoin(tmp)
                yield scrapy.Request(new_url, callback=self.parse_content)
            except:
                pass

    def parse_content(self, response):
        try:
            tmp = response.xpath('//div[@class="bm cl"]/div/a[@href]//text()').extract()
            if tmp:
                first = tmp[1].strip()
                second = tmp[2].strip()
                title = tmp[3].strip()
            tmp = ','.join(response.xpath('//div[@class="pl bm"]/div')[0].xpath('//td[@class="t_f"]/text()').extract())
            if tmp:
                item = HuxiuItem()
                content = tmp.strip()
                item['first'] = first
                item['second'] = second
                item['title'] = title
                item['content'] = content.replace('\n', '').replace('\r', '')
                item['url'] = str(response.request.url).strip()
                yield item
        except Exception as err:
            pass
