# Generated by Django 4.2.5 on 2023-11-10 13:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0014_delete_customuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='size',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='home.size'),
            preserve_default=False,
        ),
    ]
