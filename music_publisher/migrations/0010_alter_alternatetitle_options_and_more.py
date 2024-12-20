# Generated by Django 4.2.13 on 2024-12-05 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("music_publisher", "0009_alter_workacknowledgement_society_code_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="alternatetitle",
            options={
                "ordering": ("-suffix", "title_type", "title"),
                "verbose_name": "Alternate Title",
            },
        ),
        migrations.RenameIndex(
            model_name="workacknowledgement",
            new_name="music_publi_society_ebcad0_idx",
            old_fields=("society_code", "remote_work_id"),
        ),
        migrations.AlterUniqueTogether(
            name="alternatetitle",
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name="artistinwork",
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name="track",
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name="writerinwork",
            unique_together=set(),
        ),
        migrations.AddField(
            model_name="alternatetitle",
            name="title_type",
            field=models.CharField(
                choices=[
                    ("AT", "Alternative Title"),
                    ("TE", "First Line of Text"),
                    ("FT", "Formal Title"),
                    ("IT", "Incorrect Title"),
                    ("OT", "Original Title"),
                    ("TT", "Original Title Translated"),
                    ("ET", "Extra Search Title"),
                ],
                default="AT",
                max_length=2,
            ),
        ),
        migrations.AddField(
            model_name="work",
            name="title_type",
            field=models.CharField(
                choices=[
                    ("AT", "Alternative Title"),
                    ("TE", "First Line of Text"),
                    ("FT", "Formal Title"),
                    ("IT", "Incorrect Title"),
                    ("OT", "Original Title"),
                    ("TT", "Original Title Translated"),
                    ("ET", "Extra Search Title"),
                ],
                default="AT",
                max_length=2,
            ),
        ),
        migrations.AddIndex(
            model_name="alternatetitle",
            index=models.Index(
                fields=["work_id", "title_type", "title"],
                name="music_publi_work_id_bf054a_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="artistinwork",
            index=models.Index(
                fields=["work", "artist"], name="music_publi_work_id_bdf6c3_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="track",
            index=models.Index(
                fields=["recording", "release"], name="music_publi_recordi_0f0a83_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="track",
            index=models.Index(
                fields=["release", "cut_number"], name="music_publi_release_f5662c_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="writerinwork",
            index=models.Index(
                fields=["work", "writer", "controlled"],
                name="music_publi_work_id_0a239a_idx",
            ),
        ),
    ]
