from django.shortcuts import render
from .models import News, Collections, Historys
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
''''''
import requests
from bs4 import BeautifulSoup
import re
import time
from selenium import webdriver
from selenium.common import exceptions

# Create your views here.


def index(request):

	return render(request, 'base.html')

@login_required
def news(request):
	objects = News.objects.order_by("-date")
	#收藏
	current_user = request.user
	collection_list = current_user.collections.all()
	news_list = list()
	for collection in collection_list:
		news_list.append(collection.news)


	#分类
	news_bilibili = News.objects.filter(source='BiliBili').order_by("-date")
	news_weibo = News.objects.filter(source='Weibo').order_by('-date')
	news_wechat = News.objects.filter(source='Wechat').order_by('-date')
	news_jianshu = News.objects.filter(source='Jianshu').order_by('-date')
	news_github = News.objects.filter(source='Github')
	news_twitter = News.objects.filter(source='Twitter')
	
	#分页
	page= request.GET.get('page', 1)
	paginator= Paginator(objects, 5)

	try:
		objects = paginator.page(page)

	except PageNotAnInteger:
		objects = paginator.page(1)

	except EmptyPage:
		objects = paginator.page(paginator.num_pages)

	return render(request, 'news.html', {'objects': objects, 
							'news_list': news_list,#收藏 
							'news_bilibili': news_bilibili, 
							'news_weibo':news_weibo,
							'news_wechat':news_wechat,
							'news_jianshu':news_jianshu,
							'news_github':news_github,
							'news_twitter': news_twitter})

@login_required
def update(request):

	if request.method == 'POST':
		scrapy_type = request.POST['type']
		if scrapy_type == 'Jianshu':
			spider = NewsFromJianshuSpider()
		elif scrapy_type == 'BiliBili':
			spider = NewsFromBiliBiliSpider()
		elif scrapy_type == 'Wechat':
			spider = NewsFromWechatSpider()
		elif scrapy_type == 'Weibo':
			spider = NewsFromWeiboSpider()
		elif scrapy_type == 'Github':
			spider = NewsFromGithubSpider()
		spider.get_news()
		spider.save_data_to_model()
		datas = spider.datas
		return render(request, 'update.html', {'scrapy_type': scrapy_type, 'datas':datas})


	return render(request, 'update.html')

def home(request):

	return render(request, 'home.html')

def test(request):

	return render(request, 'test.html')

def profile(request):

	user = request.user
	news_list = reversed([collection.news for collection in user.collections.all()])
	historys_list = user.historys.all().order_by("-created_at")

	return render(request, 'profile.html', {'news_list' : news_list, 'historys_list':historys_list})


def likeNews(request):

	if request.method == 'GET':
		user_id = request.GET['user']
		news_id = request.GET['news']
		user = User.objects.get(pk=user_id)
		news = News.objects.get(pk=news_id)
		if news not in [collection.news for collection in user.collections.all()]:
			new = Collections(user=user, news=news)
			new.save()

		return HttpResponse('success!')

	else:
		return HttpResponse('request method is not a GET')

def historys(request):

	if request.method == 'GET':
		user_id = request.GET['user']
		news_id = request.GET['news']
		user = User.objects.get(pk=user_id)
		news = News.objects.get(pk=news_id)

		new = Historys(user=user, news=news)
		new.save()

		return HttpResponse('success!')

	else:
		return HttpResponse('request method is not a GET')
