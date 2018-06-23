# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import time

class CoolscrapyPipeline(object):
    def __init__(self):
        now_date = time.strftime("%Y%m%d")
        self.file = open('./data/%s_items.txt' %now_date, 'w')
        self.read_file = open('./read_data/%s_read.txt' %now_date, 'w')

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        self.read_file.write('============================================\n')
        for field, value in item.items():
            if field == 'content':
                for elem in value:
                    if not elem:
                        continue
                    self.read_file.write(elem + '\n')
            else:
                self.read_file.write('【'+field +'】:' + value + '\n')
        return item

    def close_spider(self):
        self.file.close()
        self.read_file.close()
