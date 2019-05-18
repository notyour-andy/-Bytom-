# Generated by Django 2.1.5 on 2019-05-07 11:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('news_aggregation', '0003_auto_20190427_1116'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collections',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AlterField(
            model_name='news',
            name='source',
            field=models.CharField(choices=[('T', 'Twitter'), ('WB', 'Weibo'), ('WC', 'Wechat'), ('B', 'BiliBili'), ('G', 'GitHub'), ('J', 'Jianshu')], max_length=20),
        ),
        migrations.AlterField(
            model_name='news',
            name='url',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AddField(
            model_name='collections',
            name='news',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collections', to='news_aggregation.News'),
        ),
        migrations.AddField(
            model_name='collections',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collections', to=settings.AUTH_USER_MODEL),
        ),
    ]
