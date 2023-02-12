from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.db.models import Count,Q,Sum,F,ExpressionWrapper,Case, Value, When,Max,Subquery,OuterRef,FloatField
from .models import *
from .forms import *
from django.urls import reverse_lazy,reverse
from django.shortcuts import render, get_object_or_404,redirect
from django.views.generic import CreateView,UpdateView,DeleteView
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib import messages
from django.conf import settings
import os
from django.http import JsonResponse
from django.views.generic.edit import FormView
from datetime import date,datetime
from django.db.models.functions import (
    ExtractDay, ExtractMonth, ExtractQuarter, ExtractWeek,
     ExtractIsoWeekDay, ExtractWeekDay, ExtractIsoYear, ExtractYear,
 )
from django.db.models import Count
from django.db import IntegrityError, transaction
from django.db.models.functions import Cast
from django.db.models import IntegerField,DecimalField,CharField
from django.contrib.auth import authenticate, login, logout
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
import xlwt

def dashboard(request):
    seuil = Produit.objects.filter(quantite_stock__lte = F('seuil'))
    return render(request, 'dashboard.html', locals())

def user_login(request):
    next = request.POST.get('next', request.GET.get('next', ''))

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['nom_d_utilisateur'], password=cd['mot_de_passe'])
            if user is not None:

                login(request, user)
                request.session['utilisateur'] = cd['nom_d_utilisateur']
                request.session['mot_de_passe'] = cd['mot_de_passe']
                msg = "Vous êtes maintenant connecté."


                

                messages.success(request, msg)
                if next:
                    return HttpResponseRedirect(next)

            else:
                messages.warning(request, "Vérifier vos paramètres de connexion.")
            return redirect('stock:dashboard')
    else:
        form = LoginForm()
        ctx = {'form': form, 'next': next}
    return render(request, 'connexion.html', locals())


@login_required
def deconnexion(request):
    logout(request)
    return redirect('stock:connexion')

@login_required
def changepassword(request):
    if request.method == 'POST':
        form = changepwd(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if cd['Ancien_mot_de_passe'] != request.session['mot_de_passe']:
                messages.warning(request, "Vérifier votre ancien mot de passe.")
                return redirect('stock:deconnexion')
            else:
                if cd['Nouveau_mot_de_passe'] != cd['Confirmer_nouveau_mot_de_passe']:
                    messages.warning(request, "Les mots de passe ne correspondent pas. Opération avortée")
                    return redirect(reverse('stock:changepassword'))
                else:
                    user = request.user
                    user.set_password(form.cleaned_data['Nouveau_mot_de_passe'])
                    user.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, "mot de passe changé.")
                    return redirect(reverse('stockconnexion'))
    else:
        form = changepwd()
    return render(request, 'change_password.html', {'form': form})











@login_required
def delegue_list(request,zone = None):
    delegue = Delegue.objects.all()
    
    if zone:
        delegue = delegue.filter(base=zone)
    paginator = Paginator(delegue, 5) # 10 posts in each page
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request, 'delegue_list.html', {'page': page,
                                                 'nambir': delegue.count(),
                                                   'posts':posts,
                                                   })



@login_required
def delegue_detail(request, id):
    delegue = get_object_or_404(Delegue, id=id) 
    year = ExtractYear(date.today())
    month= ExtractMonth(date.today())
    total = delegue.visitemedicaleDelegue.all().order_by("-date","produit__nom_produit")
    echantillon = delegue.visitemedicaleDelegue.filter(date__month = month,date__year =year).values("produit__nom_produit").order_by("produit__nom_produit").annotate(total_qte=Sum('quantite_donne')) 
    echantillon2 = delegue.visitemedicaleDelegue.filter(date__year =year).values("produit__nom_produit").order_by("produit__nom_produit").annotate(total_qte=Sum('quantite_donne'))  

    return render(request, 'delegue_detail.html', {'delegue': delegue,
                                                     'echantillon': echantillon,
                                                     'echantillon2': echantillon2,
                                                     'total': total      })


