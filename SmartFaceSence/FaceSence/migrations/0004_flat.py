# Generated by Django 4.2 on 2023-12-01 12:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('FaceSence', '0003_person'),
    ]

    operations = [
        migrations.CreateModel(
            name='Flat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('block_no', models.CharField(max_length=2)),
                ('total_floor', models.CharField(max_length=3)),
                ('flat_no', models.CharField(max_length=3)),
                ('flat_type', models.CharField(max_length=5)),
                ('status', models.CharField(max_length=5)),
                ('alloted_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FaceSence.person')),
            ],
        ),
    ]
