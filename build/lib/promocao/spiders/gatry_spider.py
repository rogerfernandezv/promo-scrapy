import scrapy
from promocao.items import PromocaoItem
from datetime import datetime
from pytz import timezone
import re

class GatrySpider(scrapy.Spider):
	name = 'gatry'
	start_urls = [
		"https://gatry.com"
	]

	def parse(self, response):
		promocoes_url = response.xpath('//article[contains(@class,"promocao")]')
		for promocao_url in promocoes_url:
			url = response.urljoin(promocao_url.xpath(".//div[@class='informacoes']/p[@class='opcoes']/a[ re:test(@class,'mais hidden.*')]/@href").extract_first())
			yield scrapy.Request(url, callback=self.parse_contents)

	def parse_contents(self, response):

		#instanciando Items
		promo = PromocaoItem()

		#fixed values
		promo['name'] = self.name
		promo['dt_criacao'] = datetime.now(timezone('America/Sao_Paulo')).strftime("%Y-%m-%d %H:%M:%S")
		promo['url_origem'] = response.url
		
		#areaMainContent
		mainContent = response.xpath('//main[ contains(@class,"content") ]')

		#areaMainContent -> areaPromocao
		promocao = mainContent.xpath('.//article[contains(@class,"promocao")]')

		promo['cod_prom'] = promocao.xpath('@id').re_first(r'\d+')
		if(promo['cod_prom']):
				promo['cod_prom'] += "_" + self.name

		promo['url_img'] = promocao.css('.imagem a img::attr(src)').extract_first()
		data = promocao.xpath('.//p[contains(@class,"opcoes")]/span[contains(@class,"data_postado")]/@title').extract_first()
		data = re.sub(r'[^\d\/\:\s]','',data)
		data = re.sub(r'\s{2,20}',' ',data)
		promo['data_prom'] = data

		#areaPromocao -> areaInformacoes
		areaInformacoes = promocao.xpath('.//div[@class="informacoes"]')
		promo['nm_prom'] = areaInformacoes.xpath('h3/a/text()').extract_first()
		promo['url_prom'] = areaInformacoes.xpath('h3/a/@href').extract()
		promo['valor'] = areaInformacoes.xpath("p[@class='preco']/span[@itemprop='price']/text()").extract_first()
		
		#areaMainContent -> areaComentarios
		areaComentarios = mainContent.xpath(".//section[ contains(@class,'comentarios') ]")
		promo['nm_obs'] = areaComentarios.xpath("ul/li/div[ contains(@class,'box-content-comentario') ]/p/text()").extract_first()

		yield promo
