# Generated by Django 5.2.3 on 2025-06-21 04:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='automate',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
