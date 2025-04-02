# Generated by Django 5.1.4 on 2025-04-02 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ludwig', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='harmonicrecord',
            name='I_prevail_ang1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='harmonicrecord',
            name='I_prevail_ang2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='harmonicrecord',
            name='I_prevail_ang3',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='harmonicrecord',
            name='I_prevail_ang4',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='harmonicrecord',
            name='I_prevail_mag1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='harmonicrecord',
            name='I_prevail_mag2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='harmonicrecord',
            name='I_prevail_mag3',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='harmonicrecord',
            name='I_prevail_mag4',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
