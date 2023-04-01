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
from django.db.models import ProtectedError

def dashboard(request):
    seuil = Produit.objects.filter(quantite_stock__lte = F('seuil'))
    query = request.GET.get('q')
    request.session['recherche'] = query
    if query:
        prd=Produit.objects.filter(
            Q(nom_produit__icontains=query)|
            Q(seuil__icontains=query)|
            Q(quantite_stock__icontains=query)|
            Q(prix__icontains=query)
            ).distinct()

        clt=Client.objects.filter(
            Q(nom_client__icontains=query)|
            Q(base_client__icontains=query)|
            Q(taux_remise__icontains=query)|
            Q(type_client__icontains=query)
            ).distinct()

        cont=Contactclient.objects.filter(
            Q(nom_contact__icontains=query)|
            Q(fonction_contact__icontains=query)
            ).distinct()
        dele=Delegue.objects.filter(
            Q(nom_delegue__icontains=query)|
            Q(base__icontains=query)
            ).distinct()        
        


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
    messages.success(request, f'Vous avez été deconnecté')
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
                    return redirect(reverse('stock:connexion'))
    else:
        form = changepwd()
    return render(request, 'change_password.html', {'form': form})






def rechercheContact(request):
    cont = Contactclient.objects.all()

    if request.session.get('recherche', None):     
        cont = cont.filter(
            Q(nom_contact__icontains=request.session['recherche'])|
            Q(fonction_contact__icontains=request.session['recherche'])
            ).distinct()
        del request.session['recherche']
    return render(request, 'contacts_list.html', {
                                                'sel':cont,                                        
                                                   })

        

@login_required
def alimenterStock(request,prd):
    prd = get_object_or_404(Produit,id = prd)
    his= prd.alimenterproduit.all()
    alim= None
    if request.method == 'POST':
        form = AlimenterForm(request.POST)
        if form.is_valid():
            alim= form.save(commit=False)
            alim.produit=prd
            alim.save()
            messages.success(request,f'Alimentation du stock ajoutée avec succés')
            
            return redirect('stock:produit_list')
    else:
        form= AlimenterForm(initial={'produit':prd.id})
    
    return render(request, 'produit_alimenter.html', {'form': form,
                                                        'prd':prd,
                                                        'his':his,
   
                                                   }) 

@login_required
def delegue_list(request,zone = None):
    delegue = Delegue.objects.all()
    
    if request.session.get('recherche', None): 
        delegue=delegue.filter(
            Q(nom_delegue__icontains=request.session['recherche'])|
            Q(base__icontains=request.session['recherche'])
            ).distinct()
        del request.session['recherche']
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
    selected_prd = Produit.objects.all()


    

    return render(request, 'delegue_detail.html', {'delegue': delegue,
                                                     'echantillon': echantillon,
                                                     'echantillon2': echantillon2,
                                                     'total': total,
                                                    'selected_prd': selected_prd,     })



@login_required
def delegue_detail_filtre(request, id):
    total=VisiteMedicale.objects.filter(delegue=id)

    if request.POST['dd']  :
        total=total.filter(date__gte = request.POST['dd']) 

    if request.POST['df']  :
        total=total.filter(date__lte = request.POST['df']) 

    if request.POST['prd']  != "None" :
        total=total.filter(produit__nom_produit = request.POST['prd'])   
        
    return render(request, 'delegue_detail_filtre.html', { 'total': total,
                                                       })


@method_decorator(login_required, name='dispatch')
class delegue_ajouter(CreateView):
    model = Delegue
    form_class = delegueAjoutForm
    template_name = "delegue_ajouter.html"
    def get_success_url(self):
        messages.success(self.request,f'Délégué ajouté avec succés')
        return (reverse('stock:delegue_list'))

@method_decorator(login_required, name='dispatch')
class delegue_supprimer(DeleteView):
    model = Delegue
    #success_url ="stock:delegue_list"
    template_name = "delegue_supprimer.html"


    
    def get_success_url(self):
        messages.success(self.request,f'Délégué supprimé avec succés')
        return (reverse('stock:delegue_list'))
    
    
