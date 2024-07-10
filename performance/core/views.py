from django.http import HttpResponse
from django.shortcuts import render

def analytics(request):
    return render(request, 'core/analytics.html')

def bills(request):
    return render(request, 'core/bills.html')

def clients(request):
    return render(request, 'core/clients.html')

def dashboard(request):
    return render(request, 'core/dashboard.html')

def products(request):
    return render(request, 'core/products.html')

def reports(request):
    return render(request, 'core/reports.html')

def settings(request):
    return render(request, 'core/settings.html')
