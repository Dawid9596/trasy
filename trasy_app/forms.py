from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Trasa, PunktTrasy, ObrazTla

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class TrasaForm(forms.ModelForm):
    class Meta:
        model = Trasa
        fields = ['nazwa', 'opis', 'obraz_tla']

class PunktTrasyForm(forms.ModelForm):
    class Meta:
        model = PunktTrasy
        fields = ['x', 'y']
        
    def __init__(self, *args, **kwargs):
        self.trasa = kwargs.pop('trasa', None)
        super(PunktTrasyForm, self).__init__(*args, **kwargs)
        
    def save(self, commit=True):
        punkt = super(PunktTrasyForm, self).save(commit=False)
        if self.trasa:
            punkt.trasa = self.trasa
            # Ustaw kolejność punktu na ostatni + 1
            ostatni_punkt = PunktTrasy.objects.filter(trasa=self.trasa).order_by('-kolejnosc').first()
            punkt.kolejnosc = 1 if not ostatni_punkt else ostatni_punkt.kolejnosc + 1
        
        if commit:
            punkt.save()
        return punkt