@method_decorator(login_required, name='dispatch')
class produit_supprimer(DeleteView):
    model = Produit
    
    template_name = "produit_supprimer.html"
    def get_success_url(self):
        messages.success(self.request,f'Produit supprimé avec succés')
        return (reverse('stock:produit_list'))
    
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
                messages.success(request, f'Opération effectué avec succés')
                return redirect(reverse("stock:delegue_list"))
        
    else:
        form = VisiteAjoutForm()

    return render(request, 'Visite_ajouter.html', locals())           


@method_decorator(login_required, name='dispatch')
class visite_supprimer(DeleteView):
    model = VisiteMedicale
    
    template_name = "visite_supprimer.html"
    def get_success_url(self):
        messages.success(self.request,f'Echantillons supprimés avec succés')
        return (reverse_lazy('stock:delegue_list'))



def remises_list(request,clt):
    clt =get_object_or_404(Client,nom_client=clt)
    sel = clt.remiseclient.all()
    return render(request, 'remise_list.html', {'clt':clt,
                                                'sel':sel,                                        
                                                   })

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
                if client.taux_remise != 0:
                    prix = quantite_vendu * (1-client.taux_remise/100) * tmp.prix
                    montant_remise = quantite_vendu * tmp.prix - prix
                else:
                    prix = quantite_vendu  * tmp.prix
                    montant_remise = 0

                new_links.append(Vente(client = client,numero_BL=numero_BL, numero_facture=numero_facture,  \
                moyen_payement=moyen_payement,paye=paye,gratuit=gratuit,produit=produit, \
                quantite_vendu= quantite_vendu,prix=prix,montant_remise=montant_remise ))
                
    
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
                    messages.success(request, f'Votre vente à été correctement saisie.')
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
    prd = Produit.objects.all()
    clt=Client.objects.all()
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
    
    postss = ventes.filter(gratuit=True).order_by('-date_vente')
    # ventes = ventes.annotate(total_produit=( Cast('quantite_vendu',output_field=IntegerField()) * Cast('client__taux_remise',output_field=DecimalField())  )) 
    ventes= ventes.exclude(gratuit=True ).order_by("numero_BL","numero_facture")
    
    # ventes = ventes.annotate( price=(F('quantite_vendu') * F('client__taux_remise') * F('produit__prix') ))
    somme = ventes.aggregate(Sum('prix'))['prix__sum'] or 0.000

    # ventes = ventes.annotate(
    # total=ExpressionWrapper(
    #     F('quantite_vendu') * F('client__taux_remise') * F('produit__prix'), output_field=DecimalField()))
    # ventes = ventes.annotate( price = Case( \
    #     When (produit__prix__isnull =  True , then= (F('quantite_vendu')  * F('produit__prix'))),
    #     When (produit__prix__gt =  0, then= (F('quantite_vendu') * F('client__taux_remise') * F('produit__prix'))),
    #     # default= (F('quantite_vendu')  * F('produit__prix')),
        
    #     output_field=DecimalField()))

    ventesnp = ventes.exclude(paye=True).order_by('-date_vente')
    sommenp = ventesnp.aggregate(Sum('prix'))['prix__sum'] or 0.00
    ventes = ventes.order_by('-date_vente')

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
                                                'prd':prd,
                                                'clt':clt,
                                                   'ventesnp':ventesnp,
                                                   'sommenp':sommenp,
                                                    'somme': somme,
                                                    'postss':postss,
                                                   })


