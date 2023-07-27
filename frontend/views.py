from django.shortcuts import render, redirect
from .models import Profile

def catalog(request, id=None):
    if id:
        request.session['id_cat'] = id
    else:
        request.session['id_cat'] = None
    return render(request, 'frontend/catalog.html')

def profile(request):
    if request.user.is_authenticated == True:
        Profile.objects.filter(user_id=request.user)
        return render(request, 'frontend/profile.html')
    else:
        return redirect('/catalog/')


def payment(request, id):
    if 'paymentType' in request.session:
        if request.session['paymentType'] == 'someone':
            return render(request, 'frontend/paymentsomeone.html')
        else:
            return render(request, 'frontend/payment.html')
    else:
        return redirect('/catalog/')