from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from apps.user import models, send_email

def sair( request ):
    logout(request)
    return redirect('user_login')


def login_and_forgot_password(request):
    if request.method == 'POST':        
        errors = {}
        # Parte de Login
        if 'signin' in request.POST and 'email' in request.POST and 'password' in request.POST:
            try:
                auth_user = User.objects.get(email = request.POST['email'])
                
                user = authenticate(username = request.POST['email'], 
                                    password = request.POST['password'])

                if user is not None:                    
                    login(request, user) # Efetuando login
                    
                    request.session.set_expiry(3600) # Definindo o tempo de 1h em que o usuário estará logado no sistema
                    
                    # Redirecionando o admin para admin_area e o usuario para user_area
                    if user.is_staff:
                        return redirect('admin_area') 
                    else:
                        return redirect('user_painel')
                
                # Caso em que o usuário ainda não confirmou sua inscrição
                elif not auth_user.is_active:
                    errors['login_error'] = "Inscrição não confirmada"                
                else:
                    errors['login_error'] = "Email ou senha incorreta"
                
                errors['email'] = request.POST['email']
            
            except User.DoesNotExist:
                errors['login_error'] = "Email ou senha incorreta"

        # Parte de esqueci minha senha 
        elif 'email_forgot_password' in request.POST and 'forgot_password' in request.POST:
            try:
                auth_user = User.objects.get(email=request.POST['email_forgot_password'])
                usuario   = models.Usuario.objects.get(user=auth_user)

                if auth_user is not None and usuario is not None:
                    hash = usuario.hash()
                    url = send_email.url_for_forgot_my_password( hash, usuario.id )
                    usuario.hash_confirm_senha = hash
                    usuario.save()

                    send_email.send_mail_for_user_forgot_my_password(usuario.nome, auth_user.email, url)

                    msg = {
                        'title': 'Aviso',
                        'msg': 'Um email foi enviado para este endereço contendo um link para alterar sua senha.'
                    }
                    return render(request, 'user/notification.html', { 'msg': msg })
                else:
                    errors['forgotpassword_error'] = 'Usuário não encontrado'
                    errors['forgotpasword_error_email'] = request.POST['email_forgot_password']
                
            except (User.DoesNotExist, models.Usuario.DoesNotExist):
                errors['forgotpassword_error'] = 'Usuário não encontrado'
                errors['forgotpasword_error_email'] = request.POST['email_forgot_password']
            
            errors['forgotpassword'] = True
        
        return render(request, 'user/login.html', { 'errors': errors })

    elif request.method == 'GET':
        return render(request, 'user/login.html')

