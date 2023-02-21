from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import pre_delete
from django.dispatch import receiver

class Produit(models.Model):
    nom_produit = models.CharField(max_length=200,unique = True)
    #slug = models.SlugField(max_length=200)
    image = models.ImageField(upload_to='products/%Y/%m/%d',blank=True)
    description = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=10,decimal_places=3)
    quantite_stock = models.PositiveIntegerField(default=0,blank=True, null=True)
    seuil = models.PositiveIntegerField(default=0,blank=True, null=True)

    class Meta:
        ordering = ['nom_produit']
        indexes = [

models.Index(fields=['nom_produit']),
models.Index(fields=['quantite_stock']),
]
    def __str__(self):
        return self.nom_produit
    def get_absolute_url(self):
        return reverse('stock:produit_detail', args=[self.id])
    def diminuer(self, qte):
        self.quantite_stock -= qte
        self.save()



class Delegue(models.Model):
    zone = (
  ('Nord', 'Nord'),
  ('Centre', 'Centre'),
  ('Sfax', 'Sfax'),
  ('Sud', 'Sud'),
 )
    nom_delegue = models.CharField(max_length=200,unique = True)
    base = models.CharField(max_length=10, choices=zone, default='nord')

    class Meta:
        ordering = ['nom_delegue']
        indexes = [

models.Index(fields=['nom_delegue']),

]
    def __str__(self):
        return self.nom_delegue

    def get_absolute_url(self):
        return reverse('stock:delegue_detail', args=[self.id])

    
class Client(models.Model):

    type = (
  ('Pharmacie', 'Pharmacie'),
  ('Grossiste', 'Grossiste'),

 )

    zone = (
  ('Nord', 'Nord'),
  ('Centre', 'Centre'),
  ('Sfax', 'Sfax'),
  ('Sud', 'Sud'),
 )
    nom_client = models.CharField(max_length=200,unique = True)
    #slug = models.SlugField(max_length=200)
    description = models.TextField(blank=True)
   
   
    base_client = models.CharField(max_length=10, choices=zone, default='nord')
    type_client = models.CharField(max_length=10, choices=type, default='grossiste')
    taux_remise =   models.DecimalField(max_digits=10,decimal_places=0,blank=True, null=True,default=0)


    class Meta:
        ordering = ['nom_client']
        indexes = [
models.Index(fields=['id', ]),
models.Index(fields=['nom_client']),

]
    def __str__(self):
        return self.nom_client
    def get_absolute_url(self):
        return reverse('stock:client_detail', args=[self.id])


class Contactclient(models.Model):
    client = models.ForeignKey(Client,on_delete=models.PROTECT,related_name='contacts')
    nom_contact = models.CharField(max_length=100)
    fonction_contact = models.CharField(max_length=100)
    telephone_contact = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.nom_contact} {self.fonction_contact} {self.client.nom_client}"

class RemiseClient(models.Model)   :
    
        
    PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]
    client= models.ForeignKey(Client,on_delete=models.PROTECT,related_name='remiseclient') 
    taux_remise = models.DecimalField(max_digits=3, decimal_places=0, default=0, validators=PERCENTAGE_VALIDATOR)
    date_remise = models.DateField(auto_now_add=True)
    class Meta:
        ordering = ['date_remise']
    def save(self, *args, **kwargs):
        self.client.taux_remise = self.taux_remise 
        self.client.save()
        super(RemiseClient,self).save(*args, **kwargs)
    def delete(self):
        ab= Client.objects.get(pk=self.client.id)

        super(RemiseClient, self).delete()
        ab=ab.remiseclient.all()
        if ab:
            self.client.taux_remise = ab.last().taux_remise
        else:
            self.client.taux_remise = 0
        self.client.save()


    def __str__(self):
        return f" {self.client.nom_client} - remise {self.taux_remise}% "

class VisiteMedicale(models.Model):
    delegue= models.ForeignKey(Delegue,on_delete=models.PROTECT,related_name='visitemedicaleDelegue')
    produit = models.ForeignKey(Produit,on_delete=models.PROTECT,related_name='visitemedicaleProduit')
    date = models.DateField(auto_now_add=True)
    quantite_donne = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['date']
    def __str__(self):
        return f"{self.delegue.nom_delegue} à bénéficié de {self.produit.nom_produit} du produit {self.quantite_donne}"
    def save(self, *args, **kwargs):
        
        if self.quantite_donne > self.produit.quantite_stock:
            raise ValidationError(f"ATTENTION !! Vous avez seulement {self.produit.quantite_stock} en stock !!")
        else:
            b=Produit.objects.get(nom_produit = self.produit.nom_produit)
            b.quantite_stock =  b.quantite_stock - self.quantite_donne
            b.save(update_fields=["quantite_stock"])
            super().save(*args, **kwargs)


class Vente(models.Model):
    payement = (
  ('chèque', 'chèque'),
  ('traite', 'traite'),
  ('espèces', 'espèces'),
  ('gratuit', 'gratuit'),
 ) 

    client= models.ForeignKey(Client,on_delete=models.PROTECT,related_name='venteclient')
    produit = models.ForeignKey(Produit,on_delete=models.PROTECT,related_name='venteproduit')
    numero_BL = models.CharField(max_length=200,blank=True, null=True)
    numero_facture = models.CharField(max_length=200,blank=True, null=True)
    quantite_vendu = models.PositiveIntegerField(default=0)
    montant_remise = models.DecimalField(max_digits=10,decimal_places=3,blank=True, null=True,default=0)
    prix = models.DecimalField(max_digits=10,decimal_places=3,blank=True, null=True,default=0)
    date_vente = models.DateField(auto_now_add=True,blank=True, null=True)
    moyen_payement = models.CharField(max_length=20,choices=payement,default="espèces")
    paye = models.BooleanField(default=False)
    gratuit = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('stock:vente_detail', args=[self.client.nom_client,self.date_vente,self.numero_BL,
                       self.numero_facture])

    def __str__(self):
        return f"{self.client.nom_client} à acheté {self.quantite_vendu} du produit {self.produit.nom_produit}"
    
    class Meta:
        ordering = ['-date_vente']
    


    def save(self, *args, **kwargs):
        if self.gratuit and self.moyen_payement != "gratuit" :
            raise ValidationError(f"quand gratuit est coché le moyen de payement doit être gratuit")
        elif not self.gratuit and self.moyen_payement == "gratuit" :
            raise ValidationError(f"Quand le moyen de payement est gratuit la case gratuit doit être cochée")
        super().save(*args, **kwargs)

            

        


            



class Alimenter_stock(models.Model):
    produit = models.ForeignKey(Produit,on_delete=models.PROTECT,related_name='alimenterproduit')
    quantite_entree = models.PositiveIntegerField(default=0)
    date_entree = models.DateField(auto_now_add=True)
    def __str__(self):
        return f"le stock de {self.produit.nom_produit} augmenté de  {self.quantite_entree}"
    def save(self, *args, **kwargs):
        b=Produit.objects.get(nom_produit = self.produit.nom_produit)
        b.quantite_stock =  b.quantite_stock + self.quantite_entree
        b.save(update_fields=["quantite_stock"])
        super().save(*args, **kwargs)