@method_decorator(login_required, name='dispatch')
class delegue_ajouter(CreateView):
    model = Delegue
    form_class = delegueAjoutForm
    template_name = "delegue_ajouter.html"
    def get_success_url(self):
        return (reverse('stock:delegue_list'))

@method_decorator(login_required, name='dispatch')
class delegue_supprimer(DeleteView):
    model = Delegue
    # success_url ="stock:delegue_list"
    template_name = "delegue_supprimer.html"
    def get_success_url(self):
        return (reverse('stock:delegue_list'))

@login_required
def visite_ajouter(request):

    if request.method == "POST":
        form = VisiteAjoutForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            qq= Produit.objects.get(nom_produit=cd["produit"])
            if cd["quantite_donne"] > qq.quantite_stock:
                messages.error(request, "Erreur. Stock insuffisant !!")
            else:
                form.save()    
                return redirect(reverse("stock:delegue_list"))
        
    else:
        form = VisiteAjoutForm()

    return render(request, 'Visite_ajouter.html', locals())           



# def Vente_ajouter(request):
#     # client = Client.objects.all()
    
#     produit = Produit.objects.all()
#     vente_precedente = Vente.objects.all()
    
#     # link_data = [{'prd': l}
#     #     for l in produit]
#     if request.method == "POST":
#         form = Entetevente(request.POST)
#         LinkFormSet= formset_factory(VenteFormSet, formset=BaseLinkFormSet, extra=1)
#         if LinkFormSet.is_valid() and form.is_valid:
#              messages.error(request, 'imchi wija asba')
#     else:
#         form = Entetevente()
      
#         LinkFormSet = formset_factory(VenteFormSet, formset=BaseLinkFormSet, extra=1)
    
#     context = {
#         'form': form,
#         'LinkFormSet': LinkFormSet,
#         # 'choice_links':link_data
#     }
#     return render(request, 'vente_ajouter.html', context)


@login_required
def Vente_ajouter(request):
    LinkFormSet = formset_factory(LinkForm, formset=BaseLinkFormSet, extra=3)
    arti=Produit.objects.all().values("nom_produit")
    link_data = [{'nom_produit': l ,'quantite_vendu':0}
        for l in arti]   
    if request.method == 'POST':
        form= Entetevente(request.POST)
        link_formset = LinkFormSet(request.POST)
        if link_formset.is_valid() and form.is_valid():
            new_links = []
            cd = form.cleaned_data
            cd2 = link_formset.cleaned_data
            for link_form in link_formset:
                client = cd['client']
                numero_BL= cd['numero_BL']
                numero_facture= cd['numero_facture']
                
                moyen_payement= cd['moyen_payement']
                paye= cd['paye']
                gratuit= cd['gratuit']
                produit= link_form.cleaned_data.get('nom_produit')
                
                quantite_vendu= link_form.cleaned_data.get('quantite_vendu')
                
                tab=[]
                #tmp = Vente.objects.filter(client__nom_client = client,numero_BL=numero_BL, numero_facture=numero_facture)
                tmp = get_object_or_404(Produit,nom_produit = produit)
               #
                if quantite_vendu > tmp.quantite_stock:
                
                    messages.error(request, f"ERREUR. OPERATION INTERROMPU! Vous ne disposez pas assez de stock! Vous avez {tmp.quantite_stock} en stock pour  \
                                       produit {produit} vous ne pouvez vendre {quantite_vendu}  ")
                    return redirect(reverse('stock:vente_list'))
                
                # tmp = Vente.objects.filter(client__nom_client = client,numero_BL=numero_BL, numero_facture=numero_facture)
                # for ab in tmp:
                #     tab.append({'nom':produit,'qte':ab.quantite_vendu})

                new_links.append(Vente(client = client,numero_BL=numero_BL, numero_facture=numero_facture,  \
                moyen_payement=moyen_payement,paye=paye,gratuit=gratuit,produit=produit, \
                quantite_vendu= quantite_vendu ))
                
    
            try:
                with transaction.atomic():
                    UserLink = Vente.objects.all()


                    # UserLink.filter(client = client,numero_BL=numero_BL,numero_facture=numero_facture).delete()

                    UserLink.bulk_create(new_links)
                    # tabb = list(tab)
                    # for bbb in tabb:
                    #     b=Produit.objects.get(nom_produit = bbb['nom'])
                    #     b.quantite_stock =  b.quantite_stock + bbb['qte']
                    #     b.save()
                    for ab in new_links:
                        b=get_object_or_404(Produit,nom_produit = ab.produit.nom_produit)
                        b.quantite_stock =  b.quantite_stock - ab.quantite_vendu
        
                        b.save()


                    
                    #oldvente = Vente.objects.filter(client = client,numero_BL=numero_BL,numero_facture=numero_facture).delete()
                    #oldvente.bulk_create(new_links)
                    messages.success(request, f'Votre vente à été correctement saisie/mis à jour.')
                    return redirect(reverse('stock:vente_list'))

            except IntegrityError:  # If the transaction failed
                messages.error(request, 'Une exception à provoqué une erreur. veuillez ré-essayer ultérieurement')
            return redirect(reverse('stock:delegue_list'))
        else:
            messages.error(request,'Saisie incorrecte !! veuillez éessayer.')
    else:
        
        form= Entetevente()
        link_formset = LinkFormSet()
        #link_formset = LinkFormSet(initial=k)

    
    context = {
        'form' : form,
        'link_formset': link_formset,
        # 'choice_links':link_data
    }
    return render(request, 'vente_ajouter.html', context)


