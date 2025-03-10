# Generated by Django 5.1.6 on 2025-02-23 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hostel', '0006_gallery_alter_announcement_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='status',
            field=models.CharField(choices=[('Present', 'Present'), ('Absent', 'Absent')], max_length=10),
        ),
        migrations.AlterUniqueTogether(
            name='attendance',
            unique_together={('hosteller', 'date')},
        ),
    ]
