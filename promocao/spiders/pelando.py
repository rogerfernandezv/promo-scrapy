import scrapy
from promocao.items import PromocaoItem
from datetime import datetime
import datetime as dt
from pytz import timezone
import re

class GatrySpider(scrapy.Spider):
	name = 'pelando'
	start_urls = [
		"https://www.pelando.com.br/"
	]

	def parse(self, response):
		promocoes_url = response.xpath('//div[contains(@class,"fGrid-last")]/article[contains(@id,"thread_")]//strong/a[contains(@href,"oferta")]')

		for promocao_url in promocoes_url:
			url = promocao_url.xpath('./@href').extract_first()
			yield scrapy.Request(url, callback=self.parse_contents)

	def parse_contents(self, response):

		#instanciando Items
		promo = PromocaoItem()

		#fixed values
		promo['name'] = self.name
		promo['dt_criacao'] = datetime.now(timezone('America/Sao_Paulo')).strftime("%Y-%m-%d %H:%M:%S")
		promo['url_origem'] = response.url

		# areaPromocao
		promocao = response.xpath('//article[contains(@id,"thread_")] [1]')
		
		promo['url_img'] = promocao.xpath('.//p[contains(@class,"imgFrame imgFrame")]//img/@src').extract_first()
		#promo['nm_prom'] = promocao.xpath('//div[contains(@class,"boxSec")]/strong[contains(@class,"thread-title box")]/a/text()').extract_first()
		promo['nm_prom'] = promocao.xpath('.//div[contains(@class,"cept-thread-main")]/h1[contains(@class,"thread-title thread-title")]/span/text()').extract_first()
		
		#promo['valor'] = promocao.xpath('//span[contains(@class,"thread-price tGrid")]/text()').re_first(r'\d.*')
		promo['valor'] = promocao.xpath('//div[contains(@class,"voucher-code box--all-b")]/text()').re_first(r'\d.*')

		#cod = promocao.xpath('//div[contains(@class,"boxSec")]/strong[contains(@class,"thread-title box")]/a/@href').re_first(r'(\d+)$')
		cod = promocao.xpath('.//a[contains(@class,"cept-deal-cloak")][//span[contains(.,"Ir para")] ]/@href').re_first(r'(\d+)$')
		promo['cod_prom'] = cod + "_" + self.name
		#promo['url_prom'] = promocao.xpath('//div[contains(@class,"boxSec")]/strong[contains(@class,"thread-title box")]/a/@href').extract()
		promo['url_prom'] = promocao.xpath('.//a[contains(@class,"cept-deal-cloak")][//span[contains(.,"Ir para")] ]/@href').extract()

		#categoria = promocao.xpath('//div[contains(@class,"boxSec")]/a[contains(@class,"thread-category linkPlain")]/text()').extract_first()
		categoria = promocao.xpath('//div[contains(@class,"cept-thread-main")]/a[contains(@class,"thread-category linkPlain")]/text()').extract_first()
		
		#obs = promocao.xpath('//div[contains(@class,"thread-main page2-space")]//div[contains(@class,"userHtml")]')
		obs = promocao.xpath('//div[contains(@class,"cept-thread-content")]//div[contains(@class,"userHtml")]')
		promo['nm_obs'] = obs.xpath('normalize-space()').extract_first()

		data = promocao.xpath('//p/time[contains(@class,"mute--text")]/@datetime').extract_first()

		promo['data_prom'] = dt.date.fromtimestamp(int(data)).strftime('%d/%m/%Y')

		yield promo