# class ListeConv(ListView):
#     model = Vente
#     context_object_name = "ven"
#     template_name = "vente_list.html"
#     paginate_by = 5

@staff_member_required
def vente_list(request,period = None):
    ventes = Vente.objects.all().order_by('client__nom_client')

    today =ExtractDay(date.today())
    yesterday = date.today() - timedelta(days=1)
    week = ExtractWeek(date.today())
    month= ExtractMonth(date.today())
    year = ExtractYear(date.today())
    if period:
        if period == '1' :
            ventes = ventes.filter(date_vente = date.today() )
        
        elif period == '2' :
            ventes = ventes.filter(date_vente = yesterday )
    
        elif period == '3' :
            ventes = ventes.filter(date_vente__week = week,date_vente__month = month, date_vente__year= year )

        elif period == '4' :
            ventes = ventes.filter(date_vente__month = month,date_vente__year= year)   
     
    
    # ventes = ventes.annotate(total_produit=( Cast('quantite_vendu',output_field=IntegerField()) * Cast('client__taux_remise',output_field=DecimalField())  )) 
    ventes= ventes.exclude(gratuit=True ).order_by("numero_BL","numero_facture")
    ventes = ventes.annotate( price=(F('quantite_vendu') * F('client__taux_remise') * F('produit__prix') ))
    # ventes = ventes.annotate(
    # total=ExpressionWrapper(
    #     F('quantite_vendu') * F('client__taux_remise') * F('produit__prix'), output_field=DecimalField()))

   
    globalite = 0 
    for t in ventes:
        globalite = globalite + t.price

    paginator = Paginator(ventes, 50) # 10 posts in each page

    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request, 'vente_list.html', {'page': page,
                                                 'nambir': ventes.count(),
                                                   'posts':posts,
                                                   'globalite': globalite,
                                        
                                                   })
@staff_member_required
def vente_detail(request, bl,facture):
    ventes = Vente.objects.filter(numero_BL=bl,numero_facture=facture) 
    
    ventes = ventes.order_by("produit__nom_produit").annotate(
        price= (F('quantite_vendu') * F('client__taux_remise') * F('produit__prix') ))
    gg = ventes.first()       
    globalite = 0 
    for t in ventes:
        globalite = globalite + t.price
    return render(request, 'vente_detail.html', {'ventes': ventes,           
                                                 'globalite': globalite ,
                                                   'gg':gg,  })

