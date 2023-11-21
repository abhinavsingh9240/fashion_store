# Generated by Django 4.2.5 on 2023-11-13 04:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0018_orderitem_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='home.product'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='size',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='home.size'),
        ),
    ]