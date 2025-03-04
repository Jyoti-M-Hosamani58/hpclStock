# Generated by Django 3.0 on 2024-12-05 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hp_app', '0039_stocktodept_remark'),
    ]

    operations = [
        migrations.AddField(
            model_name='depttodept',
            name='balanceqty',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='depttodept',
            name='issuedqty',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='depttodept',
            name='receivedBy',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='depttodept',
            name='receivedFrom',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='depttodept',
            name='remark',
            field=models.CharField(max_length=500, null=True),
        ),
    ]