@login_required
def produit_list(request):
    prd = Produit.objects.all()
    
    query = request.GET.get('q')
    if query:
        prd=prd.filter(

            Q(nom_produit__icontains=query)|
            Q(seuil__icontains=query)|
            Q(quantite_stock__icontains=query)|
            Q(prix__icontains=query)

        ).distinct()
    
    paginator = Paginator(prd, 5) # 5 posts in each page
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request, 'produit_list.html', {'page': page,
                                                 'nambir': prd.count(),
                                                   'posts':posts,
                                                   })                                                
@method_decorator(login_required, name='dispatch')
class produit_ajouter(CreateView):
    model = Produit
    form_class = produitAjoutForm
    template_name = "produit_ajouter.html"
    success_message = "%(produit)s ajouté avec succés"
    def get_success_url(self):
        return (reverse('stock:produit_list'))
    
def produit_detail(request, id):
    form=produitAjoutForm()

    prd = get_object_or_404(Produit, id=id) 
    return render(request, 'produit_detail.html', {'prd': prd,
                                                   })

@method_decorator(login_required, name='dispatch')
class produitUpdateView(UpdateView):
    # specify the model you want to use
    model = Produit

    fields = [
        "image",
        "description",
        "prix",
        "quantite_stock",
        "seuil"
    ]
    template_name = "produit_modifier.html"
    context_object_name = "prd"
    def get_success_url(self):
        return (reverse('stock:produit_list'))
    
    def updateimage(request, id):  #this function is called when update data
        data = Produit.objects.get(id=id)
        form = form(request.POST,request.FILES,instance = data)
        if form.is_valid():
            data.image_document.delete()  # This will delete your old image
            form.save()
            # return redirect("/myapp/productlist")
        else:
            messages.error(request,"ATTENTION, l'operation à echoué")
            return (reverse('stock:produit_list'))
      
@staff_member_required
def venteClient(request,id,period=None):
    cl = get_object_or_404(Client,id=id)
    historique = cl.venteclient.all()
    today =ExtractDay(date.today())
    yesterday = (date.today() - timedelta(days=1))
    week = ExtractWeek(date.today())
    month= ExtractMonth(date.today())
    year = ExtractYear(date.today())
    if period:
        if period == '1' :
            historique = historique.filter(date_vente = date.today() )
        
        elif period == '2' :
            historique = historique.filter(date_vente = yesterday )
    
        elif period == '3' :
            historique = historique.filter(date_vente__week = week,date_vente__month = month, date_vente__year=year)

        elif period == '4' :
            historique = historique.filter(date_vente__month = month , date_vente__year=year)   
    gratuite = historique
    historique2= historique
    gratuite = gratuite.filter(gratuit=True)
    historique = historique.exclude(gratuit=True)
    historique = historique.annotate( price=(F('quantite_vendu') * F('client__taux_remise') * F('produit__prix') ))
    
    # historique = historique.annotate(price=Case(
    #     When (gratuit=False,then=Value(F('quantite_vendu') * F('client__taux_remise') * F('produit__prix') )) ,
    #     default=Value(0),
    #     output_field=DecimalField() ))



    historique2 = historique.exclude(paye=True)
    historique2 = historique2.annotate( price2=(F('quantite_vendu') * F('client__taux_remise') * F('produit__prix') ))
  

    globalite = 0 
    for t in historique:
        globalite = globalite + t.price
    globalite2 = 0 
    for t in historique2:
        globalite2 = globalite2 + t.price2    
    return render(request, 'vente_client_historique.html', {'historique': historique, 
                                                 'nambir': historique.count(),
                                                 'globalite': globalite,
                                                 'cl':cl,
                                                 'globalite2': globalite2,
                                                 'historique2': historique2,
                                                 'gratuite':gratuite})

                                        
