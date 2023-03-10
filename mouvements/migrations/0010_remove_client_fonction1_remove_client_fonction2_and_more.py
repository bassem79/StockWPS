# Generated by Django 4.1.6 on 2023-02-20 15:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mouvements', '0009_alter_vente_options_alter_visitemedicale_delegue_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='fonction1',
        ),
        migrations.RemoveField(
            model_name='client',
            name='fonction2',
        ),
        migrations.RemoveField(
            model_name='client',
            name='fonction3',
        ),
        migrations.RemoveField(
            model_name='client',
            name='fonction4',
        ),
        migrations.RemoveField(
            model_name='client',
            name='telephone1',
        ),
        migrations.RemoveField(
            model_name='client',
            name='telephone2',
        ),
        migrations.RemoveField(
            model_name='client',
            name='telephone3',
        ),
        migrations.RemoveField(
            model_name='client',
            name='telephone4',
        ),
        migrations.CreateModel(
            name='Contactclient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom_contact', models.CharField(max_length=100)),
                ('fonction_contact', models.CharField(max_length=100)),
                ('telephone_contact', models.CharField(max_length=100)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='contacts', to='mouvements.client')),
            ],
        ),
    ]
