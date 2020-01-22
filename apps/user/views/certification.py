from django.shortcuts import render

def certificate(request):
    return render(request, 'user/certification.html')