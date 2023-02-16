from django.contrib import admin
from .models import Client, Produit,Delegue,VisiteMedicale,Vente,Alimenter_stock,RemiseClient



@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ['nom_produit', 'image','description','prix','quantite_stock','seuil']
    #prepopulated_fields = {'slug': ('nom_produit',)}
    list_filter = ['nom_produit', 'seuil', 'quantite_stock','prix']
    search_fields = ('nom_produit','seuil', 'quantite_stock','prix')
    ordering = ['nom_produit']
   # prepopulated_fields = {'slug': ('nom_produit',)}


    
@admin.register(Delegue)
class DelegueAdmin(admin.ModelAdmin):
    list_display = ['nom_delegue', 'base']
    list_filter = ['nom_delegue', 'base']
    search_fields = ['nom_delegue', 'base']
    ordering = ['nom_delegue']

    
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['nom_client', 'description','telephone','base_client','type_client','taux_remise']
    list_filter = ['nom_client', 'base_client','type_client','taux_remise']
    search_fields = ['nom_client', 'base_client','type_client','taux_remise']
    #prepopulated_fields = {'slug': ('nom_client',)}

@admin.register(VisiteMedicale)
class VisiteMedicaleAdmin(admin.ModelAdmin):
    list_display = ['delegue', 'produit','date','quantite_donne']
    list_filter = ['delegue', 'produit','date','quantite_donne']
    search_fields = ['delegue', 'produit','date','quantite_donne']
    ordering = ['date']

@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = ['client', 'produit','date_vente','numero_BL','numero_facture',
    'quantite_vendu','moyen_payement','paye','gratuit','montant_remise','prix']
    list_filter = ['client__nom_client', 'produit__nom_produit','date_vente', 'quantite_vendu','moyen_payement','paye','gratuit']
    search_fields = ['client__nom_client', 'produit__nom_produit','date_vente', 'numero_BL','numero_facture','quantite_vendu','moyen_payement','paye','gratuit']
    ordering = ['date_vente','produit']


@admin.register(Alimenter_stock)
class Alimenter_stockAdmin(admin.ModelAdmin):
    list_display = ['produit','date_entree','quantite_entree']
    list_filter = ['produit','date_entree','quantite_entree']
    search_fields = ['produit','date_entree','quantite_entree']
    ordering = ['date_entree','produit']

@admin.register(RemiseClient)
class RemiseClientAdmin(admin.ModelAdmin):
    list_display = ['client','taux_remise','date_remise']
    list_filter = ['client','taux_remise','date_remise']
    search_fields = ['client','taux_remise','date_remise']
    ordering = ['date_remise']

