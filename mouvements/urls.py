from django.urls import path
from . import views
app_name = 'stock'
urlpatterns = [

path('', views.dashboard, name='dashboard'),
path('connexion/', views.user_login, name='connexion'),
path('deconnexion/', views.deconnexion, name='deconnexion'),
path('init_password/', views.changepassword, name='init_password'),    
    
path('delegue/', views.delegue_list, name='delegue_list'),
path('<str:zone>/delegue/', views.delegue_list, name='delegue_list_zone'),
path('delegue/<int:id>/', views.delegue_detail, name='delegue_detail'),

path('delegue/filtre/<int:id>/', views.delegue_detail_filtre, name='delegue_detail_filtre'),

path('delegue/ajouter/', views.delegue_ajouter.as_view(), name='delegue_ajouter'),
path('delegue/supprimer/<pk>/', views.delegue_supprimer.as_view(),name='delegue_supprimer'),
path('delegue/<pk>/update', views.delegueUpdateView.as_view(),name='delegue_modifier'), 

path('vente/ajouter/', views.Vente_ajouter,name='vente_ajouter'),
path('visite/', views.visite_ajouter,name='visite_ajouter'),


path('vente/filtre/', views.vente_list_filtre, name='vente_list_filtre'),
path('vente/', views.vente_list, name='vente_list'),
path('<str:period>/vente/', views.vente_list, name='vente_list_period'),
path('vente/<str:bl>/<str:facture>/', views.vente_detail, name='vente_detail'),
path('vente/filtrage/', views.vente_bl_facture, name='vente_bl_facture'),
path('vente/max/', views.vente_max, name='vente_max'),
path('produit/vente/max/', views.vente_max_produit, name='vente_max_produit'),

path('vente/filtre/max/<str:period>/', views.vente_max, name='vente_max_period'),
path('vente/ca/', views.vente_ca, name='vente_ca'),
path('vente/payement/', views.vente_payement, name='vente_payement'),
path('vente/payement/<str:bl>/<str:fact>/',views.payement, name='payement'),
path('vente/filtre/ca/<str:period>/', views.vente_ca, name='vente_ca_period'),
path('vente/supprimer/', views.vente_supprimer, name='vente_supprimer'),
path('vente/supprimer/<str:bl>/<str:fact>/',views.suppression, name='suppression'),

path('produit/', views.produit_list, name='produit_list'),
path('produit/ajouter/', views.produit_ajouter.as_view(), name='produit_ajouter'),
path('produit/<int:id>/', views.produit_detail, name='produit_detail'),
path('produit/<pk>/update', views.produitUpdateView.as_view(),name='produit_modifier'), 
path('produit/supprimer/<pk>/', views.produit_supprimer.as_view(),name='produit_supprimer'),



path('client/ajouter/', views.client_ajouter.as_view(), name='client_ajouter'),
path('client/', views.client_list, name='client_list'),
path('client/<pk>/update', views.clientUpdateView.as_view(),name='client_modifier'), 
path('client/<pk>/delete', views.clientDeleteView.as_view(),name='client_supprimer'), 


path('remise/list/<str:clt>',views.remises_list,name='remises_list'),
path('remise/ajouter/', views.remise_ajouter.as_view(), name='remise_ajouter'),
path('remise/<pk>/update', views.remiseUpdateView.as_view(),name='remise_modifier'), 
path('remise/<pk>/delete', views.remiseDeleteView.as_view(),name='remise_supprimer'), 

path('remise/<str:id>/ajouter/', views.remise_ajouter_clt, name='remise_ajouter_clt'),

path('contact/recherche/',views.rechercheContact,name='rechercheContact'),


path('contact/list/<str:clt>',views.contacts_list,name='contacts_list'),
path('contact/ajouter/', views.contact_ajouter.as_view(), name='contact_ajouter'),
path('contact/<pk>/update', views.contactUpdateView.as_view(),name='contact_modifier'), 
path('contact/<pk>/delete', views.contactDeleteView.as_view(),name='contact_supprimer'), 
path('contact/<str:id>/ajouter/', views.contact_ajouter_clt, name='contact_ajouter_clt'),


path('client/<int:id>/', views.venteClient, name='vente_client_historique'),
path('client/<int:id>/<str:period>', views.venteClient, name='vente_client_historique_period'),



path('export/xls/ventes', views.export_ventes_xls, name='export_ventes_xls'),
path('export/xls/produits', views.export_produits_xls, name='export_produits_xls'),
path('export/xls/clients', views.export_clients_xls, name='export_clients_xls'),
path('export/xls/delegues', views.export_delegues_xls, name='export_delegues_xls'),

path('vente_prd_chart/', views.vente_prd_chart,name='vente_prd_chart'),
path('vente_prd_filtre_chart/', views.vente_prd_filtre_chart,name='vente_prd_filtre_chart'),
path('vente_clt_chart/', views.vente_clt_chart,name='vente_clt_chart'),
path('vente_clt_filtre_chart/', views.vente_clt_filtre_chart,name='vente_clt_filtre_chart'),
path('vente_prd_evol_chart/', views.vente_prd_evol_chart,name='vente_prd_evol_chart'),
path('vente_base_chart/', views.vente_base_chart,name='vente_base_chart'),

]