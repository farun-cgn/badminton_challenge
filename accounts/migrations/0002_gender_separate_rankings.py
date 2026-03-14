from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        # Add gender field
        migrations.AddField(
            model_name='playerprofile',
            name='gender',
            field=models.CharField(
                choices=[('M', 'Männlich'), ('F', 'Weiblich')],
                default='M',
                max_length=1,
                verbose_name='Geschlecht',
            ),
        ),
        # Remove unique constraint from rank_position so rank 1 can exist per gender
        migrations.AlterField(
            model_name='playerprofile',
            name='rank_position',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
