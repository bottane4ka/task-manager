# Generated by Django 2.2.16 on 2021-05-20 09:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0002_auto_20210520_1144'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='notifycountmodel',
            unique_together={('table_schema', 'table_name')},
        ),
    ]