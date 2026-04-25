# Generated manually for SongParameters refactor.

from django.db import migrations, models


def copy_song_parameters_into_song(apps, schema_editor):
    Song = apps.get_model('core', 'Song')
    SongParameters = apps.get_model('core', 'SongParameters')

    for params in SongParameters.objects.all().iterator():
        Song.objects.filter(pk=params.song_id).update(
            title=params.title,
            occasion=params.occasion,
            genre=params.genre,
            voice_type=params.voice_type,
            custom_text=params.custom_text,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_song_callback_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='custom_text',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='song',
            name='genre',
            field=models.CharField(blank=True, choices=[('pop', 'Pop'), ('rock', 'Rock'), ('jazz', 'Jazz'), ('classical', 'Classical'), ('other', 'Other')], max_length=20),
        ),
        migrations.AddField(
            model_name='song',
            name='occasion',
            field=models.CharField(blank=True, choices=[('birthday', 'Birthday'), ('wedding', 'Wedding'), ('anniversary', 'Anniversary'), ('romantic_event', 'Romantic Event'), ('graduation', 'Graduation'), ('other', 'Other')], max_length=20),
        ),
        migrations.AddField(
            model_name='song',
            name='title',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='song',
            name='voice_type',
            field=models.CharField(blank=True, choices=[('baby', 'Baby'), ('grown_woman', 'Grown Woman'), ('grown_man', 'Grown Man'), ('girl', 'Girl'), ('boy', 'Boy')], max_length=20),
        ),
        migrations.RunPython(copy_song_parameters_into_song, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='song',
            name='genre',
            field=models.CharField(choices=[('pop', 'Pop'), ('rock', 'Rock'), ('jazz', 'Jazz'), ('classical', 'Classical'), ('other', 'Other')], max_length=20),
        ),
        migrations.AlterField(
            model_name='song',
            name='occasion',
            field=models.CharField(choices=[('birthday', 'Birthday'), ('wedding', 'Wedding'), ('anniversary', 'Anniversary'), ('romantic_event', 'Romantic Event'), ('graduation', 'Graduation'), ('other', 'Other')], max_length=20),
        ),
        migrations.AlterField(
            model_name='song',
            name='title',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='song',
            name='voice_type',
            field=models.CharField(choices=[('baby', 'Baby'), ('grown_woman', 'Grown Woman'), ('grown_man', 'Grown Man'), ('girl', 'Girl'), ('boy', 'Boy')], max_length=20),
        ),
        migrations.DeleteModel(
            name='SongParameters',
        ),
    ]
