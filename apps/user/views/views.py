from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from apps.user import models, send_email

def validate_password(password, confirm_password):
    """Validações se as senhas passadas estão de acordo com as condições 
    do sistema.

    Args:
        password (str): nova senha do usuário.
        confirm_password (str): senha de confirmação.
    
    Returns:
        dict: Dicionário contendo a mensagem e o no nome do error.
    """
    errors = {}
    password = password.replace(" ", "")
    confirm_password = confirm_password.replace(" ", "")

    if password == "" or confirm_password == "":
        errors['senha_vazia'] = "Por favor, preencha todos os campos."
    elif password != confirm_password:
        errors['senha_diferentes'] = "As senhas são diferentes"
    elif password.isdigit() or password.isalpha():
        errors['senha_numerica'] = "Sua senha deve conter números e letras"
    elif len(password) < 6:
        errors['senha_pequena'] = "Sua senha deve conter mais de seis caracteres"
    
    return errors


def sair(request):
    """Desautentica usuário do sistema."""
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
                    url = send_email.url_for_forgot_my_password(hash, usuario.id)
                    usuario.hash_confirm_senha = hash
                    usuario.save()

                    send_email.send_mail_for_user_forgot_my_password(usuario.nome, auth_user.email, url)

                    msg = {
                        'title': 'Aviso',
                        'msg': 'Um email foi enviado para este endereço contendo um link para alterar sua senha.'
                    }
                    return render(request, 'user/notification.html', { 'msg': msg })
                else:
                    errors['forgotpassword_error'] = 'User not found'
                    errors['forgotpasword_error_email'] = request.POST['email_forgot_password']
                
            except (User.DoesNotExist, models.Usuario.DoesNotExist):
                errors['forgotpassword_error'] = 'User not found'
                errors['forgotpasword_error_email'] = request.POST['email_forgot_password']
            
            errors['forgotpassword'] = True
        
        return render(request, 'user/login.html', { 'errors': errors })

    elif request.method == 'GET':
        return render(request, 'user/login.html')


def painel(request):
    if request.user.is_authenticated:
        try:
            usuario = models.Usuario.objects.get(user=request.user.id)

            return render(request, "user/painel.html", { 'usuario': usuario })
        except models.Usuario.DoesNotExist:
            return redirect('user_login')
    else:
        return redirect('user_login')


def change_password(request):    
    if request.user.is_authenticated:
        if request.method == 'POST':                                
            errors = validate_password(request.POST['senha'],
                                       request.POST['repeat_password'])
            if not check_password(request.POST['oldsenha'], request.user.password):
                errors['senha_incorreta'] = "Senha incorreta"
                    
            if errors == {}:
                # update_session_auth_hash() reloga o usuário pois o set_password()
                # desloga o usuário do sistema.
                request.user.set_password(request.POST['senha'])
                request.user.save()
                update_session_auth_hash(request, request.user)
                request.session.set_expiry(3600) 
                return render(request, 'user/changepassword.html', {'errors': {'concluido': "Senha alterada com sucesso"}, 'confirm': True, 'authenticated': True})
            else:
                return render(request, 'user/changepassword.html', {'errors': errors, 'confirm': False, 'authenticated': True})
        else:
            return render(request, 'user/changepassword.html', {'confirm': False, 'authenticated': True})
    
    elif 'id_usuario' in request.session.keys():
        if request.method == 'POST':
            usuario = User.objects.get(pk=request.session['id_usuario'])
            errors  = validate_password(request.POST['senha'],
                                        request.POST['repeat_password'])
            if errors == {}:
                usuario.set_password(request.POST['senha'])
                usuario.save()                
                del request.session['id_usuario']                
                msg = {
                    'msg': 'Senha alterada com sucesso.',
                    'title': 'Parabéns'
                }
                
                return render(request, 'user/notification.html', {'msg': msg, 'confirm': True})
            else:
                return render(request, 'user/changepassword.html', {'errors': errors, 'confirm': False})
        else:
            return render(request, 'user/changepassword.html', {'confirm': False})
    
    else:
        return redirect('user_login')


def authenticate_change_password(request, hash, id):     
    msg = {
        'msg': 'Url inválida.', 
        'title': 'Error'
    }

    try:
        usuario = models.Usuario.objects.get(pk=id)
        
        if usuario.hash_confirm_senha != "" and usuario.hash_confirm_senha == hash:
            usuario.hash_confirm_senha = ""
            usuario.save()
            request.session['id_usuario'] = usuario.user.id
            request.session.set_expiry(240)
            return redirect('user_change_password', permanent=True)
    except:
        pass

    return render(request, 'user/notification.html', { 'msg': msg })
