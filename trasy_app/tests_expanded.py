from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import ObrazTla, Trasa, PunktTrasy

class ModelRelationTests(TestCase):
    """
    Testy sprawdzające relacje między modelami
    """
    
    def setUp(self):
        # Tworzenie użytkownika testowego
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123',
            email='test@example.com'
        )
        
        # Tworzenie testowego obrazu tła
        self.obraz_tla = ObrazTla.objects.create(
            nazwa='Test Background',
            opis='Test background description',
            szerokosc=800,
            wysokosc=600,
            obraz=SimpleUploadedFile(
                "test_background.jpg",
                b"file_content",
                content_type="image/jpeg"
            )
        )
        
        # Tworzenie testowej trasy
        self.trasa = Trasa.objects.create(
            nazwa='Test Route',
            opis='Test route description',
            uzytkownik=self.user,
            obraz_tla=self.obraz_tla
        )
        
        # Dodawanie punktów do trasy
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
    
    def test_cascade_delete_user(self):
        """Test usuwania kaskadowego tras po usunięciu użytkownika"""
        trasa_id = self.trasa.id
        # Usuwamy użytkownika
        self.user.delete()
        # Sprawdzamy czy trasa została usunięta
        self.assertFalse(Trasa.objects.filter(id=trasa_id).exists())
    
    def test_cascade_delete_trasa(self):
        """Test usuwania kaskadowego punktów po usunięciu trasy"""
        punkt_id = self.punkt1.id
        # Usuwamy trasę
        self.trasa.delete()
        # Sprawdzamy czy punkt został usunięty
        self.assertFalse(PunktTrasy.objects.filter(id=punkt_id).exists())
    
    def test_punkty_ordering(self):
        """Test kolejności punktów trasy"""
        punkty = self.trasa.punkty.all()
        self.assertEqual(list(punkty), [self.punkt1, self.punkt2])


class AuthorizationTests(TestCase):
    """
    Testy sprawdzające autoryzację dostępu do zasobów
    """
    
    def setUp(self):
        # Tworzenie dwóch użytkowników
        self.user1 = User.objects.create_user(
            username='user1',
            password='password1',
            email='user1@example.com'
        )
        
        self.user2 = User.objects.create_user(
            username='user2',
            password='password2',
            email='user2@example.com'
        )
        
        # Tworzenie obrazu tła
        self.obraz_tla = ObrazTla.objects.create(
            nazwa='Auth Test Background',
            opis='Background for auth tests',
            szerokosc=800,
            wysokosc=600,
            obraz=SimpleUploadedFile(
                "auth_background.jpg",
                b"file_content",
                content_type="image/jpeg"
            )
        )
        
        # Tworzenie trasy dla użytkownika 1
        self.trasa_user1 = Trasa.objects.create(
            nazwa='User1 Route',
            opis='Route owned by user1',
            uzytkownik=self.user1,
            obraz_tla=self.obraz_tla
        )
        
        # Dodawanie punktu do trasy
        self.punkt_user1 = PunktTrasy.objects.create(
            trasa=self.trasa_user1,
            x=100,
            y=100,
            kolejnosc=1
        )
    
    def test_access_own_route(self):
        """Test dostępu do własnej trasy"""
        self.client.login(username='user1', password='password1')
        response = self.client.get(reverse('trasa_edit', args=[self.trasa_user1.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_access_other_user_route(self):
        """Test próby dostępu do trasy innego użytkownika"""
        self.client.login(username='user2', password='password2')
        response = self.client.get(reverse('trasa_edit', args=[self.trasa_user1.id]))
        self.assertEqual(response.status_code, 404)
    
    def test_delete_own_point(self):
        """Test usuwania własnego punktu trasy"""
        self.client.login(username='user1', password='password1')
        response = self.client.get(reverse('punkt_delete', args=[self.punkt_user1.id]))
        self.assertEqual(response.status_code, 302)  # Redirect po usunięciu
        self.assertFalse(PunktTrasy.objects.filter(id=self.punkt_user1.id).exists())
    
    def test_delete_other_user_point(self):
        """Test próby usunięcia punktu trasy innego użytkownika"""
        self.client.login(username='user2', password='password2')
        response = self.client.get(reverse('punkt_delete', args=[self.punkt_user1.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(PunktTrasy.objects.filter(id=self.punkt_user1.id).exists())


class RouteFunctionalityTests(TestCase):
    """
    Testy sprawdzające funkcjonalności związane z trasami
    """
    
    def setUp(self):
        # Tworzenie użytkownika
        self.user = User.objects.create_user(
            username='routeuser',
            password='routepass',
            email='route@example.com'
        )
        
        # Tworzenie obrazu tła
        self.obraz_tla = ObrazTla.objects.create(
            nazwa='Route Functionality Test Background',
            opis='Background for route functionality tests',
            szerokosc=800,
            wysokosc=600,
            obraz=SimpleUploadedFile(
                "func_background.jpg",
                b"file_content",
                content_type="image/jpeg"
            )
        )
        
        # Logowanie użytkownika
        self.client.login(username='routeuser', password='routepass')
    
    def test_create_route_form_display(self):
        """Test wyświetlania formularza tworzenia trasy"""
        response = self.client.get(reverse('trasa_create', args=[self.obraz_tla.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="nazwa"')
        self.assertContains(response, 'name="opis"')
    
    def test_route_create_success(self):
        """Test pomyślnego utworzenia trasy"""
        response = self.client.post(
            reverse('trasa_create', args=[self.obraz_tla.id]),
            {
                'nazwa': 'New Functional Test Route',
                'opis': 'Route created in functional test',
                'obraz_tla': self.obraz_tla.id
            }
        )
        
        # breakpoint()
        # Sprawdzenie przekierowania
        self.assertEqual(response.status_code, 302)
        
        # Sprawdzenie czy trasa została utworzona
        self.assertTrue(
            Trasa.objects.filter(
                nazwa='New Functional Test Route',
                uzytkownik=self.user
            ).exists()
        )
    
    def test_add_point_ajax(self):
        """Test dodawania punktu przez AJAX"""
        # Najpierw utwórz trasę
        trasa = Trasa.objects.create(
            nazwa='AJAX Test Route',
            opis='Route for testing AJAX point addition',
            uzytkownik=self.user,
            obraz_tla=self.obraz_tla
        )
        
        # Wysłanie żądania AJAX dodania punktu
        response = self.client.post(
            reverse('add_point_click', args=[trasa.id]),
            {'x': 150, 'y': 250},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Sprawdzenie odpowiedzi
        self.assertEqual(response.status_code, 200)
        self.assertTrue('success' in response.json())
        self.assertTrue(response.json()['success'])
        
        # Sprawdzenie czy punkt został dodany do bazy
        self.assertTrue(
            PunktTrasy.objects.filter(
                trasa=trasa,
                x=150,
                y=250
            ).exists()
        )