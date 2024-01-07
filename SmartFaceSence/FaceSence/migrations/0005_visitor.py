# Generated by Django 4.2 on 2023-12-01 12:43

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('FaceSence', '0004_flat'),
    ]

    operations = [
        migrations.CreateModel(
            name='Visitor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visitor_name', models.CharField(max_length=256)),
                ('mobile_no', models.IntegerField()),
                ('address', models.CharField(max_length=256)),
                ('visitor_image', models.ImageField(default=None, upload_to='visitors/')),
                ('entry_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('proof', models.CharField(max_length=20)),
                ('flat_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FaceSence.flat')),
                ('whome_to_meet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='FaceSence.person')),
            ],
        ),
    ]