@login_required
def vente_list_filtre(request):
    
    total=Vente.objects.all()

    if request.POST['dd']  :
        total=total.filter(date_vente__gte = request.POST['dd']) 

    if request.POST['df']  :
        total=total.filter(date_vente__lte = request.POST['df']) 

    if request.POST['prd']  != "None" :
        total=total.filter(produit__nom_produit = request.POST['prd'])   
    if request.POST['clt']  != "None" :
        total=total.filter(client__nom_client = request.POST['clt'])   
        
    
    gratuit=total.filter(gratuit=True)
    total=total.exclude(gratuit=True)
    totalnp = total.filter(paye=False)
    somme = total.aggregate(Sum('prix'))['prix__sum'] or 0.00
    sommenp = totalnp.aggregate(Sum('prix'))['prix__sum'] or 0.00
        
    return render(request, 'vente_list_filtre.html', { 'total': total,
                                                      'totalnp' : totalnp,
                                                      'somme':somme,
                                                      'sommenp':sommenp,
                                                      'gratuit' : gratuit,
                                                      'nambir' : total.count()
                                                       })    

@staff_member_required
def vente_detail(request, bl,facture):

    if bl != "None" and facture == "None":
        ventes =  Vente.objects.filter(numero_BL=bl)

    elif bl == "None" and facture != "None":
        ventes =  Vente.objects.filter(numero_facture=facture)  

    elif bl != "None" and facture != "None":
        ventes = Vente.objects.filter(numero_BL = bl, numero_facture=facture)
    
   
    ventes = ventes.exclude(gratuit=True)
    somme = ventes.aggregate(Sum('prix'))['prix__sum'] or 0.000
    

   

    return render(request, 'vente_detail.html', {'ventes': ventes,           
                                                 'somme': somme ,                                              
                                                   })

@login_required
def produit_list(request):
    prd = Produit.objects.all()
    

    if request.session.get('recherche', None): 
        prd=Produit.objects.filter(
            Q(nom_produit__icontains=request.session['recherche'])|
            Q(seuil__icontains=request.session['recherche'])|
            Q(quantite_stock__icontains=request.session['recherche'])|
            Q(prix__icontains=request.session['recherche'])
            ).distinct()
    
        del request.session['recherche']
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
        messages.success(self.request,f'Produit ajouté avec succés')
        return (reverse('stock:produit_list'))


@login_required
def contacts_list(request,clt):
    clt =get_object_or_404(Client,nom_client=clt)
    

    sel = clt.contacts.all()
    return render(request, 'contacts_list.html', {'clt':clt,
                                                'sel':sel,                                        
                                                   })


@login_required
def contact_ajouter_clt(request,id):
    clt=get_object_or_404(Client,id=id)
    rem= None
    if request.method == 'POST':
        form = ContactclientForm(request.POST)
        if form.is_valid():
            rem= form.save(commit=False)
            rem.client=clt
            rem.save()
            messages.success(request,f'Contact ajoutée avec succés')
            
            return redirect('stock:client_list')
    else:
        form= ContactclientForm(initial={'client':clt.id})
    
    return render(request, 'contact_ajouter.html', {'form': form,
   
   
                                                   }) 

@method_decorator(login_required, name='dispatch')
class contact_ajouter(CreateView):
    model = Contactclient
    form_class = ContactclientForm
    template_name = "contact_ajouter.html"
    success_message = "%(contact)s ajouté avec succés"
    def get_success_url(self):
        messages.success(self.request,f'Contact ajouté avec succés')
        return (reverse('stock:client_list'))
    
@method_decorator(login_required, name='dispatch')
class contactUpdateView(UpdateView):
    # specify the model you want to use
    model = Contactclient

    fields = [
        
        
        "nom_contact",
        "fonction_contact",
        "telephone_contact",
        
    ]
    template_name = "contact_modifier.html"
    context_object_name = "del"
    def get_success_url(self):
        messages.success(self.request,f'Contact mis à jour avec succés')
        return (reverse('stock:client_list'))

@method_decorator(login_required, name='dispatch')
class contactDeleteView(DeleteView):
    model = Contactclient
    template_name = "contact_effacer.html"
    def get_success_url(self):
        messages.success(self.request,f'Contact supprimé avec succés')
        return (reverse('stock:client_list'))



