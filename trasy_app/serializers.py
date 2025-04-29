from rest_framework import serializers
from .models import ObrazTla, Trasa, PunktTrasy
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ObrazTlaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObrazTla
        fields = ['id', 'nazwa', 'opis', 'obraz', 'szerokosc', 'wysokosc', 'data_dodania']
        read_only_fields = ['data_dodania']

class PunktTrasySerializer(serializers.ModelSerializer):
    class Meta:
        model = PunktTrasy
        fields = ['id', 'x', 'y', 'kolejnosc', 'trasa']
        read_only_fields = ['trasa']

class TrasaSerializer(serializers.ModelSerializer):
    punkty = PunktTrasySerializer(many=True, read_only=True)
    obraz_tla_details = ObrazTlaSerializer(source='obraz_tla', read_only=True)
    
    class Meta:
        model = Trasa
        fields = ['id', 'nazwa', 'opis', 'uzytkownik', 'obraz_tla', 'obraz_tla_details', 
                  'data_utworzenia', 'data_modyfikacji', 'punkty']
        read_only_fields = ['uzytkownik', 'data_utworzenia', 'data_modyfikacji']

    def create(self, validated_data):
        # Przypisanie zalogowanego użytkownika jako właściciela trasy
        validated_data['uzytkownik'] = self.context['request'].user
        return super().create(validated_data)