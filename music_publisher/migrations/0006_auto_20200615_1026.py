# Generated by Django 3.0.6 on 2020-06-15 10:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('music_publisher', '0005_work__work_id'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='work',
            options={'ordering': ('-id',), 'permissions': (('can_process_royalties', 'Can perform royalty calculations'),), 'verbose_name': 'Musical Work'},
        ),
    ]
