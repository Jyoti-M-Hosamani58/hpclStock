# Generated by Django 3.0 on 2024-11-26 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hp_app', '0018_remove_stock_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='vendorCompany',
            field=models.CharField(max_length=500, null=True),
        ),
    ]
