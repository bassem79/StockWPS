# Generated by Django 4.1.6 on 2023-02-17 17:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mouvements', '0006_alter_client_taux_remise'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='taux_remise',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True),
        ),
    ]
