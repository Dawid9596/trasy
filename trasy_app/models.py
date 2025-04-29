from django.db import models
from django.contrib.auth.models import User

class ObrazTla(models.Model):
    nazwa = models.CharField(max_length=100)
    opis = models.TextField(blank=True)
    obraz = models.ImageField(upload_to='tla/')
    szerokosc = models.IntegerField()
    wysokosc = models.IntegerField()
    data_dodania = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nazwa
    
    class Meta:
        verbose_name = "Obraz tła"
        verbose_name_plural = "Obrazy tła"

class Trasa(models.Model):
    nazwa = models.CharField(max_length=100)
    opis = models.TextField(blank=True)
    uzytkownik = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trasy')
    obraz_tla = models.ForeignKey(ObrazTla, on_delete=models.CASCADE, related_name='trasy')
    data_utworzenia = models.DateTimeField(auto_now_add=True)
    data_modyfikacji = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.nazwa} ({self.uzytkownik.username})"
    
    class Meta:
        verbose_name = "Trasa"
        verbose_name_plural = "Trasy"

class PunktTrasy(models.Model):
    trasa = models.ForeignKey(Trasa, on_delete=models.CASCADE, related_name='punkty')
    x = models.IntegerField()
    y = models.IntegerField()
    kolejnosc = models.IntegerField()
    
    def __str__(self):
        return f"Punkt {self.kolejnosc} trasy {self.trasa.nazwa} ({self.x}, {self.y})"
    
    class Meta:
        verbose_name = "Punkt trasy"
        verbose_name_plural = "Punkty trasy"
        ordering = ['kolejnosc']