@login_required
def remise_ajouter_clt(request,id):
    clt=get_object_or_404(Client,id=id)
    rem= None
    if request.method == 'POST':
        form = remiseAjoutForm(request.POST)
        if form.is_valid():
            rem= form.save(commit=False)
            rem.client=clt
            rem.save()
            messages.success(request,f'Remise ajoutée avec succés')
            
            return redirect('stock:client_list')
    else:
        form= remiseAjoutForm(initial={'client':clt.id})
    
    return render(request, 'remise_ajouter.html', {'form': form,
   
   
                                                   }) 


@method_decorator(login_required, name='dispatch')
class remise_ajouter(CreateView):
    model = RemiseClient
    form_class = remiseAjoutForm
    template_name = "remise_ajouter.html"
    def get_success_url(self):
        messages.success(self.request,f'Remise ajouté avec succés')
        return (reverse('stock:client_list'))

@login_required
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
        messages.success(self.request,f'Produit mis à jour avec succés')
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



@login_required
def client_list(request):
    clt = Client.objects.all()
    
    
    
    if request.session.get('recherche', None): 
        clt=clt.filter(
            Q(nom_client__icontains=request.session['recherche'])|
            Q(base_client__icontains=request.session['recherche'])|
            Q(taux_remise__icontains=request.session['recherche'])|
            Q(type_client__icontains=request.session['recherche'])
            ).distinct()
    
        del request.session['recherche']
    paginator = Paginator(clt, 10) # 5 posts in each page
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request, 'client_list.html', {'page': page,
                                                 'nambir': clt.count(),
                                                   'posts':posts,
                                                   }) 

@method_decorator(login_required, name='dispatch')
class client_ajouter(CreateView):
    model = Client
    form_class = clientAjoutForm
    template_name = "client_ajouter.html"
   
    def get_success_url(self):
        messages.success(self.request,f'Client ajouté avec succés')
        return (reverse('stock:client_list'))

@method_decorator(login_required, name='dispatch')
class remiseUpdateView(UpdateView):
    # specify the model you want to use
    model = RemiseClient

    fields = [
        
        
        "taux_remise",
        
    ]
    template_name = "remise_modifier.html"
    context_object_name = "del"
    def get_success_url(self):
        messages.success(self.request,f'Remise mise à jour avec succés')
        return (reverse('stock:client_list'))

@method_decorator(login_required, name='dispatch')
class delegueUpdateView(UpdateView):
    # specify the model you want to use
    model = Delegue

    fields = [
        
        "base",
        
    ]
    template_name = "delegue_modifier.html"
    context_object_name = "del"
    def get_success_url(self):
        messages.success(self.request,f'Délegué mis à jour avec succés')
        return (reverse('stock:delegue_list'))

@method_decorator(login_required, name='dispatch')    
class clientUpdateView(UpdateView):
    # specify the model you want to use
    model = Client

    fields = [
        
        "description",
        
        "base_client",
        
        "type_client"
    ]
    template_name = "client_modifier.html"
    context_object_name = "clt"
    def get_success_url(self):
        messages.success(self.request,f'Client mis à jour avec succés')
        return (reverse('stock:client_list'))

@method_decorator(login_required, name='dispatch')
class clientDeleteView(DeleteView):
    model = Client
    template_name = "client_effacer.html"
    def get_success_url(self):
        messages.success(self.request,f'Client supprimé avec succés')
        return (reverse('stock:client_list'))

@method_decorator(login_required, name='dispatch')
class remiseDeleteView(DeleteView):
    model = RemiseClient
    template_name = "remise_effacer.html"
    def get_success_url(self):
        messages.success(self.request,f'Remise supprimé avec succés')
        return (reverse('stock:client_list'))

