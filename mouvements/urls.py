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
path('delegue/ajouter/', views.delegue_ajouter.as_view(), name='delegue_ajouter'),
path('delegue/supprimer/<pk>/', views.delegue_supprimer.as_view(),name='delegue_supprimer'),
path('vente/ajouter/', views.Vente_ajouter,name='vente_ajouter'),
path('visite/', views.visite_ajouter,name='visite_ajouter'),

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


path('client/<int:id>/', views.venteClient, name='vente_client_historique'),
path('client/<int:id>/<str:period>', views.venteClient, name='vente_client_historique_period'),



path('export/xls/ventes', views.export_ventes_xls, name='export_ventes_xls'),
path('export/xls/produits', views.export_produits_xls, name='export_produits_xls'),
]