@staff_member_required
def vente_bl_facture(request) :    
  
    
        
    
    
    if request.POST['bl'] != "None" :
            selected_bl =  Vente.objects.filter(numero_BL=request.POST['bl'])
    elif request.POST['fact'] != "None" :
            selected_bl =  Vente.objects.filter(numero_facture=request.POST['fact'])  
    elif request.POST['bl'] == "None" or request.POST['fact'] == "None":    
            messages.error (request, "Problème de filtre! vous devez choisir un BL ou une facture !! ")
            return redirect('stock:vente_list')
    gratuite = selected_bl
    historique2= selected_bl
    gratuite = gratuite.filter(gratuit=True)
    selected_bl = selected_bl.exclude(gratuit=True)
    selected_bl = selected_bl.annotate( price=(F('quantite_vendu') * F('client__taux_remise') * F('produit__prix') ))




    historique2 = selected_bl.exclude(paye=True)
    historique2 = historique2.annotate( price2=(F('quantite_vendu') * F('client__taux_remise') * F('produit__prix') ))
  
    
    globalite = 0 
    for t in selected_bl:
        globalite = globalite + t.price
    globalite2 = 0 
    for tt in historique2:
        globalite2 = globalite2 + tt.price2   


    

    return render(request, 'vente_detail_BlFact.html', {
        #  'cl':cl,
            'selected_bl': selected_bl,
                                                             'nambir': selected_bl.count(),
                                                 'globalite': globalite,
                                             
                                                 'globalite2': globalite2,
                                                 'historique2': historique2,
                                                 'gratuite':gratuite})


 
@staff_member_required  
def vente_ca(request,period=None):
    ventes = Vente.objects.all()

    yesterday = date.today() - timedelta(days=1)
    week = ExtractWeek(date.today())
    month= ExtractMonth(date.today())
    year = ExtractYear(date.today())
    
    if period == '1' :
        ventes = ventes.filter(date_vente = date.today() )
        
    elif period == '2' :
        ventes = ventes.filter(date_vente = yesterday )
    
    elif period == '3' :
        ventes = ventes.filter(date_vente__week = week, date_vente__month = month ,date_vente__year = year )

    elif period == '4' :
        ventes = ventes.filter(date_vente__month = month,date_vente__year = year ) 
    elif period == '5' :
        ventes = ventes.filter(date_vente__year = year )
#     annotation = {
#     'AcSum': Sum('quantite_vendu')
# }
    print(period)
    ventes = ventes.order_by('client__nom_client').values('client__nom_client').annotate(AcSum= Sum(
    F('quantite_vendu') * F('client__taux_remise') * F('produit__prix')

    ))
    max = ventes.order_by('-AcSum')[:1]
    

#     sub_filter = Q(produit__nom_produit=OuterRef('produit__nom_produit'))

#     subquery = ventes.objects.filter(sub_filter).values(
#    'produit__nom_produit', 'quantite_vendu').annotate(**annotation).order_by(
#     '-AcSum').values('AcSum')[:1]

#     query = query.annotate(max_intensity=Subquery(subquery))


    return render(request, 'vente_ca.html', {'ventes':ventes,
                                                'nambir': ventes.count(),
                                            'max':max,
                                           
                                                } )

@staff_member_required
def vente_max(request,period=None):
    ventes = Vente.objects.all()

    yesterday = date.today() - timedelta(days=1)
    week = ExtractWeek(date.today())
    month= ExtractMonth(date.today())
    year = ExtractYear(date.today())
    
    if period == '1' :
        ventes = ventes.filter(date_vente = date.today() )
        
    elif period == '2' :
        ventes = ventes.filter(date_vente = yesterday )
    
    elif period == '3' :
        ventes = ventes.filter(date_vente__week = week, date_vente__month = month ,date_vente__year = year )

    elif period == '4' :
        ventes = ventes.filter(date_vente__month = month,date_vente__year = year ) 
    elif period == '5' :
        ventes = ventes.filter(date_vente__year = year )
