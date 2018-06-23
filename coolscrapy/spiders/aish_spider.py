#encoding:utf-8
"""
Topic: sample
Desc :
"""
from coolscrapy.items import HuxiuItem
import traceback
import scrapy
import re
from scrapy_splash import SplashRequest


def filter_tags(htmlstr):
    #先过滤CDATA
    htmlstr = str(htmlstr)
    re_cdata=re.compile('//<!\[CDATA\[[^>]*//\]\]>',re.I) #匹配CDATA
    re_script=re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>',re.I)#Script
    re_style=re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>',re.I)#style
    re_br=re.compile('<br\s*?/?>')#处理换行
    re_h=re.compile('</?\w+[^>]*>')#HTML标签
    re_comment=re.compile('<!--[^>]*-->')#HTML注释
    s=re_cdata.sub('',htmlstr)#去掉CDATA
    s=re_script.sub('',s) #去掉SCRIPT
    s=re_style.sub('',s)#去掉style
    s=re_br.sub('\n',s)#将br转换为换行
    s=re_h.sub('',s) #去掉HTML 标签
    s=re_comment.sub('',s)#去掉HTML注释
    #去掉多余的空行
    blank_line=re.compile('\n+')
    s=blank_line.sub('\n',s)
    s=replaceCharEntity(s)#替换实体
    return s

def replaceCharEntity(htmlstr):
    CHAR_ENTITIES={'nbsp':' ','160':' ',
                'lt':'<','60':'<',
                'gt':'>','62':'>',
                'amp':'&','38':'&',
                'quot':'"','34':'"',}

    re_charEntity=re.compile(r'&#?(?P<name>\w+);')
    sz=re_charEntity.search(htmlstr)
    while sz:
        entity=sz.group()#entity全称，如&gt;
        key=sz.group('name')#去除&;后entity,如&gt;为gt
        try:
            htmlstr=re_charEntity.sub(CHAR_ENTITIES[key],htmlstr,1)
            sz=re_charEntity.search(htmlstr)
        except KeyError:
            #以空串代替
            htmlstr=re_charEntity.sub('',htmlstr,1)
            sz=re_charEntity.search(htmlstr)
    return htmlstr

def repalce(s,re_exp,repl_string):
    return re_exp.sub(repl_string,s)

class AishSpider(scrapy.Spider):
    name = "aish"
    allowed_domains = [""]
    start_urls = [
    ]

    def start_requests(self):
        splash_args = {
            'wait': 0.5,
            'splash_url': 'localhost:8050'
        }
        for url in self.start_urls:
            USER_AGENT = "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36"

            headers = {"User-Agent": USER_AGENT}
            #yield scrapy.Request(url, callback=self.parse, headers=headers)
            #yield scrapy.Request(url, callback=self.parse)
            yield SplashRequest(url, self.parse, endpoint='render.html',
                                args=splash_args)


    def parse(self, response):
        for sel in response.xpath('//div[@class="mn"]//div[@class="fl bm"]//div[@class="bm bmw  cl"]//tbody/tr/td/h2'):
            try:
                tmp = sel.xpath('a/@href').extract_first()
                url = response.urljoin(tmp)
                tmp = sel.xpath('a/text()').extract_first()
                if tmp not in allow_part:
                    continue
                yield scrapy.Request(url, callback=self.parse_list)
            except Exception as err:
                print('Exception occurred', traceback.format_exc())
                print(err)

    def parse_list(self, response):
        for sel in response.xpath('//div[@class="mn"]//div[@class="bm_c"]//tbody[contains(@id,"normalthread")]//th[@class="new"]'):
            try:
                tmp = sel.xpath('a[@class="s xst"]/text()').extract_first()
                tmp = sel.xpath('a[@class="s xst"]/@href').extract_first()
                new_url = response.urljoin(tmp)
                yield scrapy.Request(new_url, callback=self.parse_content)
            except:
                pass
        try:
            max_page = response.xpath('.//div[@class="mn"]//a[@class="bm_h"]/@totalpage').extract_first()
            if max_page:
                max_page = int(max_page)
                url_parse = response.url.split('-')
                tmp = url_parse[-1].split('.')
                page = int(tmp[0])
                other = '.'.join(tmp[1:])
                if page < max_page:
                    page += 1
                    new_url = '-'.join(url_parse[:-1]) + '-' + str(page) + '.' + other
                    yield scrapy.Request(new_url, callback=self.parse_list, dont_filter=True)
        except:
            print('Exception occurred', traceback.format_exc())
            pass

    def parse_content(self, response):
        try:
            tmp = response.xpath('//div[@class="bm cl"]/div[@class="z"]/a[@href]//text()').extract()
            if tmp:
                first = tmp[2].strip()
                second = tmp[3].strip()
                title = tmp[4].strip()
            #tmp = '\t'.join(response.xpath('//div[@class="wp cl"]//div[@class="pl c"]')[0].xpath('//blockquote/text()').extract()[0])
            #tmp = response.xpath('//div[@class="pl bm"]//div[@class="pl hin"]//tbody').extract()
            tmp = filter_tags(response.xpath('//div[@class="pl bm"]//table[@class="plhin"]//td[@class="t_f"]//blockquote').extract_first()).strip().replace('\n', '').replace('\xa0',' ')
            if tmp:
                item = HuxiuItem()
                content = tmp.strip().split('\r')
                #print('============================')
                #print(content)
                item['first'] = first
                item['second'] = second
                item['title'] = title
                item['content'] = content
                item['url'] = str(response.request.url).strip()
                return item
        except Exception as err:
            print(tmp)
            print('Exception occurred', traceback.format_exc())
            print(err)
            pass
