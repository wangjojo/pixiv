import requests
from bs4 import BeautifulSoup
import re,os
import easygui as g

class PixivSpider(object):
	def __init__(self,base_url_index = 0,referer_index = 0):
		self.base_url_index = base_url_index
		self.referer_index = referer_index

		self.base_url = ['https://www.pixiv.net/ranking_area.php?type=detail&no=6',
						'https://www.pixiv.net/ranking.php?mode=daily']

		self.referer = ['https://www.pixiv.net/ranking_area.php?type=detail&no=6',
						'https://www.pixiv.net/ranking.php?mode=daily'
						]
		self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
						'Referer':self.referer[self.referer_index],
						'Connection':'keep-alive'
						}

	#修改图片链接
	def change(self,url):
		r = r'2017.*p0'
		url = re.search(r,url).group()
		url = 'https://i.pximg.net/img-original/img/' + url + '.jpg'
		return url

	def get_html(self):
		#访问网页，返回国际排行榜页面源代码
		#检查网页是否访问成功
		response = requests.get(self.base_url[self.base_url_index],headers = self.headers)
	
		if str(response) == '<Response [200]>':
			return response.text
		else:
			print('error')

	#获取图片url
	def get_jpg_url(self):
		html = self.get_html()
		#使用bs解析页面

		soup = BeautifulSoup(html,'html.parser')
		url_list = soup.find_all('img',{'data-filter':"thumbnail-filter lazy-image"},src = re.compile('https'))
		jpg_list = []
		#修改图片链接
		for each in url_list:
			each = self.change(each['data-src'])
			jpg_list.append(each)
		return jpg_list

	#下载图片
	def download(self):
		jpg_list = self.get_jpg_url()
		for each in jpg_list:
			tupian = requests.get(each,headers = self.headers)
			#如果状态码不为200，则为png格式
			if str(tupian) == '<Response [200]>':
				filename = each.split('/')[-1]
				with open(filename,'wb') as f:
					f.write(tupian.content)
			else:
				each = each.replace('jpg','png')
				tupian = requests.get(each,headers = self.headers)
				filename = each.split('/')[-1]
				with open(filename,'wb') as f:
					f.write(tupian.content)

#爬取今日榜
class PixivSpider_daily(PixivSpider):
	"""docstring for PixivSpider_daily"""
	def __init__(self,datenums):
		super(PixivSpider_daily, self).__init__()
		self.daily_base_url = 'https://www.pixiv.net/ranking.php?mode=daily&date='
		self.datenums = datenums
		self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
						'Referer':'https://www.pixiv.net/ranking.php?mode=daily',
						'Connection':'keep-alive'
						}

	def get_html(self,url):
		#访问网页，返回国际排行榜页面源代码
		#检查网页是否访问成功
		response = requests.get(url,headers = self.headers)
	
		if str(response) == '<Response [200]>':
			return response.text
		else:
			print('error')

	def get_jpg_url(self,url):
		html = self.get_html(url)
		#使用bs解析页面

		soup = BeautifulSoup(html,'html.parser')
		url_list = soup.find_all('img',{'data-filter':"thumbnail-filter lazy-image"},src = re.compile('https'))
		jpg_list = []
		#修改图片链接
		for each in url_list:
			each = self.change(each['data-src'])
			jpg_list.append(each)
		return jpg_list

	def get_url_list(self):
		url_list = []
		for i in self.datenums:
			url = self.daily_base_url + str(i)
			url_list.append(url)
		return url_list

	def download(self):
		url_list = self.get_url_list()
		print(url_list)
		for i in url_list:
			jpg_list = self.get_jpg_url(i)
			for each in jpg_list:
				tupian = requests.get(each,headers = self.headers)
				#如果状态码不为200，则为png格式
				if str(tupian) == '<Response [200]>':
					filename = each.split('/')[-1]
					with open(filename,'wb') as f:
						f.write(tupian.content)
				else:
					each = each.replace('jpg','png')
					tupian = requests.get(each,headers = self.headers)
					filename = each.split('/')[-1]
					with open(filename,'wb') as f:
						f.write(tupian.content)


g.msgbox("嗨，欢迎进入第一版p站爬虫^_^")
msg = '你希望下载什么榜的图片呢'
title = '下载榜单选择'
choices = ('今日榜','国际榜')
choice = g.buttonbox(msg = msg,title = title,choices = choices)

#保存文件路径，如果不是默认则跳转
default = r'C:\Users\上衫夏乡\learn\pixiv'
savepath = g.diropenbox('请选择保存路径',default = default)
if savepath != default:
	os.chdir(savepath)
#可以考虑是否新建文件夹，名字可以从页面标题获取或者自选

if choice == '国际榜':
	pixiv = PixivSpider(0,0)
	g.msgbox('开始下载')
	pixiv.download()
	g.msgbox('下载已完成')

elif choice == '今日榜':
	daily_choice = g.buttonbox('请进一步选择',choices = ('过往今日榜','最新今日榜','批量下载过往今日榜'))
	if daily_choice == '过往今日榜':
		datenum = g.intergerbox('请输入日期，例【20171002】')
	elif daily_choice == '最新今日榜':
		pass
	elif daily_choice == '批量下载过往今日榜':
		#这个地方要写一些检查代码，判断日期的正确与否
		datenums = []
		datefields = g.multenterbox('请输入日期范围',fields =('*开始日期','*结束日期'))

		begaindate = int(datefields[0])
		enddate = int(datefields[1])

		while begaindate <= enddate:
			datenums.append(begaindate)
			begaindate += 1

		pixiv = PixivSpider_daily(datenums)
		pixiv.download()



