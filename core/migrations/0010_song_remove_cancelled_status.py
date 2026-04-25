from django.db import migrations, models


def cancelled_to_failed(apps, schema_editor):
    Song = apps.get_model('core', 'Song')
    Song.objects.filter(status='cancelled').update(status='failed')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_user_password'),
    ]

    operations = [
        migrations.RunPython(cancelled_to_failed, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='song',
            name='status',
            field=models.CharField(
                choices=[
                    ('generating', 'Generating'),
                    ('ready', 'Ready'),
                    ('failed', 'Failed'),
                ],
                default='generating',
                max_length=20,
            ),
        ),
    ]
