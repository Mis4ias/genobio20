from django.shortcuts import render

def login_and_forgot_password(request):
    return render(request, 'user/login.html')
