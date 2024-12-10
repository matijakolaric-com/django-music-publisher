# Generated by Django 4.2.13 on 2024-12-07 09:00

from django.db import migrations, models
import django.db.models.deletion
import music_publisher.base
import music_publisher.validators


class Migration(migrations.Migration):

    replaces = [
        ("music_publisher", "0003_cwrexport_created_on"),
        ("music_publisher", "0004_exofile"),
        ("music_publisher", "0005_auto_20220206_1720"),
        ("music_publisher", "0006_alter_cwrexport_nwr_rev"),
        ("music_publisher", "0007_auto_20220724_1028"),
        ("music_publisher", "0008_release_artist"),
    ]

    dependencies = [
        ("music_publisher", "0002_mayday"),
    ]

    operations = [
        migrations.AddField(
            model_name="cwrexport",
            name="created_on",
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.CreateModel(
            name="Playlist",
            fields=[],
            options={
                "verbose_name": "Playlist",
                "verbose_name_plural": "Playlists",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("music_publisher.release",),
        ),
        migrations.AlterModelOptions(
            name="artistinwork",
            options={
                "ordering": ("artist__last_name", "artist__first_name"),
                "verbose_name": "Artist performing",
                "verbose_name_plural": "Artists performing (not mentioned in recordings section)",
            },
        ),
        migrations.AddField(
            model_name="artist",
            name="description",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="artist",
            name="image",
            field=models.ImageField(
                blank=True, max_length=255, upload_to=music_publisher.base.upload_to
            ),
        ),
        migrations.AddField(
            model_name="label",
            name="description",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="label",
            name="image",
            field=models.ImageField(
                blank=True,
                max_length=255,
                upload_to=music_publisher.base.upload_to,
                verbose_name="Logo",
            ),
        ),
        migrations.AddField(
            model_name="recording",
            name="audio_file",
            field=models.FileField(
                blank=True, max_length=255, upload_to=music_publisher.base.upload_to
            ),
        ),
        migrations.AddField(
            model_name="release",
            name="description",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="release",
            name="image",
            field=models.ImageField(
                blank=True,
                max_length=255,
                upload_to=music_publisher.base.upload_to,
                verbose_name="Cover Art",
            ),
        ),
        migrations.AddField(
            model_name="writer",
            name="description",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="writer",
            name="image",
            field=models.ImageField(
                blank=True, max_length=255, upload_to=music_publisher.base.upload_to
            ),
        ),
        migrations.AlterField(
            model_name="recording",
            name="artist",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="recordings",
                to="music_publisher.artist",
                verbose_name="Recording Artist",
            ),
        ),
        migrations.AlterField(
            model_name="track",
            name="release",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tracks",
                to="music_publisher.release",
            ),
        ),
        migrations.AlterField(
            model_name="work",
            name="writers",
            field=models.ManyToManyField(
                related_name="works",
                through="music_publisher.WriterInWork",
                to="music_publisher.writer",
            ),
        ),
        migrations.AlterField(
            model_name="writer",
            name="saan",
            field=models.CharField(
                blank=True,
                help_text="Use this field for a general original publishing agreement.",
                max_length=14,
                null=True,
                validators=[music_publisher.validators.CWRFieldValidator("saan")],
                verbose_name="SAAN",
            ),
        ),
        migrations.AlterField(
            model_name="ackimport",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="alternatetitle",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="artist",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="artistinwork",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="cwrexport",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="dataimport",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="label",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="library",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="recording",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="release",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="track",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="work",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="workacknowledgement",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="writer",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="writerinwork",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="cwrexport",
            name="nwr_rev",
            field=models.CharField(
                choices=[
                    ("NW2", "CWR 2.2: New work registrations"),
                    ("RE2", "CWR 2.2: Revisions of registered works"),
                ],
                db_index=True,
                default="NWR",
                max_length=3,
                verbose_name="CWR version/type",
            ),
        ),
        migrations.AddField(
            model_name="writer",
            name="account_number",
            field=models.CharField(
                blank=True,
                help_text="Use this field for linking royalty statements with your accounting.",
                max_length=100,
                null=True,
                verbose_name="Account #",
            ),
        ),
        migrations.AlterField(
            model_name="ackimport",
            name="id",
            field=models.AutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="alternatetitle",
            name="id",
            field=models.AutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="artist",
            name="id",
            field=models.AutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="artistinwork",
            name="id",
            field=models.AutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="cwrexport",
            name="id",
            field=models.AutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="cwrexport",
            name="nwr_rev",
            field=models.CharField(
                choices=[
                    ("NWR", "CWR 2.1: New work registrations"),
                    ("REV", "CWR 2.1: Revisions of registered works"),
                    ("NW2", "CWR 2.2: New work registrations"),
                    ("RE2", "CWR 2.2: Revisions of registered works"),
                    ("WRK", "CWR 3.0: Work registration"),
                    ("ISR", "CWR 3.0: ISWC request (EDI)"),
                    ("WR1", "CWR 3.1 DRAFT: Work registration"),
                ],
                db_index=True,
                default="NWR",
                max_length=3,
                verbose_name="CWR version/type",
            ),
        ),
        migrations.AlterField(
            model_name="dataimport",
            name="id",
            field=models.AutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="label",
            name="id",
            field=models.AutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="library",
            name="id",
            field=models.AutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="recording",
            name="id",
            field=models.AutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="release",
            name="id",
            field=models.AutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="track",
            name="id",
            field=models.AutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="work",
            name="id",
            field=models.AutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="workacknowledgement",
            name="id",
            field=models.AutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="writer",
            name="id",
            field=models.AutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="writerinwork",
            name="id",
            field=models.AutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AddField(
            model_name="release",
            name="artist",
            field=models.ForeignKey(
                blank=True,
                help_text="Leave empty if a compilation by different artists.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="music_publisher.artist",
                verbose_name="Display Artist",
            ),
        ),
    ]