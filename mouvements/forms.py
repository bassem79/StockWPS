from django import forms
from .models import *
from django.forms.formsets import BaseFormSet
from django.forms.models import inlineformset_factory, formset_factory, modelformset_factory
from django.contrib.admin.widgets import AdminDateWidget

class delegueAjoutForm(forms.ModelForm):
    class Meta:
        model = Delegue
        fields = '__all__'

class VisiteAjoutForm(forms.ModelForm):
    class Meta:
        model = VisiteMedicale
        fields = '__all__'


class produitAjoutForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = '__all__'


class AlimenterForm(forms.ModelForm):
    class Meta:
        model = Alimenter_stock
        fields = ['quantite_entree',]



class clientAjoutForm(forms.ModelForm):
    class Meta:
        model = Client
        exclude = ['taux_remise',]



class remiseAjoutForm(forms.ModelForm):
    class Meta:
        model = RemiseClient
        fields = '__all__'

class Entetevente(forms.ModelForm):
        class Meta:
            model = Vente
            fields = ['client','numero_BL','numero_facture','moyen_payement','paye','gratuit']
        # def clean_bl(self):
        #     cd = self.cleaned_data
        #     if cd['numero_BL'] is None and cd["numero_facture"] is None: 
        #         raise forms.ValidationError("Erreur il faut remplir au moins le champs Numéro BL")

class ContactclientForm(forms.ModelForm):
    class Meta:
        model = Contactclient
        fields = '__all__'







class LinkForm(forms.Form):
    def __init__(self, *args, **kwargs):
        nom_produit = forms.CharField()
        quantite_vendu = forms.IntegerField()
        super(LinkForm, self).__init__(*args, **kwargs)
       
        self.fields["nom_produit"] = forms.ModelChoiceField(empty_label="--Choisir un produit--",\
        queryset=Produit.objects.all())
        self.fields["quantite_vendu"] = forms.IntegerField()


# class choix_bl(forms.Form):
#     def __init__(self, *args, **kwargs):
#         Numero_BL = forms.CharField()
#         Numero_Facture = forms.CharField()
#         super(choix_bl, self).__init__(*args, **kwargs)
       
#         self.fields["Numero_BL"] = forms.ModelChoiceField(empty_label="--Choisir un BL--",\
#         queryset=Vente.objects.filter(paye=False,gratuit=False).order_by("numero_BL").distinct().values('numero_BL'),to_field_name="numero_BL")
#         self.fields["Numero_Facture"] = forms.ModelChoiceField(empty_label="--Choisir une facture--",\
#         queryset=Vente.objects.filter(paye=False,gratuit=False).order_by("numero_facture").distinct().values('numero_facture'))







class BaseLinkFormSet(BaseFormSet):
    def clean(self):
        """
        Adds validation to check that no two links have the same anchor or URL
        and that all links have both an anchor and URL.
        """
        if any(self.errors):
            return

        anchors = []
        urls = []
        duplicates = False

        for form in self.forms:
            if form.cleaned_data:
                dona = form.cleaned_data.get('nom_produit')
                # univ = dona.univ
                anchor = dona.nom_produit
                # Check that no two links have the same anchor or URL
                if anchor :
                    if anchor in anchors:
                        duplicates = True
                    anchors.append(anchor)

                    # if url in urls:
                    #     duplicates = True
                    # urls.append(url)

                if duplicates:
                    raise forms.ValidationError(
                        'Vous ne pouvez choisir le même produit plusiuers fois.',
                        code='duplicate_etab'
                    )

    def __init__(self, *args, **kwargs):
        super(BaseLinkFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False


class Pwd_initForm(forms.Form):
    Email = forms.EmailField()

class LoginForm(forms.Form):
    nom_d_utilisateur = forms.CharField()
    mot_de_passe = forms.CharField(widget=forms.PasswordInput)

class changepwd(forms.Form):
    Ancien_mot_de_passe = forms.CharField()
    Nouveau_mot_de_passe = forms.CharField(widget=forms.PasswordInput)
    Confirmer_nouveau_mot_de_passe = forms.CharField(widget=forms.PasswordInput)


class FDate(forms.Form):
    dd = forms.DateInput(attrs={'class':'form-control', 'type':'date'}),
    df = forms.DateInput(attrs={'class':'form-control', 'type':'date'}),


    def clean(self):
        cleaned_data = super(FDate, self).clean()
        date_debut = cleaned_data.get("dd")
        date_fin = cleaned_data.get("df")
        return cleaned_data