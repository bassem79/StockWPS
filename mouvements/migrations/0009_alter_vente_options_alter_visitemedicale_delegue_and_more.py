# Generated by Django 4.1.6 on 2023-02-19 16:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mouvements', '0008_alter_client_taux_remise'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vente',
            options={'ordering': ['-date_vente']},
        ),
        migrations.AlterField(
            model_name='visitemedicale',
            name='delegue',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='visitemedicaleDelegue', to='mouvements.delegue'),
        ),
        migrations.AlterField(
            model_name='visitemedicale',
            name='produit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='visitemedicaleProduit', to='mouvements.produit'),
        ),
    ]