#     annotation = {
#     'AcSum': Sum('quantite_vendu')
# }
    ventes = ventes.order_by('client__nom_client','produit__nom_produit').values('client__nom_client','produit__nom_produit').annotate(AcSum= Sum('quantite_vendu'))
    ventes=ventes.order_by('-AcSum')
    max = ventes.order_by('-AcSum')[:1]
   
    

#     sub_filter = Q(produit__nom_produit=OuterRef('produit__nom_produit'))

#     subquery = ventes.objects.filter(sub_filter).values(
#    'produit__nom_produit', 'quantite_vendu').annotate(**annotation).order_by(
#     '-AcSum').values('AcSum')[:1]

#     query = query.annotate(max_intensity=Subquery(subquery))


    return render(request, 'vente_max.html', {'ventes':ventes,
                                                'nambir': ventes.count(),
                                            'max':max,
                                           
                                                } )

@login_required
def vente_payement(request):
    selected_bl = Vente.objects.filter(paye=False,gratuit=False).values("numero_BL","numero_facture").order_by("numero_BL","numero_facture")
    globalite = 0   
    
    if request.method == 'POST':
        if request.POST['bl'] != "None" and request.POST['fact'] == "None":
            selected_bl =  Vente.objects.filter(numero_BL=request.POST['bl'])

        elif request.POST['bl'] == "None" and request.POST['fact'] != "None":
            selected_bl =  Vente.objects.filter(numero_facture=request.POST['fact'])  

        elif request.POST['bl'] != "None" and request.POST['fact'] != "None":
            selected_bl = Vente.objects.filter(numero_BL = request.POST['bl'], numero_facture=request.POST['fact'])
        elif request.POST['bl'] == "None" and request.POST['fact'] == "None":
            messages.error (request, "Problème de filtre! vous devez choisir un BL ou une facture !! ")
            return redirect('stock:vente_payement')
        
        selected_bl = selected_bl.annotate( price=(F('quantite_vendu') * F('client__taux_remise') * F('produit__prix') ))

        for t in selected_bl:
                globalite = globalite + t.price
        bl = request.POST["bl"]
        fact= request.POST['fact']
        return render(request, 'vente_payement.html', {'selected_bl':selected_bl,
                                           
                                            'globalite':globalite,
                                            'bl':bl,
                                            'fact':fact,

                                                } )


    return render(request, 'vente_payement.html', {'selected_bl':selected_bl,
                                            'globalite':globalite,

                                                } )
@login_required
def payement(request,bl=None,fact=None):
    
    if bl != 'None' and fact == 'None':
        ventes = Vente.objects.filter(numero_BL = bl)

    elif  bl == 'None' and fact != 'None':
        ventes = Vente.objects.filter(numero_facture = fact)

    elif bl != 'None' and fact != 'None':
        ventes = Vente.objects.filter(numero_BL = bl, numero_facture=fact)

    

    
    for ab in ventes:
         
        ab.paye=True
        ab.save()
        
    messages.success(request, f'Le payement à été correctement effectué pour {bl} {fact}')
    #return redirect(reverse('stock:vente_payement'))
    return HttpResponseRedirect(reverse('stock:vente_payement'))

@login_required
def vente_supprimer(request):
    selected_bl = Vente.objects.values("numero_BL","numero_facture").order_by("numero_BL","numero_facture")
    globalite = 0   
    
    if request.method == 'POST':
        if request.POST['bl'] != "None" and request.POST['fact'] == "None":
            selected_bl =  Vente.objects.filter(numero_BL=request.POST['bl'])

        elif request.POST['bl'] == "None" and request.POST['fact'] != "None":
            selected_bl =  Vente.objects.filter(numero_facture=request.POST['fact'])  

        elif request.POST['bl'] != "None" and request.POST['fact'] != "None":
            selected_bl = Vente.objects.filter(numero_BL = request.POST['bl'], numero_facture=request.POST['fact'])
        elif request.POST['bl'] == "None" and request.POST['fact'] == "None":
            messages.error (request, "Problème de filtre! vous devez choisir un BL ou une facture !! ")
            return redirect('stock:vente_supprimer')
        
        selected_bl = selected_bl.annotate( price=(F('quantite_vendu') * F('client__taux_remise') * F('produit__prix') ))

        for t in selected_bl:
                globalite = globalite + t.price
        bl = request.POST["bl"]
        fact= request.POST['fact']
        return render(request, 'vente_supp.html', {'selected_bl':selected_bl,
                                           
                                            'globalite':globalite,
                                            'bl':bl,
                                            'fact':fact,

                                                } )


    return render(request, 'vente_supp.html', {'selected_bl':selected_bl,
                                            'globalite':globalite,

                                                } )


