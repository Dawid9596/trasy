from django.contrib import admin
from .models import ObrazTla, Trasa, PunktTrasy

class PunktTrasynline(admin.TabularInline):
    model = PunktTrasy
    extra = 0

@admin.register(ObrazTla)
class ObrazTlaAdmin(admin.ModelAdmin):
    list_display = ('nazwa', 'szerokosc', 'wysokosc', 'data_dodania')
    search_fields = ('nazwa', 'opis')

@admin.register(Trasa)
class TrasaAdmin(admin.ModelAdmin):
    list_display = ('nazwa', 'uzytkownik', 'obraz_tla', 'data_utworzenia', 'data_modyfikacji')
    list_filter = ('uzytkownik', 'obraz_tla', 'data_utworzenia')
    search_fields = ('nazwa', 'opis')
    inlines = [PunktTrasynline]

@admin.register(PunktTrasy)
class PunktTrasyAdmin(admin.ModelAdmin):
    list_display = ('trasa', 'kolejnosc', 'x', 'y')
    list_filter = ('trasa',)