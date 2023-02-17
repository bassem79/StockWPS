from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


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
    fonction1= models.CharField(max_length=70,blank=True, null=True)
    telephone1 = models.CharField(max_length=20,blank=True, null=True)
    fonction2= models.CharField(max_length=70,blank=True, null=True)
    telephone2 = models.CharField(max_length=20,blank=True, null=True)
    fonction3= models.CharField(max_length=70,blank=True, null=True)
    telephone3 = models.CharField(max_length=20,blank=True, null=True)
    fonction4= models.CharField(max_length=70,blank=True, null=True)
    telephone4 = models.CharField(max_length=20,blank=True, null=True)
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

class VisiteMedicale(models.Model):
    delegue= models.ForeignKey(Delegue,on_delete=models.CASCADE,related_name='visitemedicaleDelegue')
    produit = models.ForeignKey(Produit,on_delete=models.CASCADE,related_name='visitemedicaleProduit')
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