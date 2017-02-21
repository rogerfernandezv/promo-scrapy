import scrapy
import re
from promocao.items import PromocaoItem
from datetime import date
from datetime import datetime
from pytz import timezone

class HardmobSpider(scrapy.Spider):
	name = 'hardmob'
	start_urls = [
		"http://www.hardmob.com.br/promocoes/"
	]
	

	def parse(self, response):
		listLink = response.xpath('//ol[contains(@id,"threads")]/li[ contains(@id,"thread") ]')
		for link in listLink:
			url = response.urljoin(link.xpath(".//a[ re:test(@id,'thread_title.*')]/@href").extract_first())
			yield scrapy.Request(url, callback=self.parse_contents)

	def parse_contents(self, response):
		hoje = datetime.now(timezone('America/Sao_Paulo'))
		ontem = date.fromordinal(hoje.toordinal()-1)

		#instanciando Items
		promo = PromocaoItem()

		# valores fixos e/ou atributos da pagina
		promo['name'] = self.name
		promo['url_origem'] = response.url
		promo['dt_criacao'] =  datetime.now(timezone('America/Sao_Paulo')).strftime("%Y-%m-%d %H:%M:%S")

		#areaPromocao
		areaPromocao = response.xpath('//div[ contains(@id,"postlist") ]/ol[ contains(@id,"posts") ][1]/li[1]')
		
		if(areaPromocao):
			#areaPromocao -> areaHEAD
			areaHead = areaPromocao.xpath('div[contains(@class,"posthead")][1]')
			promo['cod_prom'] = areaHead.xpath('span[contains(@class,"nodecontrols")]/a[1]/@href').re_first(r'promocoes\/(\d+)\-')
			if(promo['cod_prom']):
				promo['cod_prom'] += "_" + self.name

			# areaPromocao -> areaHEAD -> areaDATEeTIME
			areaData = areaHead.xpath('span[contains(@class,"postdate old")][1]')
			if(areaData):
				data = areaData.xpath('span[ contains(@class,"date") ]/text()').extract_first()
				data = re.sub(r'Ontem', ontem.strftime("%Y-%m-%d"), data)
				data = re.sub(r'Hoje', hoje.strftime("%Y-%m-%d"), data)
				hora = areaData.xpath('span[ contains(@class,"date") ]/span[ contains(@class,"time") ]/text()').extract_first()
				promo['data_prom'] = data + " " + hora

			# areaPromocao -> areaPost
			areaPost = areaPromocao.xpath('div[@class="postdetails"]/div[@class="postbody"][1]/div[@class="postrow has_after_content"][1]')
			
			# areaPromocao -> areaPost -> areaTitulo
			areaTitulo = areaPost.xpath('h2[ contains(@class,"title icon") ]')
			promo['nm_prom'] = areaTitulo.re_first(r'<img.*?>[\r\n]+(.*)')
			promo['valor'] = areaTitulo.re_first(r'<img.*?>[\r\n]+.*\-[\s]?([Rr]\$[\s]?\d+[\,\.]\d+)')
			if not(promo['valor']):
				promo['valor'] = areaTitulo.re_first(r'<img.*?>[\r\n]+.*\-[\s]?([Rr]\$[\s]?\d+\.\d+\,\d+)')
				if not(promo['valor']):
					promo['valor'] = areaTitulo.re_first(r'<img.*?>[\r\n]+.*\-[\s]?([Rr]\$[\s]?\d+)')
					if not(promo['valor']):
						promo['valor'] = areaTitulo.re_first(r'<img.*?>[\r\n]+.*por[\s]?([Rr]\$[\s]?\d+[\,\.]\d+)')


			# areaPromocao -> areaPost -> areaContent
			areaContent = areaPost.xpath('div[ contains(@class,"content") ][1]/div[1]/blockquote[ contains(@class,"postcontent restore") ][1]')
			obs = areaContent.xpath('normalize-space()').extract_first()
			obs = re.sub(r'http:\/\/.*?\s','',obs)
			obs = re.sub(r'(http:\/\/[^\s]+)$','',obs)
			obs = re.sub(r'(\/\*[\s]?<\!\[CDATA.*>[\s]?\*\/)','',obs)
			promo['nm_obs'] = obs
			promo['url_prom'] = areaContent.xpath('.//a[ not( re:test(@href,"(post\d+)$") ) ]/@href').extract()
			promo['url_img'] = areaContent.xpath('.//img[ not( re:test(@src,"(hardmob|smil[ie]|^\/|\.gif))"))]/@src').extract_first()


		yield promo
