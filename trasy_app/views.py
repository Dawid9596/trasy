from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import ObrazTla, Trasa, PunktTrasy
from .forms import UserRegisterForm, TrasaForm, PunktTrasyForm

def home(request):
    return render(request, 'trasy_app/home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_staff = True # Potencjalnie niechciane
            user.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Konto utworzone dla {username}! Możesz się teraz zalogować.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'trasy_app/register.html', {'form': form})

@login_required
def tlo_list(request):
    tla = ObrazTla.objects.all()
    return render(request, 'trasy_app/tlo_list.html', {'tla': tla})

@login_required
def trasa_create(request, tlo_id):
    tlo = get_object_or_404(ObrazTla, id=tlo_id)
    
    if request.method == 'POST':
        form = TrasaForm(request.POST)
        if form.is_valid():
            trasa = form.save(commit=False)
            trasa.uzytkownik = request.user
            trasa.obraz_tla = tlo
            trasa.save()
            messages.success(request, f'Trasa "{trasa.nazwa}" została utworzona!')
            return redirect('trasa_edit', trasa_id=trasa.id)
    else:
        form = TrasaForm(initial={'obraz_tla': tlo})
    
    return render(request, 'trasy_app/trasa_create.html', {'form': form, 'tlo': tlo})

@login_required
def trasa_edit(request, trasa_id):
    trasa = get_object_or_404(Trasa, id=trasa_id, uzytkownik=request.user)
    punkty = trasa.punkty.all().order_by('kolejnosc')
    
    # Formularz do dodawania nowych punktów
    if request.method == 'POST':
        form = PunktTrasyForm(request.POST, trasa=trasa)
        if form.is_valid():
            form.save()
            # AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                punkty = trasa.punkty.all().order_by('kolejnosc')
                data = [{
                    'id': p.id,
                    'x': p.x,
                    'y': p.y,
                    'kolejnosc': p.kolejnosc
                } for p in punkty]
                return JsonResponse({'success': True, 'punkty': data})
            else:
                messages.success(request, 'Punkt został dodany do trasy!')
                return redirect('trasa_edit', trasa_id=trasa.id)
    else:
        form = PunktTrasyForm()
    
    context = {
        'trasa': trasa,
        'punkty': punkty,
        'form': form,
    }
    return render(request, 'trasy_app/trasa_edit.html', context)

@login_required
def punkt_delete(request, punkt_id):
    punkt = get_object_or_404(PunktTrasy, id=punkt_id, trasa__uzytkownik=request.user)
    trasa_id = punkt.trasa.id
    usunieta_kolejnosc = punkt.kolejnosc
    
    # Usuwamy punkt
    punkt.delete()
    
    # Aktualizujemy kolejność pozostałych punktów
    from django.db.models import F
    PunktTrasy.objects.filter(
        trasa_id=trasa_id,
        kolejnosc__gt=usunieta_kolejnosc
    ).update(kolejnosc=F('kolejnosc') - 1)
    
    # Obsługa zapytań AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        punkty = PunktTrasy.objects.filter(trasa_id=trasa_id).order_by('kolejnosc')
        data = [{
            'id': p.id, 
            'x': p.x, 
            'y': p.y, 
            'kolejnosc': p.kolejnosc
        } for p in punkty]
        return JsonResponse({'success': True, 'punkty': data})
    
    messages.success(request, 'Punkt został usunięty z trasy!')
    return redirect('trasa_edit', trasa_id=trasa_id)

@login_required
def user_trasy(request):
    trasy = Trasa.objects.filter(uzytkownik=request.user)
    return render(request, 'trasy_app/user_trasy.html', {'trasy': trasy})

@login_required
def add_point_click(request, trasa_id):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        trasa = get_object_or_404(Trasa, id=trasa_id, uzytkownik=request.user)
        x = request.POST.get('x')
        y = request.POST.get('y')
        
        # Znajdź kolejny numer kolejności
        ostatni_punkt = PunktTrasy.objects.filter(trasa=trasa).order_by('-kolejnosc').first()
        kolejnosc = 1 if not ostatni_punkt else ostatni_punkt.kolejnosc + 1
        
        punkt = PunktTrasy.objects.create(
            trasa=trasa,
            x=x,
            y=y,
            kolejnosc=kolejnosc
        )
        
        return JsonResponse({'success': True, 'punkt_id': punkt.id})
    
    return JsonResponse({'success': False}, status=400)

@login_required
def punkt_move(request, punkt_id, kierunek):
    """
    Zamienia kolejność punktu z sąsiednim (w górę lub w dół)
    """
    punkt = get_object_or_404(PunktTrasy, id=punkt_id, trasa__uzytkownik=request.user)
    trasa_id = punkt.trasa.id
    
    if kierunek == 'up' and punkt.kolejnosc > 1:
        # Zamień z poprzednim punktem
        punkt_poprzedni = get_object_or_404(PunktTrasy, trasa_id=trasa_id, kolejnosc=punkt.kolejnosc-1)
        punkt_poprzedni.kolejnosc += 1
        punkt.kolejnosc -= 1
        punkt_poprzedni.save()
        punkt.save()
    elif kierunek == 'down':
        # Zamień z następnym punktem
        try:
            punkt_nastepny = PunktTrasy.objects.get(trasa_id=trasa_id, kolejnosc=punkt.kolejnosc+1)
            punkt_nastepny.kolejnosc -= 1
            punkt.kolejnosc += 1
            punkt_nastepny.save()
            punkt.save()
        except PunktTrasy.DoesNotExist:
            pass
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        punkty = PunktTrasy.objects.filter(trasa_id=trasa_id).order_by('kolejnosc')
        data = [{
            'id': p.id, 
            'x': p.x, 
            'y': p.y, 
            'kolejnosc': p.kolejnosc
        } for p in punkty]
        return JsonResponse({'success': True, 'punkty': data})
    
    return redirect('trasa_edit', trasa_id=trasa_id)


@login_required
def get_punkty(request, trasa_id):
    """
    Zwraca wszystkie punkty dla konkretnej trasy w formacie JSON
    """
    trasa = get_object_or_404(Trasa, id=trasa_id, uzytkownik=request.user)
    punkty = trasa.punkty.all().order_by('kolejnosc')
    
    data = [{
        'id': p.id, 
        'x': p.x, 
        'y': p.y, 
        'kolejnosc': p.kolejnosc
    } for p in punkty]
    
    return JsonResponse({'success': True, 'punkty': data})