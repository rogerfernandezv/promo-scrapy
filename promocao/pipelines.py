# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem

class PromocaoPipeline(object):
	def process_item(self, item, spider):
		if item['cod_prom']:
			if item['nm_prom']:
				if item['url_prom']:
					return item
		else:
			DropItem("Sem codigo em %s" % item)