#简书爬虫
class NewsFromJianshuSpider():
	def __init__(self):
		self.headers ={
		'cookie': "sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2216a44840fb418f-0c36eb4b735b18-366e7e04-1024000-16a44840fb62c8%22%2C%22%24device_id%22%3A%2216a44840fb418f-0c36eb4b735b18-366e7e04-1024000-16a44840fb62c8%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; __yadk_uid=kYq687Mjh2eIGQw2kW20j47icr8ShD8J; read_mode=day; default_font=font2; locale=zh-CN; Hm_lvt_0c0e9d9b1e7d617b3e6842e85b9fb068=1555927666,1556123649; signin_redirect=https%3A%2F%2Fwww.jianshu.com%2Fu%2F0ff83f048a95; _m7e_session_core=034e049548d38e3c40457087b460623d; Hm_lpvt_0c0e9d9b1e7d617b3e6842e85b9fb068=1556343190",
		'upgrade-insecure-requests': '1',
		'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko)"}

		self.base_url = "https://www.jianshu.com"
		self.user_url = "https://www.jianshu.com/u/0ff83f048a95"
		self.datas = list()


	def get_news(self):
		
		response = requests.get(self.user_url, headers=self.headers)
		bs_obj = BeautifulSoup(response.text, 'lxml')

		'''确定文章的分页数'''
		passage_nums = bs_obj.find('div', class_="info").find_all('li')[2].p.text
		page_num = int(passage_nums) // 9 + 1

		for i in range(page_num):
			scrapy_url = self.user_url + "?order_by=shared_at&page=" + str(i+1)
			response = requests.get(scrapy_url, headers= self.headers)
			bs_obj = BeautifulSoup(response.text, 'lxml')
			passages = bs_obj.findAll('li', id=re.compile(r'note.[0-9]+'))

			for p in passages:
			    passage_url = self.base_url + p.a['href']
			    passage_title = p.find(class_ = 'title').text
			    passage_time = p.find(class_='time').attrs['data-shared-at']
			    passage_time = passage_time[0:10] + ' ' + passage_time[11:16]
			    if 'have-img' in p.attrs['class']:
			        passage_img_url = 'https:' + p.img['data-echo']
			    else:
			        passage_img_url = "{% static 'imgs/jianshu.jpg'%}"
			    
			    passage_source = 'Jianshu'
			    self.datas.append((passage_url, passage_title, passage_time, passage_img_url, passage_source))

	def save_data_to_model(self):
		for data in self.datas:
			if News.objects.filter(url=data[0]):
				continue
			else:
				new_model = News()
				new_model.url = data[0]
				new_model.title = data[1]
				new_model.date = data[2]
				new_model.img_url = data[3]
				new_model.source = data[4]
				new_model.save()


#B站爬虫
class NewsFromBiliBiliSpider():

	def __init__(self):

		self.user_url = 'https://space.bilibili.com/340186989/video'
		self.datas = list()

	def get_news(self):
		option=webdriver.ChromeOptions()
		option.add_argument('headless') # 设置option, 后台运行
		driver = webdriver.Chrome(executable_path='chromedriver',chrome_options=option)

		try:
			driver.get(self.user_url)
		except exceptions.InvalidSessionIdException as e:
			print(e.message)

		time.sleep(3)

		page_source_tree = driver.page_source
		bs_obj = BeautifulSoup(page_source_tree, 'lxml')

		video_tags = bs_obj.findAll('li', class_= re.compile(r'small-item .+'))

		for tag in video_tags:
			video_url = 'https:' + tag.a['href']
			video_img_url = 'https:' + tag.img['src']
			video_title = tag.img['alt']
			video_date = tag.find(class_='time').text
			if(video_date.count('-') == 1):
				video_date = '2019-' + video_date
			if(len(video_date.split('-')[1]) == 1):
				video_date = video_date[0:5] + '0' + video_date[5:]
			video_source = 'BiliBili'

			self.datas.append((video_url, video_title, video_date, video_img_url, video_source))

		driver.close()



	def save_data_to_model(self):
		for data in self.datas:
			if News.objects.filter(url=data[0]):
				continue
			else:
				new_model = News()
				new_model.url = data[0]
				new_model.title = data[1]
				new_model.date = data[2]
				new_model.img_url = data[3]
				new_model.source = data[4]
				new_model.save()

#wechat公众号爬虫
class NewsFromWechatSpider():

	def __init__(self):

		self.base_url = base_url = "https://wemp.app/accounts/be44c2b8-36f3-465f-a779-bfd9c17336f1?page="
		self.headers = {
		    'Cookie': "_ga=GA1.2.1611022330.1556462311; _gid=GA1.2.65581596.1556462313",
		    'Host': "wemp.app",
		    'If-None-Match': "4b53-x1GpiHHl3v3CfQXEkkFE8uwW1z4",
		    'Upgrade-Insecure-Requests': "1",
		    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko)"
			}

		self.datas = list()
		self.page_nums = 11
		self.date_header = '2019-'

	def get_news(self):
		for i in range(1, self.page_nums+1):
		    response = requests.get(self.base_url+str(i), headers=self.headers)
		    bs_obj =BeautifulSoup(response.text, 'lxml')
		    passage_tags = bs_obj.findAll('div', class_="post-item")
		    for tag in passage_tags:
		        passage_img_url = tag.img['src']
		        passage_title = tag.img['alt']
		        passage_date = tag.find(class_="post-item__date").text.strip()
		        if int(passage_date[0:2]) > 5:
		            self.date_header = '2018-'
		        passage_date = self.date_header + passage_date
		        passage_url = tag.find(class_="post-item__title")['href']
		        passage_url = 'https://wemp.app' + passage_url
		        passage_source = 'Wechat'
		        self.datas.append((passage_url, passage_title, passage_date, passage_img_url, passage_source))

		self.datas[-1][0].replace('2018', '2017')


	def save_data_to_model(self):
		for data in self.datas:
			if News.objects.filter(url=data[0]):
				continue
			else:
				new_model = News()
				new_model.url = data[0]
				new_model.title = data[1]
				new_model.date = data[2]
				new_model.img_url = data[3]
				new_model.source = data[4]
				new_model.save()