@login_required
def produit_detail(request, id):
    form=produitAjoutForm()

    prd = get_object_or_404(Produit, id=id) 
    return render(request, 'produit_detail.html', {'prd': prd,
                                                   })



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
    somme = historique.aggregate(Sum('prix'))['prix__sum'] or 0.000
    
    historique2 = historique.exclude(paye=True)
    sommenp = historique2.aggregate(Sum('prix'))['prix__sum'] or 0.000

 
    return render(request, 'vente_client_historique.html', {'historique': historique, 
                                                 'nambir': historique.count(),
                                                 'somme': somme,
                                                 'cl':cl,
                                                 'sommenp': sommenp,
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
    somme = selected_bl.aggregate(Sum('prix'))['prix__sum'] or 0.000




    historique2 = selected_bl.exclude(paye=True)
    #historique2 = historique2.annotate( price2=(F('quantite_vendu') * F('client__taux_remise') * F('produit__prix') ))
    sommenp = historique2.aggregate(Sum('prix'))['prix__sum'] or 0.000

    return render(request, 'vente_detail_BlFact.html', {
   
            'selected_bl': selected_bl,
                                                             'nambir': selected_bl.count(),
                                                 'somme': somme,
                                             
                                                 'sommenp': sommenp,
                                                 'historique2': historique2,
                                                 'gratuite':gratuite})


 
@staff_member_required  
def vente_ca(request,period=None):
    ventes = Vente.objects.filter(gratuit=False)

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
    
    # ventes = ventes.order_by('client__nom_client').values('client__nom_client').annotate(AcSum= Sum(
    # F('quantite_vendu') * F('client__taux_remise') * F('produit__prix')

    # ))
    ventes = ventes.order_by('client__nom_client').values('client__nom_client').annotate(AcSum= Sum(
     'prix' ))
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
    return (reverse('stock:vente_payement'))

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
    return (reverse('stock:vente_supprimer'))


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


@login_required
def export_clients_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="clients.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('clients')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['nom_client', 'description','telephone', 'base_client','taux_remise',]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = Client.objects.all().values_list('nom_client', 'description','telephone', 'base_client','taux_remise')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response      


@login_required
def export_delegues_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="delegues.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('delegues')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['nom_delegue', 'base','nom echantillon', 'quantite echantillon','date']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = Delegue.objects.all().values_list('nom_delegue', 'base', 'visitemedicaleDelegue__produit__nom_produit','visitemedicaleDelegue__quantite_donne','visitemedicaleDelegue__date')
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



@staff_member_required
def vente_prd_chart(request):
    
    prd=Produit.objects.all()
    clt= Client.objects.all()
    dataset= Vente.objects.filter(gratuit=False)
    dataset = dataset.values('produit__nom_produit') \
        .annotate(totqte=Sum('quantite_vendu')) \
        .order_by('produit__nom_produit')
 
    if request.method == 'POST':

        if request.POST['dd']  :
            dataset=dataset.filter(date_vente__gte = request.POST['dd'] )
        if request.POST['df']  :
            dataset=dataset.filter(date_vente__lte = request.POST['df'] )  
        if request.POST['prd']: 
            dataset = dataset.filter(produit__nom_produit=request.POST['prd'])
        if request.POST['clt']  : 
            dataset = dataset.filter(client__nom_client=request.POST['clt'])
        return render(request, 'vente_prd_chart.html', {'dataset': dataset,'prd':prd,'clt':clt})
    return render(request, 'vente_prd_chart.html', {'dataset': dataset,'prd':prd,'clt':clt})

@staff_member_required
def vente_prd_filtre_chart(request):
    dataset= Vente.objects.filter(gratuit=False)

    dataset = dataset.values('produit__nom_produit') \
        .annotate(totqte=Sum('quantite_vendu')) \
        .order_by('produit__nom_produit')
    if request.POST['dd']  :
        dataset=dataset.filter(date_vente__gte = request.POST['dd'] )
    if request.POST['df']  :
        dataset=dataset.filter(date_vente__lte = request.POST['df'] )    

    return render(request, 'vente_prd_chart.html', {'dataset': dataset})

@staff_member_required
def vente_clt_chart(request):
    prd=Produit.objects.all()
    clt= Client.objects.all()
    dataset= Vente.objects.filter(gratuit=False)
    dataset = dataset.values('client__nom_client') \
    .annotate(totqte=Sum('prix')) \
    .order_by('client__nom_client')
       # .annotate(totqte=Sum('prix'), filter=Q(gratuit=False)) \
    if request.method == 'POST':

        if request.POST['dd']  :
            dataset=dataset.filter(date_vente__gte = request.POST['dd'] )
        if request.POST['df']  :
            dataset=dataset.filter(date_vente__lte = request.POST['df'] )  
        if request.POST['prd']: 
            dataset = dataset.filter(produit__nom_produit=request.POST['prd'])
        if request.POST['clt']  : 
            dataset = dataset.filter(client__nom_client=request.POST['clt'])
        return render(request, 'vente_clt_chart.html', {'dataset': dataset,'prd':prd,'clt':clt})
        
    return render(request, 'vente_clt_chart.html', {'dataset': dataset,'prd':prd,'clt':clt})

@staff_member_required
def vente_clt_filtre_chart(request):
    dataset= Vente.objects.filter(gratuit=False)
    dataset = dataset.values('client__nom_client') \
        .annotate(totqte=Sum('prix')) \
        .order_by('client__nom_client')
    if request.POST['dd']  :
        dataset=dataset.filter(date_vente__gte = request.POST['dd'] )
    if request.POST['df']  :
        dataset=dataset.filter(date_vente__lte = request.POST['df'] ) 
        
    return render(request, 'vente_clt_chart.html', {'dataset': dataset})


@staff_member_required
def vente_prd_evol_chart(request):
   
    prd=Produit.objects.all()
    clt= Client.objects.all()
    dataset= Vente.objects.filter(gratuit=False)
    dataset= dataset.values('date_vente') \
        .annotate(totqte=Sum('quantite_vendu'))   \
        .order_by('date_vente')
    if request.method == 'POST':
        if request.POST['prd']: 
            dataset = dataset.filter(produit__nom_produit=request.POST['prd'])
        if request.POST['clt']  : 
            dataset = dataset.filter(client__nom_client=request.POST['clt'])
        if request.POST['dd']  :
            dataset=dataset.filter(date_vente__gte = request.POST['dd'] )
        if request.POST['df']  :
            dataset=dataset.filter(date_vente__lte = request.POST['df'] )  
        
        
   
        return render(request, 'vente_prd_evol_chart.html', {'dataset': dataset,'prdd':request.POST['prd'],
                                                             
            'cltt':request.POST['clt']   , 'prd':prd,'clt':clt                                             })
    return render(request, 'vente_prd_evol_chart.html', {'dataset': dataset,'prd':prd,'clt':clt})

@staff_member_required
def vente_base_chart(request):
    
    prd=Produit.objects.all()
    clt= Client.objects.all()
    dataset = Vente.objects.filter(gratuit=False)
    dataset2 = Vente.objects.filter(gratuit=False)
    dataset = dataset.values('client__base_client','produit__nom_produit') \
        .annotate(sumqte=Sum('quantite_vendu'), filter=Q(gratuit=False)) \
        .order_by('client__base_client','produit__nom_produit')

    dataset2 = dataset2.values('client__base_client') \
        .annotate(sumqte=Sum('quantite_vendu')) \
        .order_by('client__base_client')
    if request.method == 'POST':
        if request.POST['dd']  :
            dataset=dataset.filter(date_vente__gte = request.POST['dd'] )
            dataset2=dataset2.filter(date_vente__gte = request.POST['dd'] )
        if request.POST['df']  :
            dataset=dataset.filter(date_vente__lte = request.POST['df'] )
            dataset2=dataset2.filter(date_vente__lte = request.POST['df'] )     
        if request.POST['prd']: 
            dataset = dataset.filter(produit__nom_produit=request.POST['prd'])
            dataset2 = dataset2.filter(produit__nom_produit=request.POST['prd'])
        if request.POST['clt']  : 
            dataset = dataset.filter(client__nom_client=request.POST['clt'])
            dataset2 = dataset2.filter(client__nom_client=request.POST['clt'])
        return render(request, 'vente_base_chart.html', {'dataset': dataset,'dataset2': dataset2,
                                                         'prd':prd,'clt':clt})
    

    return render(request, 'vente_base_chart.html', {'dataset': dataset,'dataset2': dataset2,
                 'prd':prd,'clt':clt                                    })
   

