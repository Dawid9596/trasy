from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import ObrazTla, Trasa, PunktTrasy

class ModelTests(TestCase):
    """
    Testy sprawdzające poprawność działania modeli danych
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
    
    def test_obraz_tla_creation(self):
        """Test tworzenia instancji modelu ObrazTla"""
        self.assertEqual(self.obraz_tla.nazwa, 'Test Background')
        self.assertEqual(self.obraz_tla.szerokosc, 800)
        self.assertEqual(self.obraz_tla.wysokosc, 600)
        self.assertIsNotNone(self.obraz_tla.data_dodania)
    
    def test_trasa_creation(self):
        """Test tworzenia instancji modelu Trasa"""
        self.assertEqual(self.trasa.nazwa, 'Test Route')
        self.assertEqual(self.trasa.uzytkownik, self.user)
        self.assertEqual(self.trasa.obraz_tla, self.obraz_tla)
        self.assertIsNotNone(self.trasa.data_utworzenia)
        self.assertIsNotNone(self.trasa.data_modyfikacji)
    
    def test_punkt_trasy_creation(self):
        """Test tworzenia instancji modelu PunktTrasy"""
        self.assertEqual(self.punkt1.trasa, self.trasa)
        self.assertEqual(self.punkt1.x, 100)
        self.assertEqual(self.punkt1.y, 100)
        self.assertEqual(self.punkt1.kolejnosc, 1)
    
    def test_trasa_punkty_relation(self):
        """Test relacji między Trasą a PunktTrasy"""
        punkty = self.trasa.punkty.all().order_by('kolejnosc')
        self.assertEqual(punkty.count(), 2)
        self.assertEqual(punkty[0], self.punkt1)
        self.assertEqual(punkty[1], self.punkt2)
    
    def test_user_trasy_relation(self):
        """Test relacji między User a Trasa"""
        trasy = self.user.trasy.all()
        self.assertEqual(trasy.count(), 1)
        self.assertEqual(trasy[0], self.trasa)
    
    def test_obraz_tla_trasy_relation(self):
        """Test relacji między ObrazTla a Trasa"""
        trasy = self.obraz_tla.trasy.all()
        self.assertEqual(trasy.count(), 1)
        self.assertEqual(trasy[0], self.trasa)


class AuthViewsTests(TestCase):
    """
    Testy sprawdzające system uwierzytelniania i autoryzacji
    """
    
    def setUp(self):
        # Tworzenie użytkownika testowego
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123',
            email='test@example.com'
        )
    
    def test_login_page(self):
        """Test dostępu do strony logowania"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trasy_app/login.html')
    
    def test_register_page(self):
        """Test dostępu do strony rejestracji"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trasy_app/register.html')
    
    def test_login_success(self):
        """Test poprawnego logowania"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpassword123'
        })
        self.assertRedirects(response, reverse('home'))
    
    def test_login_failure(self):
        """Test niepoprawnego logowania"""
        # breakpoint()
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Zostajemy na stronie logowania
    
    def test_logout(self):
        """Test wylogowania"""
        # Najpierw logujemy użytkownika
        self.client.login(username='testuser', password='testpassword123')
        # Teraz wylogowujemy
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trasy_app/logout.html')
    
    def test_protected_page_access(self):
        """Test dostępu do chronionej strony bez logowania"""
        response = self.client.get(reverse('tlo_list'))
        # Powinno przekierować do strony logowania
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('tlo_list'))
    
    def test_protected_page_access_with_login(self):
        """Test dostępu do chronionej strony po zalogowaniu"""
        # Logujemy użytkownika
        self.client.login(username='testuser', password='testpassword123')
        # Próba dostępu do chronionej strony
        response = self.client.get(reverse('tlo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trasy_app/tlo_list.html')
    
    def test_registration(self):
        """Test rejestracji nowego użytkownika"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complex_password123',
            'password2': 'complex_password123'
        })
        self.assertRedirects(response, reverse('login'))
        
        # Sprawdzenie czy użytkownik został utworzony
        self.assertTrue(User.objects.filter(username='newuser').exists())


class RouteManagementTests(TestCase):
    """
    Testy sprawdzające zarządzanie trasami i punktami
    """
    
    def setUp(self):
        # Tworzenie użytkownika testowego
        self.user = User.objects.create_user(
            username='routeuser',
            password='routepassword123',
            email='route@example.com'
        )
        
        # Utworzenie drugiego użytkownika (do testów autoryzacji)
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='otherpassword123',
            email='other@example.com'
        )
        
        # Tworzenie testowego obrazu tła
        self.obraz_tla = ObrazTla.objects.create(
            nazwa='Route Test Background',
            opis='Test background for routes',
            szerokosc=800,
            wysokosc=600,
            obraz=SimpleUploadedFile(
                "route_background.jpg",
                b"file_content",
                content_type="image/jpeg"
            )
        )
        
        # Tworzenie testowej trasy
        self.trasa = Trasa.objects.create(
            nazwa='Management Test Route',
            opis='Test route for management',
            uzytkownik=self.user,
            obraz_tla=self.obraz_tla
        )
        
        # Dodawanie punktów do trasy
        self.punkt = PunktTrasy.objects.create(
            trasa=self.trasa,
            x=150,
            y=150,
            kolejnosc=1
        )
        
        # Logowanie użytkownika
        self.client.login(username='routeuser', password='routepassword123')
    
    def test_user_trasy_list(self):
        """Test wyświetlania listy tras użytkownika"""
        response = self.client.get(reverse('user_trasy'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trasy_app/user_trasy.html')
        self.assertContains(response, 'Management Test Route')
    
    def test_create_trasa(self):
        """Test tworzenia nowej trasy"""
        response = self.client.post(reverse('trasa_create', args=[self.obraz_tla.id]), {
            'nazwa': 'New Test Route',
            'opis': 'New test route description',
            'obraz_tla': self.obraz_tla.id
        })
        
        # Sprawdzenie przekierowania po utworzeniu
        self.assertEqual(response.status_code, 302)
        
        # Sprawdzenie czy trasa została utworzona
        new_trasa = Trasa.objects.filter(nazwa='New Test Route').first()
        self.assertIsNotNone(new_trasa)
        self.assertEqual(new_trasa.uzytkownik, self.user)
        self.assertEqual(new_trasa.obraz_tla, self.obraz_tla)
    
    def test_add_punkt_to_trasa(self):
        """Test dodawania punktu do trasy przez formularz"""
        response = self.client.post(reverse('trasa_edit', args=[self.trasa.id]), {
            'x': 300,
            'y': 300
        })
        
        # Sprawdzenie przekierowania po dodaniu punktu
        self.assertEqual(response.status_code, 302)
        
        # Sprawdzenie czy punkt został dodany
        punkt = PunktTrasy.objects.filter(trasa=self.trasa, x=300, y=300).first()
        self.assertIsNotNone(punkt)
        self.assertEqual(punkt.kolejnosc, 2)  # Powinien mieć kolejność 2 (bo już jest punkt z kolejnością 1)
    
    def test_add_punkt_click(self):
        """Test dodawania punktu przez kliknięcie (AJAX)"""
        response = self.client.post(
            reverse('add_point_click', args=[self.trasa.id]),
            {'x': 250, 'y': 250},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Sprawdzenie poprawności odpowiedzi JSON
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True, 'punkt_id': 2})
        
        # Sprawdzenie czy punkt został dodany
        punkt = PunktTrasy.objects.filter(trasa=self.trasa, x=250, y=250).first()
        self.assertIsNotNone(punkt)
    
    def test_delete_punkt(self):
        """Test usuwania punktu z trasy"""
        # Najpierw sprawdzamy ile jest punktów
        count_before = PunktTrasy.objects.filter(trasa=self.trasa).count()
        self.assertEqual(count_before, 1)
        
        # Usuwamy punkt
        response = self.client.get(reverse('punkt_delete', args=[self.punkt.id]))
        
        # Sprawdzenie przekierowania po usunięciu
        self.assertEqual(response.status_code, 302)
        
        # Sprawdzenie czy punkt został usunięty
        count_after = PunktTrasy.objects.filter(trasa=self.trasa).count()
        self.assertEqual(count_after, 0)
    
    def test_trasa_edit_unauthorized(self):
        """Test próby edycji trasy przez nieuprawnionego użytkownika"""
        # Logujemy się jako inny użytkownik
        self.client.logout()
        self.client.login(username='otheruser', password='otherpassword123')
        
        # Próba edycji trasy innego użytkownika
        response = self.client.get(reverse('trasa_edit', args=[self.trasa.id]))
        
        # Powinien zwrócić 404, ponieważ trasa jest filtrowana po zalogowanym użytkowniku
        self.assertEqual(response.status_code, 404)
    
    def test_punkt_delete_unauthorized(self):
        """Test próby usunięcia punktu przez nieuprawnionego użytkownika"""
        # Logujemy się jako inny użytkownik
        self.client.logout()
        self.client.login(username='otheruser', password='otherpassword123')
        
        # Próba usunięcia punktu z trasy innego użytkownika
        response = self.client.get(reverse('punkt_delete', args=[self.punkt.id]))
        
        # Powinien zwrócić 404
        self.assertEqual(response.status_code, 404)
        
        # Sprawdzenie czy punkt nadal istnieje
        self.assertTrue(PunktTrasy.objects.filter(id=self.punkt.id).exists())
