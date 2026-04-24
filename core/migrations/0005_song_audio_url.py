from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_library_id_alter_profile_id_alter_sharelink_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='audio_url',
            field=models.URLField(blank=True, default='', max_length=2048),
        ),
    ]
