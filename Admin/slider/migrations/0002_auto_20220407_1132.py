# Generated by Django 3.1.2 on 2022-04-07 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('slider', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gallerymodel',
            name='slider_img',
            field=models.ImageField(upload_to='Admin/SliderImage'),
        ),
    ]
