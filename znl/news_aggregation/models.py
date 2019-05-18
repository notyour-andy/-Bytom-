from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class News(models.Model):

	url = models.CharField(max_length=100, unique=True)
	title = models.CharField(max_length=100)
	date = models.CharField(max_length=100)

	SOURCE_OPTIONS = (
		('T', 'Twitter'),
		('WB', 'Weibo'),
		('WC', 'Wechat'),
		('B', 'BiliBili'),
		('G', 'GitHub'),
		('J', 'Jianshu')
		)

	source = models.CharField(max_length=20, choices=SOURCE_OPTIONS)
	img_url = models.CharField(max_length=200,)

class Collections(models.Model):
	user = models.ForeignKey(User, related_name='collections', on_delete=models.CASCADE)
	news = models.ForeignKey(News, related_name='collections', on_delete=models.CASCADE)

class Historys(models.Model):
	user = models.ForeignKey(User, related_name='historys', on_delete=models.CASCADE)
	news = models.ForeignKey(News, related_name='historys', on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)
