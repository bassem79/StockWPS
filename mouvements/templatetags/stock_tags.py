import os
from datetime import date
from django import template
from django.db.models import Count
from mouvements.models import Vente
from datetime import date,datetime
from datetime import timedelta

register = template.Library()


@register.simple_tag
def total_ventes():
    return Vente.objects.filter(date_vente= date.today()).count()

@register.inclusion_tag('latest.html')
def get_ventes_today():
#     getp = Vente.objects.values('numero_BL','numero_facture').filter(
# date_vente= date.today() 
# ).order_by('numero_BL','numero_facture')

    getp = Vente.objects.filter(date_vente= date.today() )
    getp=getp.values('numero_BL','numero_facture').distinct()
   
    return {'getp':getp}


@register.inclusion_tag('latest.html')
def get_ventes_hier():
    getp = Vente.objects.values('numero_BL','numero_facture').filter(
date_vente= date.today() - timedelta(days=1)
).distinct()
    return {'getp':getp}