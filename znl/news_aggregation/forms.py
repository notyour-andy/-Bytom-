from django import forms

SOURCE_OPTIONS = (
	('T', 'Twitter'),
	('WB', 'Weibo'),
	('WC', 'Wechat'),
	('B', 'BiliBili'),
	('H', 'Huodongxing'),
	('G', 'GitHub')
	)

class SpiderChoiceForm(forms.Form):
	source = forms.ChoiceField(choices=SOURCE_OPTIONS)