#Weibo爬虫：
class NewsFromWeiboSpider():

	def __init__(self):
		self.base_url = "https://m.weibo.cn/api/container/getIndex?type=uid&value=5966947038&containerid=1076035966947038&page="
		self.headers = {
			'Host': 'm.weibo.cn',
			'Referer': 'https://m.weibo.cn/u/1665372775',
			'User-Agent': 'User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1 wechatdevtools/0.7.0 MicroMessenger/6.3.9 Language/zh_CN webview/0'
			}

		self.page_nums = 16
		self.datas = list()

	def get_news(self):

		for i in range(self.page_nums):

			response = requests.get("https://m.weibo.cn/api/container/getIndex?type=uid&value=5966947038&containerid=1076035966947038&page=" + str(i), headers=self.headers)
			data = response.json()
			items = data.get('data').get('cards')

			for item in items:
				blog_url = item.get('scheme')

				blog_text = item.get('mblog').get('text')
				blog_date = item.get('mblog').get('created_at')
				if blog_date[0:4] != '2018':
					blog_date = '2019-' + blog_date

				if '0' in item.get('mblog').get('pic_types'):
					blog_img_url = item.get('mblog').get('bmiddle_pic')
				else:   
					try:
						blog_img_url = item.get('mblog').get('page_info').get('page_pic').get('url')
					except:
						blog_img_url = 'static'

				bs_obj = BeautifulSoup(item.get('mblog').get('text'), 'lxml')
				blog_title= bs_obj.text
				blog_source = 'Weibo'



				self.datas.append((blog_url, blog_title, blog_date, blog_img_url,blog_source))

	def save_data_to_model(self):
		for data in self.datas:
			if News.objects.filter(url=data[0]):
				continue
			else:
				new_model = News()
				new_model.url = data[0]
				new_model.title = data[1]
				new_model.date = data[2]
				new_model.img_url = data[3]
				new_model.source = data[4]
				new_model.save()

#Github爬虫
class NewsFromGithubSpider():

	def __init__(self):
		self.headers = {
	    'Upgrade-Insecure-Requests': '1',
	    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36"
		}
		self.base_url = "https://github.com/Bytom/"
		self.datas = list()

	def get_news(self):
		response = requests.get(self.base_url)
		bs_obj = BeautifulSoup(response.text, 'lxml')
		respositories_tags = bs_obj.find('div', class_="org-repos repo-list").findAll('li')

		for tag in respositories_tags:
		    title = tag.h3.text.strip() #标题
		    url = self.base_url + title
		    source = 'Github'
		    self.datas.append((url, title, ' ', 'static', source))


	def save_data_to_model(self):
		for data in self.datas:
			if News.objects.filter(url=data[0]):
				continue
			else:
				new_model = News()
				new_model.url = data[0]
				new_model.title = data[1]
				new_model.date = data[2]
				new_model.img_url = data[3]
				new_model.source = data[4]
				new_model.save()





def search(request):
	q = request.GET['query']
	objects = News.objects.filter(title__icontains=q).order_by("-date")

	return render(request, 'results.html', {'objects': objects, 'keywords':q })


