import scrapy
from promocao.items import PromocaoItem
from datetime import datetime
from pytz import timezone
import re

class GatrySpider(scrapy.Spider):
	name = 'promobit'
	start_urls = [
		"https://www.promobit.com.br/"
	]

	def parse(self, response):
		promocoes_url = response.xpath('//div[contains(@class,"pr-tl-card")]')
		for promocao_url in promocoes_url:
			url = response.urljoin(promocao_url.xpath('.//a[ re:test(@href,"oferta")]/@href').extract_first())
			yield scrapy.Request(url, callback=self.parse_contents)

	def parse_contents(self, response):

		#instanciando Items
		promo = PromocaoItem()

		#fixed values
		promo['name'] = self.name
		promo['dt_criacao'] = datetime.now(timezone('America/Sao_Paulo')).strftime("%Y-%m-%d %H:%M:%S")
		promo['url_origem'] = response.url

		# areaPromocao
		#promocao = response.xpath('//div[contains(@class,"pr-of-prod pr-of-box")] [1]')
		promocao = response.xpath('//div[contains(@class,"pr-of-prod pr")] [1]')

		img = promocao.xpath('./div[contains(@class,"pr-of-prod-image")]/div/img/@src').extract_first()
		http_img = re.compile('http', re.I)
		if http_img.search(img):
			promo['url_img'] = img
		else:
			promo['url_img'] = 'https:' + img
		promo['nm_prom'] = promocao.xpath('//div[contains(@class,"pr-of-prod-info")]/h1/text()').extract_first()

		promo['valor'] = promocao.xpath('.//div[contains(@itemprop,"offers")]//span[contains(@itemprop,"lowPrice")]/text()').extract_first()
		
		cod = promocao.xpath('.//div[contains(@class,"pr-of-prod-fixed")]/a/@data-key').re_first(r'\/(\d+)\/')
		if not cod:
			cod = promocao.xpath('.//div[contains(@class,"pr-of-prod-fixed")]/a/@href').re_first(r'\/(\d+)\/')

		if not cod:
			cod = promocao.xpath('.//div[contains(@class,"pr-of-prod-fixed")]/a/@href').re_first(r'\/(\d+)')
		
		if(cod):
			promo['cod_prom'] = cod + "_" + self.name

		url_prom = promocao.xpath('.//div[contains(@class,"pr-of-prod-fixed")]/a/@data-key').extract()
		if not url_prom:
			url_prom = promocao.xpath('.//div[contains(@class,"pr-of-prod-fixed")]/a/@href').extract()
		
		for i in range(len(url_prom)):
			url_prom[i] = "https://www.promobit.com.br/Redirect/to/" + cod + "/"

		promo['url_prom'] = url_prom

		# areaInfo
		areaInformacoes = response.xpath('//div[contains(@class,"pr-of-info pr")] [1]')

		nm_obs = areaInformacoes.xpath('./div[contains(@class,"pr-of-info-container")]')
		promo['nm_obs'] = nm_obs.xpath('normalize-space()').extract_first()

		promo['data_prom'] = areaInformacoes.xpath('.//div[contains(@class,"pr-of-publisher-top")]/h4').re_first(r'em\s(\d+\/\d+\/\d+)')

		yield promo
