# Generated by Django 3.2.3 on 2021-06-06 22:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0010_auto_20210606_2119'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cart',
            field=models.ForeignKey(default='0', on_delete=django.db.models.deletion.CASCADE, to='main_app.cart', verbose_name='Товары'),
            preserve_default=False,
        ),
    ]