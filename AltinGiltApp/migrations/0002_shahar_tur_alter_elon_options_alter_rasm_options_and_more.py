# Generated by Django 5.2.1 on 2025-05-12 05:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AltinGiltApp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shahar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nomi', models.CharField(max_length=100, unique=True, verbose_name='Shahar nomi')),
            ],
            options={
                'verbose_name': 'shahar',
                'verbose_name_plural': 'shaharlar',
                'ordering': ['nomi'],
            },
        ),
        migrations.CreateModel(
            name='Tur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nomi', models.CharField(max_length=50, unique=True, verbose_name='Mulk turi nomi')),
            ],
            options={
                'verbose_name': 'mulk turi',
                'verbose_name_plural': 'mulk turlari',
                'ordering': ['nomi'],
            },
        ),
        migrations.AlterModelOptions(
            name='elon',
            options={'ordering': ['-created_at'], 'verbose_name': "e'lon", 'verbose_name_plural': "e'lonlar"},
        ),
        migrations.AlterModelOptions(
            name='rasm',
            options={'verbose_name': 'rasm', 'verbose_name_plural': 'rasmlar'},
        ),
        migrations.AlterField(
            model_name='elon',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Moderatsiyada'), ('APPROVED', 'Tasdiqlangan'), ('REJECTED', 'Rad etilgan')], db_index=True, default='PENDING', max_length=10),
        ),
        migrations.AlterField(
            model_name='elon',
            name='joylashuvi',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='AltinGiltApp.shahar', verbose_name='Joylashuvi'),
        ),
        migrations.AlterField(
            model_name='elon',
            name='turi',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='AltinGiltApp.tur', verbose_name='Mulk turi'),
        ),
    ]
