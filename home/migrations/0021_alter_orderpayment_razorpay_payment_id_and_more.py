# Generated by Django 4.2.5 on 2023-11-23 03:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0020_orderpayment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderpayment',
            name='razorpay_payment_id',
            field=models.IntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name='orderpayment',
            name='razorpay_signature',
            field=models.TextField(blank=True),
        ),
    ]
