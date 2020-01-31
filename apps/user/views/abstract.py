from django.shortcuts import render

def abstract(request):
    return render(request, 'user/abstract.html')