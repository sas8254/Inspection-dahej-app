import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dahej_insp', '0003_job_performer_alter_job_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='job_date',
            # Existing rows backfilled to today; new rows require an explicit
            # value from the serializer.
            field=models.DateField(default=datetime.date.today),
            preserve_default=False,
        ),
    ]
