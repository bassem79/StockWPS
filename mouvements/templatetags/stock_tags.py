import os
from datetime import date
from django import template
from django.db.models import Count
from mouvements.models import Vente

register = template.Library()


@register.simple_tag
def total_ventes():
    return Vente.objects.filter(date_vente= date.today()).count()

@register.inclusion_tag('latest.html')
def get_ventes_payes():
    getp = Vente.objects.filter(
paye=True
).order_by('client__nom_client')[:3]
    return {'getp':getp}


@register.inclusion_tag('latest.html')
def get_ventes_nonpayes():
    getp = Vente.objects.filter(
paye=False
).order_by('client__nom_client')[:3]
    return {'getp':getp}