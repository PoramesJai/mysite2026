from django.http import HttpResponse, JsonResponse, FileResponse
from django.shortcuts import render, redirect
from django.conf import settings

def home(request):
    return redirect('/chopee/')

def info(request):
    data = {}
    print('request.META')
    for k,v in request.META.items():
        data[str(k)] = str(v)
        print(k,'=', v)
    return JsonResponse(data)

def shopping(request):
    return render(request, 'shopping.html')

def lucksoot_pdf(request):
    file_path = settings.BASE_DIR / 'lucksoot.pdf'
    return FileResponse(
        open(file_path, 'rb'), 
        content_type='application/pdf', 
        filename='lucksoot.pdf')