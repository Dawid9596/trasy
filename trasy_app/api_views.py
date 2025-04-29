from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ObrazTla, Trasa, PunktTrasy
from .serializers import ObrazTlaSerializer, TrasaSerializer, PunktTrasySerializer
from django.shortcuts import get_object_or_404

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Własne uprawnienie pozwalające tylko właścicielom obiektu edytować go.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.uzytkownik == request.user

class ObrazTlaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint dla obrazów tła - tylko do odczytu
    """
    queryset = ObrazTla.objects.all()
    serializer_class = ObrazTlaSerializer

class TrasaViewSet(viewsets.ModelViewSet):
    """
    API endpoint dla tras - pełny CRUD dla właściciela
    """
    serializer_class = TrasaSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        # Zwracaj tylko trasy należące do zalogowanego użytkownika
        return Trasa.objects.filter(uzytkownik=self.request.user)
    
    @action(detail=True, methods=['get'], url_path='punkty-details')
    def punkty(self, request, pk=None):
        """
        Pobierz wszystkie punkty dla konkretnej trasy
        """
        trasa = self.get_object()
        punkty = PunktTrasy.objects.filter(trasa=trasa).order_by('kolejnosc')
        serializer = PunktTrasySerializer(punkty, many=True)
        return Response(serializer.data)

class PunktTrasyViewSet(viewsets.ModelViewSet):
    """
    API endpoint dla punktów trasy
    """
    serializer_class = PunktTrasySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Filtruj punkty na podstawie ID trasy, jeśli zostało podane
        trasa_id = self.kwargs.get('trasa_id')
        if trasa_id:
            return PunktTrasy.objects.filter(trasa_id=trasa_id, trasa__uzytkownik=self.request.user)
        return PunktTrasy.objects.filter(trasa__uzytkownik=self.request.user)
    
    def perform_create(self, serializer):
        # Pobierz trasę na podstawie URL-a
        trasa_id = self.kwargs.get('trasa_id')
        trasa = get_object_or_404(Trasa, id=trasa_id, uzytkownik=self.request.user)
        
        # Ustal kolejność
        ostatni_punkt = PunktTrasy.objects.filter(trasa=trasa).order_by('-kolejnosc').first()
        kolejnosc = 1 if not ostatni_punkt else ostatni_punkt.kolejnosc + 1
        
        serializer.save(trasa=trasa, kolejnosc=kolejnosc)