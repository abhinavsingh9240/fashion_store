# Generated by Django 4.2.5 on 2023-10-02 03:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0009_remove_product_stock'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='thumbnail',
            field=models.ImageField(default='', upload_to='category_thumbnails/'),
            preserve_default=False,
        ),
    ]
