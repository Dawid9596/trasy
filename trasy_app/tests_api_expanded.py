from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from .models import ObrazTla, Trasa, PunktTrasy

class APIAuthenticationTests(APITestCase):
    """
    Testy sprawdzające uwierzytelnianie i autoryzację w API
    """
    
    def setUp(self):
        # Utwórz dwóch użytkowników testowych
        self.user1 = User.objects.create_user(username='apiuser1', password='apipass123')
        self.user2 = User.objects.create_user(username='apiuser2', password='apipass123')
        
        # Utwórz tokeny dla użytkowników
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)
        
        # Utwórz obraz tła testowy
        self.obraz_tla = ObrazTla.objects.create(
            nazwa="API Auth Test Tło",
            opis="Testowe tło do testów auth API",
            szerokosc=800,
            wysokosc=600
        )
        
        # Utwórz trasę testową dla user1
        self.trasa_user1 = Trasa.objects.create(
            nazwa="Trasa User1",
            opis="Testowa trasa dla User1",
            uzytkownik=self.user1,
            obraz_tla=self.obraz_tla
        )
        
        # Dodaj punkt testowy
        self.punkt_user1 = PunktTrasy.objects.create(
            trasa=self.trasa_user1,
            x=150,
            y=150,
            kolejnosc=1
        )
    
    def test_api_access_without_token(self):
        """Test dostępu do API bez tokenu"""
        url = reverse('trasa-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_api_access_with_token(self):
        """Test dostępu do API z tokenem"""
        url = reverse('trasa-list')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_token_authentication_endpoint(self):
        """Test endpointu uwierzytelniania tokenem"""
        url = reverse('api_token_auth')
        data = {
            'username': 'apiuser1',
            'password': 'apipass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)
        self.assertEqual(response.data['token'], self.token1.key)
    
    def test_user_can_access_only_own_routes(self):
        """Test, czy użytkownik może uzyskać dostęp tylko do własnych tras"""
        # Utwórz trasę dla user2
        trasa_user2 = Trasa.objects.create(
            nazwa="Trasa User2",
            opis="Testowa trasa dla User2",
            uzytkownik=self.user2,
            obraz_tla=self.obraz_tla
        )
        
        # Ustaw uwierzytelnianie dla user1
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        # Pobierz listę tras
        url = reverse('trasa-list')
        response = self.client.get(url)
        
        # Sprawdź, czy otrzymaliśmy tylko trasę użytkownika 1
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['nazwa'], "Trasa User1")


class TrasaAPIOperationsTests(APITestCase):
    """
    Testy operacji CRUD na trasach poprzez API
    """
    
    def setUp(self):
        # Utwórz użytkownika testowego
        self.user = User.objects.create_user(username='trasaapiuser', password='apipass123')
        self.token = Token.objects.create(user=self.user)
        
        # Utwórz obraz tła testowy
        self.obraz_tla = ObrazTla.objects.create(
            nazwa="API Operations Test Tło",
            opis="Testowe tło do operacji API",
            szerokosc=800,
            wysokosc=600
        )
        
        # Utwórz trasę testową
        self.trasa = Trasa.objects.create(
            nazwa="API Operations Test Trasa",
            opis="Testowa trasa dla operacji API",
            uzytkownik=self.user,
            obraz_tla=self.obraz_tla
        )
        
        # Ustaw klienta API z uwierzytelnianiem
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
    
    def test_create_new_route(self):
        """Test tworzenia nowej trasy przez API"""
        url = reverse('trasa-list')
        data = {
            'nazwa': 'Nowa Trasa API',
            'opis': 'Utworzona przez test API',
            'obraz_tla': self.obraz_tla.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nazwa'], 'Nowa Trasa API')
        
        # Sprawdź, czy trasa została utworzona w bazie danych
        self.assertTrue(
            Trasa.objects.filter(
                nazwa='Nowa Trasa API',
                uzytkownik=self.user
            ).exists()
        )
    
    def test_retrieve_route_details(self):
        """Test pobierania szczegółów trasy przez API"""
        url = reverse('trasa-detail', args=[self.trasa.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nazwa'], "API Operations Test Trasa")
        self.assertEqual(response.data['opis'], "Testowa trasa dla operacji API")
        self.assertEqual(response.data['obraz_tla'], self.obraz_tla.id)
    
    def test_update_route(self):
        """Test aktualizacji trasy przez API"""
        url = reverse('trasa-detail', args=[self.trasa.id])
        data = {
            'nazwa': 'Zaktualizowana Nazwa Trasy',
            'opis': 'Zaktualizowany opis trasy',
            'obraz_tla': self.obraz_tla.id
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Sprawdź, czy dane zostały zaktualizowane w bazie
        trasa_updated = Trasa.objects.get(id=self.trasa.id)
        self.assertEqual(trasa_updated.nazwa, 'Zaktualizowana Nazwa Trasy')
        self.assertEqual(trasa_updated.opis, 'Zaktualizowany opis trasy')
    
    def test_delete_route(self):
        """Test usuwania trasy przez API"""
        url = reverse('trasa-detail', args=[self.trasa.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Sprawdź, czy trasa została usunięta z bazy danych
        self.assertFalse(Trasa.objects.filter(id=self.trasa.id).exists())


class PunktTrasyAPITests(APITestCase):
    """
    Testy operacji na punktach trasy przez API
    """
    
    def setUp(self):
        # Utwórz użytkownika testowego
        self.user = User.objects.create_user(username='punktapiuser', password='apipass123')
        self.token = Token.objects.create(user=self.user)
        
        # Utwórz obraz tła testowy
        self.obraz_tla = ObrazTla.objects.create(
            nazwa="Punkt API Test Tło",
            opis="Testowe tło do testów punktów API",
            szerokosc=800,
            wysokosc=600
        )
        
        # Utwórz trasę testową
        self.trasa = Trasa.objects.create(
            nazwa="Punkt API Test Trasa",
            opis="Testowa trasa dla punktów API",
            uzytkownik=self.user,
            obraz_tla=self.obraz_tla
        )
        
        # Dodaj punkty testowe
        self.punkt1 = PunktTrasy.objects.create(
            trasa=self.trasa,
            x=100,
            y=100,
            kolejnosc=1
        )
        
        self.punkt2 = PunktTrasy.objects.create(
            trasa=self.trasa,
            x=200,
            y=200,
            kolejnosc=2
        )
        
        # Ustaw klienta API z uwierzytelnianiem
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
    
    def test_list_route_points(self):
        """Test pobierania listy punktów trasy przez API"""
        url = reverse('punkty-list', kwargs={'trasa_id': self.trasa.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        # breakpoint()
        self.assertEqual(response.data['results'][0]['x'], 100)
        self.assertEqual(response.data['results'][1]['x'], 200)
    
    def test_add_new_point(self):
        """Test dodawania nowego punktu do trasy przez API"""
        url = reverse('punkty-list', kwargs={'trasa_id': self.trasa.id})
        data = {
            'x': 300,
            'y': 300,
            'kolejnosc': 3
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Sprawdź, czy punkt został dodany do bazy danych
        self.assertTrue(
            PunktTrasy.objects.filter(
                trasa=self.trasa,
                x=300,
                y=300
            ).exists()
        )
        
        # Sprawdź, czy punkt ma prawidłową kolejność (3 - po istniejących punktach)
        punkt = PunktTrasy.objects.get(trasa=self.trasa, x=300, y=300)
        self.assertEqual(punkt.kolejnosc, 3)
    
    def test_retrieve_point_details(self):
        """Test pobierania szczegółów punktu przez API"""
        url = reverse('punkt-detail', kwargs={'trasa_id': self.trasa.id, 'pk': self.punkt1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['x'], 100)
        self.assertEqual(response.data['y'], 100)
        self.assertEqual(response.data['kolejnosc'], 1)
    
    def test_update_point(self):
        """Test aktualizacji punktu przez API"""
        url = reverse('punkt-detail', kwargs={'trasa_id': self.trasa.id, 'pk': self.punkt1.id})
        data = {
            'x': 150,
            'y': 150
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Sprawdź, czy dane zostały zaktualizowane w bazie
        punkt_updated = PunktTrasy.objects.get(id=self.punkt1.id)
        self.assertEqual(punkt_updated.x, 150)
        self.assertEqual(punkt_updated.y, 150)
    
    def test_delete_point(self):
        """Test usuwania punktu przez API"""
        url = reverse('punkt-detail', kwargs={'trasa_id': self.trasa.id, 'pk': self.punkt1.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Sprawdź, czy punkt został usunięty z bazy danych
        self.assertFalse(PunktTrasy.objects.filter(id=self.punkt1.id).exists())
    
    def test_api_validation_point_coordinates(self):
        """Test walidacji współrzędnych punktu w API"""
        url = reverse('punkty-list', kwargs={'trasa_id': self.trasa.id})
        data = {
            'x': 'invalid',  # Niepoprawny typ - powinien być liczbą
            'y': 300
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('x' in response.data)  # Powinien być błąd dla pola x