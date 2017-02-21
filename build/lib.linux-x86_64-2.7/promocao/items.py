# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PromocaoItem(scrapy.Item):
    # define the fields for your item here like:
	cod_prom = scrapy.Field() #id exclusivo para items ou juncao de outros dados
	nm_prom = scrapy.Field() # conteudo da promocao
	url_prom = scrapy.Field() # url da promocao
	url_origem = scrapy.Field() # url de onde veio a prom(gatry, hardmob, etc)
	name = scrapy.Field() # nome do spider
	url_img = scrapy.Field() # url da imagem
	data_prom = scrapy.Field() #data que foi publicado
	valor = scrapy.Field() # preco descrito no site se possivel
	nm_obs = scrapy.Field() # descrição adicional(geralmente infos como cupoms e instruções)
	dt_criacao = scrapy.Field() # dia da captura
