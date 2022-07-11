# -*- coding: utf8 -*-
import csv
import requests
from bs4 import BeautifulSoup
import lxml
import re
from time import sleep
import pymysql.cursors
import os
from PIL import ImageOps
from PIL import Image
import datetime
from ftplib import FTP
# import get_urls_domofond

def get_html(url):
	with requests.Session() as se:
		se.headers = {
	        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.175 Safari/537.36",
	        "Accept-Encoding": "gzip, deflate",
	        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
	        "Accept-Language": "ru"
	    }
	r = se.get(url)
	print(r.text)
	return r.text



def flat_filter(html, url):

	
	soup = BeautifulSoup(html, 'lxml')
	# print(soup)
	num = soup.find('div', class_='saller-information__root___3z-HR').find_all('div', class_='saller-information__line___1CP8j')
	num = num[1].text
	num = num.split(':')[1].strip()
	if int(num) < 5:
		adress = soup.find('a', class_='information__address___1ZM6d').text
		city = adress.split(', ')[-1]
		print(adress)
		if city == 'Санкт-Петербург':
			street = adress.split(', ')[-4]
			if 'Санкт-Петербург' in street:
				street = adress.split(', ')[-3]
				house = adress.split(', ')[-2]
			house = adress.split(', ')[-3]
			if 'стр.' in house:
				street = adress.split(', ')[-5]
				house = adress.split(', ')[-4] + ' ' + adress.split(', ')[-3]
			if 'корп.' in house:
				street = adress.split(', ')[-5]
				house = adress.split(', ')[-4] + ' ' + adress.split(', ')[-3]		
			if 'подъезд' in house:
				street = adress.split(', ')[-5]
				house = adress.split(', ')[-4]
		elif city == 'Ленинградская область':
			town = adress.split(', ')[-2]

		address = 'Санкт-Петербург, ' + street + ', ' + house

		try:
			discript = soup.find('h5', class_='description__title___2N9Wk').text 
			discript = discript.split(', ')
		except:
			try:
				discript = soup.find('h5', class_='description__title___2N9Wk').text 
				discript = discript.split(', ')
			except:
				try:
					discript = soup.find('h5', class_='description__title___2N9Wk').text 
					discript = discript.split(', ')
				except:
					print('shit')
		flat_type = discript[0]
		total_s = discript[1]
		total_s = total_s.split( )[0]
		living_space = float(total_s)*0.5
		floor = discript[2]
		floor = floor.split( )[0]
		floor = floor.split('/')
		total_f = floor[1]
		floor = floor[0]
		discription = soup.find('div', class_='description__description___2FDOM').text
		price = soup.find('div', class_='information__price___2Lpc0').text
		price = price.split( )
		price = price[:-1]
		price = price[0]+price[1]+price[2]
		price = int(price) + 100000
		
		ids = url.split('-')[-1].strip()
		
		if flat_type == '1-комн. квартира':
		#тип квартиры - 1 комнатная
			room = 'однокомнатная квартира'

		elif flat_type == 'Квартира-студия':
		#тип квартиры - студия
			room = 'квартира-студия'

		elif flat_type == '2-комн. квартира':
		#тип квартиры - 2 комнатная
			room = 'двухкомнатная квартира'
								
		elif flat_type == '3-комн. квартира':
		#тип квартиры - 3 комнатная
			room = 'трехкомнатная квартира'

		description = 'Id объекта - ' + str(ids) + ' Продается ' + room + '. Общая площадь - ' + str(total_s) + ' кв.м. Квартира расположена на ' + str(floor) + ' этаже ' + str(total_f) + '-этажного дома. Просмотры по договоренности. Подробности по телефону. Просьба звонить с 10-00 до 20-00.'
		creation_date = datetime.datetime.now().isoformat()
		# создаем папку под фотографии
		folder = str('c://Python37//SELL_XML//'+str(ids)+'//')
		os.makedirs(folder)

		connection = pymysql.connect(host='mysql.9967724406.myjino.ru',
								user='047077889_xml',
								password='Xedfr@123',
								db='9967724406_sel-xml',
								charset='utf8mb4',
								cursorclass=pymysql.cursors.DictCursor)	



		try:
			with connection.cursor() as cursor:
				sql = "INSERT INTO flats (ids, address, flat_type, area, floor, total_f, description, price, street, house, num) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

				# Выполнить команду запроса (Execute Query).
				cursor.execute(sql, (ids, address, flat_type, total_s, floor, total_f, description, price, street, house, num))
			connection.commit() 



		finally:
		# Закрыть соединение (Close connection).      
			connection.close()

	return(ids)

def get_all_links(html, fold): # вытаскивает в список url фотографий
	re_links = []
	ret_links = []
	tt = '1280x960'
	ii = 0
	soup = BeautifulSoup(html, 'lxml')
	html_text = soup.get_text()
	text_galery = html_text.split('''galleries":[{''') #разбили текст страницы на две части. Во второй части остались ссылки на картинки, а в первой ссылки на "похожие квартиры"
	text1=text_galery[1]
	text = text1.split('''"url":''')
	for i in text:
		link = i.split('"}')
		if tt in link[0]:
			fix_link = link[0]
			fix_link = fix_link[1:]
			re_links.append(fix_link)
	

	# скачивает и обрезает фотографии
	for line in re_links:
		# print(line)

		ids = fold.split('-')
		ids = ids[-1]
		ids = ids[0:-1]		

		url = str(line)
		ii=ii+1
		r = requests.get(line, stream=True)
		# try:	
		with open('c:\\Python37\\SELL_XML\\'+str(ids)+'\\'+str(ii)+'.jpg', 'bw') as f:
		
			for chunk in r.iter_content(8192):
				f.write(chunk)	

		img = Image.open('c:\\Python37\\SELL_XML\\'+str(ids)+'\\'+str(ii)+'.jpg')
		border = (0, 60, 0, 0)
		img = ImageOps.crop(img, border)
		img.save('c:\\Python37\\SELL_XML\\' + str(ids) + '\\' +str(ii)+'.jpg')
	print ('Объявление - '+ str(ids) + ' загружено')

		# except OSError:
		# 	print('Error')



def main():

	# get_urls_domofond.main()

	# folder = 0
	# tor = 0
	f = open('url.txt')
	for line in f:
		flat_filter(get_html(line), line)
		# all_img_links = get_all_links(get_html(line), line)
		try:
			# print()
			# print(line)
			try:
				flat_filter(get_html(line), line)
			except:
				print('Еще разок')
				try:
					flat_filter(get_html(line), line)
				except:
					print('Последняя попытка')
					flat_filter(get_html(line), line)
	
			all_img_links = get_all_links(get_html(line), line)
		except:
			print('Объявление ' + line + 'не удалось загрузить')




main()