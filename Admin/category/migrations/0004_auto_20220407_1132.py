# Generated by Django 3.1.2 on 2022-04-07 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0003_auto_20220407_1051'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categorymodel',
            name='cat_img',
            field=models.ImageField(null=True, upload_to='Admin/categoryImage'),
        ),
    ]
