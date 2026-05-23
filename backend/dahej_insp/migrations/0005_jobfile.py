from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dahej_insp', '0004_job_job_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='job_files/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('job', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='files', to='dahej_insp.job')),
            ],
            options={'ordering': ['-uploaded_at']},
        ),
    ]