@login_required
def suppression(request,bl=None,fact=None):
    
    if bl != 'None' and fact == 'None':
        ventes = Vente.objects.filter(numero_BL = bl)

    elif  bl == 'None' and fact != 'None':
        ventes = Vente.objects.filter(numero_facture = fact)

    elif bl != 'None' and fact != 'None':
        ventes = Vente.objects.filter(numero_BL = bl, numero_facture=fact)

    

    
    for ab in ventes:
        prd = get_object_or_404(Produit,nom_produit=ab.produit.nom_produit)
        prd.quantite_stock = prd.quantite_stock+ab.quantite_vendu
        prd.save()
        ab.delete()
        
    messages.success(request, f'La vente à été correctement supprimé pour {bl} {fact}')
    #return redirect(reverse('stock:vente_payement'))
    return HttpResponseRedirect(reverse('stock:vente_supprimer'))


@login_required
def export_ventes_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="ventes.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('ventes')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['client__nom_client', 'produit__nom_produit','date_vente', 'numero_BL','numero_facture','quantite_vendu','prix_vente','remise','moyen_payement','paye','gratuit',]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = Vente.objects.all().values_list('client__nom_client', 'produit__nom_produit','date_vente', 'numero_BL','numero_facture','quantite_vendu','produit__prix','client__taux_remise','moyen_payement','paye','gratuit')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response      

@login_required
def export_produits_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="produits.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('produits')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['nom_produit', 'seuil', 'quantite_stock','prix',]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = Produit.objects.all().values_list('nom_produit', 'seuil', 'quantite_stock','prix')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response      


@staff_member_required
def vente_max_produit(request,period=None):
    ventes = Vente.objects.all()
    ventestot = Vente.objects.all()

    yesterday = date.today() - timedelta(days=1)
    week = ExtractWeek(date.today())
    month= ExtractMonth(date.today())
    year = ExtractYear(date.today())
    
    if period == '1' :
        ventes = ventes.filter(date_vente = date.today() )
        ventestot = ventestot.filter(date_vente = date.today() )
    elif period == '2' :
        ventes = ventes.filter(date_vente = yesterday )
        ventestot = ventestot.filter(date_vente = yesterday )
    elif period == '3' :
        ventes = ventes.filter(date_vente__week = week, date_vente__month = month ,date_vente__year = year )
        ventestot = ventestot.filter(date_vente__week = week, date_vente__month = month ,date_vente__year = year )


    elif period == '4' :
        ventes = ventes.filter(date_vente__month = month,date_vente__year = year ) 
        ventestot = ventestot.filter(date_vente__month = month,date_vente__year = year ) 
    elif period == '5' :
        ventes = ventes.filter(date_vente__year = year )
        ventestot = ventestot.filter(date_vente__year = year )

    ventes = ventes.order_by('produit__nom_produit','client__nom_client').values('produit__nom_produit','client__nom_client').annotate(AcSum= Sum('quantite_vendu'))
    ventes=ventes.order_by('-AcSum')
    max = ventes.order_by('-AcSum')[:1]
   
    ventestot = ventestot.order_by('produit__nom_produit').values('produit__nom_produit').annotate(AcSum= Sum('quantite_vendu'))
    ventestot=ventestot.order_by('-AcSum')
    
    return render(request, 'vente_max_produit.html', {'ventes':ventes,
                                                'nambir': ventes.count(),
                                            'max':max,
                                           'ventestot':ventestot
                                                } )
