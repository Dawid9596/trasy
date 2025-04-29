from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from .models import ObrazTla, Trasa, PunktTrasy

class TrasaAPITests(APITestCase):
    def setUp(self):
        # Utwórz użytkownika testowego
        self.user = User.objects.create_user(username='testuser', password='password123')
        # Utwórz token dla użytkownika
        self.token = Token.objects.create(user=self.user)
        # Utwórz obraz tła testowy
        self.obraz_tla = ObrazTla.objects.create(
            nazwa="Test Tło",
            opis="Testowe tło do API",
            szerokosc=800,
            wysokosc=600
        )
        # Utwórz trasę testową
        self.trasa = Trasa.objects.create(
            nazwa="Test Trasa",
            opis="Testowa trasa dla API",
            uzytkownik=self.user,
            obraz_tla=self.obraz_tla
        )
        # Dodaj punkty testowe
        self.punkt1 = PunktTrasy.objects.create(trasa=self.trasa, x=100, y=100, kolejnosc=1)
        self.punkt2 = PunktTrasy.objects.create(trasa=self.trasa, x=200, y=200, kolejnosc=2)
        
        # Ustaw klienta API z uwierzytelnianiem
        self.client = APIClient()
        # self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.client.force_authenticate(user=self.user)
    
    def test_get_trasy_list(self):
        """
        Test pobierania listy tras użytkownika
        """
        url = reverse('trasa-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_trasa(self):
        """
        Test tworzenia nowej trasy
        """
        url = reverse('trasa-list')
        data = {
            'nazwa': 'Nowa Trasa API',
            'opis': 'Utworzona przez API',
            'obraz_tla': self.obraz_tla.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Trasa.objects.count(), 2)
    
    def test_get_punkty_trasy(self):
        """
        Test pobierania punktów trasy
        """
        url = reverse('punkty-list', kwargs={'trasa_id': self.trasa.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # print(response.content)
        self.assertEqual(len(response.data), 4)
    
    def test_add_punkt_to_trasa(self):
        """
        Test dodawania nowego punktu do trasy
        """
        
        # breakpoint()
        url = reverse('punkty-list', kwargs={'trasa_id': self.trasa.id})
        # url = f'/api/trasy/{self.trasa.id}/punkty/'
        data = {
            'x': 300,
            'y': 300,
            'kolejnosc': 3
        }
        
        # Print full URL for debugging
        # print(f"Testing URL: {url}")
        
        response = self.client.post(url, data, format='json')
        
        # Print response details for debugging
        # print(f"Status code: {response.status_code}")
        # print(f"Response content: {response.content}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PunktTrasy.objects.filter(trasa=self.trasa).count(), 3)
    
    def test_delete_punkt(self):
        """
        Test usuwania punktu z trasy
        """
        url = reverse('punkt-detail', kwargs={'trasa_id': self.trasa.id, 'pk': self.punkt1.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PunktTrasy.objects.filter(trasa=self.trasa).count(), 1)