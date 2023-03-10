# Generated by Django 4.1.6 on 2023-02-27 23:12

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mouvements', '0012_alter_produit_prix_alter_produit_quantite_stock_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alimenter_stock',
            name='produit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='alimenterproduit', to='mouvements.produit'),
        ),
        migrations.AlterField(
            model_name='contactclient',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contacts', to='mouvements.client'),
        ),
        migrations.AlterField(
            model_name='produit',
            name='quantite_stock',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='produit',
            name='seuil',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='remiseclient',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='remiseclient', to='mouvements.client'),
        ),
        migrations.AlterField(
            model_name='vente',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='venteclient', to='mouvements.client'),
        ),
        migrations.AlterField(
            model_name='vente',
            name='produit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='venteproduit', to='mouvements.produit'),
        ),
        migrations.AlterField(
            model_name='visitemedicale',
            name='delegue',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='visitemedicaleDelegue', to='mouvements.delegue'),
        ),
        migrations.AlterField(
            model_name='visitemedicale',
            name='produit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='visitemedicaleProduit', to='mouvements.produit'),
        ),
    ]
