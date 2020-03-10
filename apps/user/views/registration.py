from django.shortcuts import render, HttpResponse
from django.contrib.auth.models import User
from apps.user import models, send_email
from apps.manager.views import registration_is_available
from datetime import datetime
import re, json, logging

logger = logging.getLogger('django')

def select_cities(request):
    """Web service que seleciona no banco as cidades pertencentes ao estado informado.

    Returns:
        JSON: Um lista de objetos JSON cotendo o id e o nome das cidades pertencentes ao estado 
        informado. Ex:
            0: {
                "id": 377,
                "Nome": "Natal"
            }, 
            ...
    """
    if request.method == "GET":
        try:        
            # Selecionando todas as cidades relacionandas ao id do estado
            list_cidades = models.Cidade.objects.filter(id_estado=request.GET['id_estado'])  
            
            # Tranformando o query set em um dicionario
            cidades = {}
            for i in range(len(list_cidades)):            
                cidades[str(i)] = {
                    "id"  : list_cidades[i].id,
                    "Nome": list_cidades[i].nome
                }  
            
            cidades_json = json.dumps(cidades)

            return HttpResponse(cidades_json)
        except models.Cidade.DoesNotExist:
            return HttpResponse()   


def exist_email(email):
    """Verifica se já existe algum usuario no banco de dados com o email informado.

    Args:
        email (str): Email do usuário que será verificado.
    
    Returns:
        bool: True caso exista algum usuário com este email e False caso contrário.
    """
    try:
        usuario_aux = User.objects.get(email=email)    
        return True
    except User.DoesNotExist:
        return False


def validate_user(request):
    """Valida todos os dados do usuário, verificando se existem
    campos vazios, no formato errado, inválidos e se já não
    existe outro usuário com o email informado.

    Args:
        request (dict): Dicionário contendo os dados da requisição.

    Returns:
        dict: Um dicionário no qual suas chaves são o nome do erro, e que contem as mensagens 
        dos erros encontrado nos dados do usuário.
        dict: Um dicionário contendo os dados do usuário validados e prontos para serem inseridos
        no banco.
    """
    errors = {}
    erro_comum = "Required field"
    filtro = re.compile('([0-9]+)')  # Criando filtro para validação de cep e telefone
    usuario = {
        'nome_usuario'    : request.POST['name'],
        'email'           : request.POST['email'],
        'celular'         : request.POST['telephone'],
        'senha'           : request.POST['password'],
        'repeat_password' : request.POST['confirm_password'],
        'curso_formacao'  : request.POST['training'],
        'instituicao'     : request.POST['organization'],
        'tipo_inscricao'  : request.POST['inscricao'],
        'titulacao'       : request.POST['titulacao'],
        #'area'            : request.POST['area'],
        'cep'             : request.POST['zipcode'],
        'country'         : request.POST['country'],
        'estado'          : request.POST.get('state', None), 
        'cidade'          : request.POST.get('city', None),  
        'endereco'        : request.POST['adress']
    }    
    
    # validaçoes de email
    if exist_email(usuario['email']):
        errors['erro_email_existente'] = "There is already a registered user with this email address"

    if usuario['email'].replace(" ", "") == "":
        errors['erro_email_vazio'] = erro_comum

    # Validações para senha
    if usuario['senha'].replace(" ", "") == "" and usuario['repeat_password'].replace(" ", "") == "":
        errors['senhas_vazias'] = erro_comum

    if usuario['senha'].replace(" ", "") != usuario['repeat_password'].replace(" ", ""):
        errors['senha_diferentes'] = "Passwords do not match"

    if usuario['senha'].replace(" ", "").isdigit():
        errors['senha_numerica'] = "Your password must contain letters and numbers"

    if usuario['senha'].replace(" ", "").isalpha():
        errors['senha_digitos'] = "Your password must contain letters and numbers"

    if len(usuario['senha'].replace(" ", "")) < 6:
        errors['senha_pequena'] = "Your password must contain more than 6 characters"

    # Validação para nome
    if usuario['nome_usuario'].replace(" ", "") == "":
        errors['erro_nome_vazio'] = erro_comum

    if len(usuario['nome_usuario'].replace(" ", "")) < 2:
        errors['nome_short'] = "Fill in this field with at least 2 characters"

    # Validação para titulacao
    try:
        usuario['titulacao'] = models.Titulacao.objects.get(pk=int(usuario['titulacao']))
    except Exception:
        errors['titulo_nao_escolhido'] = "Please select a title"

    # Validaçao para tipo_inscricao
    try:
        usuario['tipo_inscricao'] = models.Tipo_Inscricao.objects.get(pk=int(usuario['tipo_inscricao']))
    except Exception:
        errors['tipo_inscricao_nao_escolhido'] = "Please select a subscription type"

    # Validaçao para area
    #try:
    #    usuario['area'] = models.Area.objects.get(pk=int(usuario['area']))
    #except Exception:
    #    errors['area_nao_escolhida'] = "Please select a area"

    # Validações de endereço
    if usuario['cep'].replace(" ", "") == "":
        errors['cep_empty'] = erro_comum

    if usuario['endereco'].replace(" ", "") == "": 
        errors['endereco_empty'] = erro_comum

    try:
        usuario['country'] = models.Pais.objects.get(pk=int(usuario['country']))
        
        # Validações para pessoas do Brasil
        if usuario['country'].id == 30:
            if len("".join(filtro.findall(usuario['cep']))) != 8:
                errors['cep_invalido'] = "Invalid zip code format"
            
            try:
                usuario['estado'] = models.Estado.objects.get(id=int(usuario['estado']))
            except Exception:
                errors['estado_nao_escolhido'] = "Please select the state"
            
            try:
                usuario['cidade'] = models.Cidade.objects.get(id=int(usuario['cidade']))
            except Exception:
                errors['cidade_nao_escolhido'] = "Please select the city"
            
            if usuario['celular'].replace(" ", "") == "":
                errors['celular_empty'] = erro_comum

            if len("".join(filtro.findall(usuario['celular']))) < 8:
                errors['celular_invalido'] = "Invalid phone format"            
    except Exception:
        errors['country_nao_escolhido'] = "Please select the country"
        usuario['country'] = "nada"

    return errors, usuario


def register(request):

    if(not registration_is_available()):
        return render(request, 'user/registration.html', {'registration_available': False})

    """Salva no banco o cliente passado na requisição"""
    dados = {
        'estados': models.Estado.objects.all(),
        'paises': models.Pais.objects.all(),
        'tipo_inscricoes' : models.Tipo_Inscricao.objects.all(),
        'titulos': models.Titulacao.objects.all(),
        #'areas': models.Area.objects.all()
    }

    if request.method == "POST":    
        errors, usuario = validate_user(request)        

        if errors == {}:
            """
            Note que o username e o email do new_auth_user são o email
            do usuário, pois são dados que devem ser únicos pois servem 
            para identificar o usuário no banco. E o único dado do usuário 
            que é único é seu email, visto que, não temos cpf ou RG do usuário
            por exemplo.
            """
            try:
                new_auth_user = User.objects.create_user(username = usuario['email'],
                                                         email     = usuario['email'],
                                                         password  = usuario['senha'],
                                                         is_active = False)
                new_auth_user.save()
            except Exception as ex:
                logger.error('\n\n({}) Error in create auth_user(registration.py line 196):\n\tMsg: {}\n\t'.format(datetime.today(), ex))                              
                return render(request, 'user/notification.html', { 'msg': {
                    'title': 'Desculpe',
                    'msg' : 'Não foi possível realizar o cadastro. Por favor entre em contato conosco.'
                }})

            try:                 
                novo_usuario = models.Usuario.objects.create(user          = new_auth_user,
                                                            nome           = usuario['nome_usuario'],
                                                            curso_formacao = usuario['curso_formacao'],
                                                            instituicao    = usuario['instituicao'],
                                                            titulacao      = usuario['titulacao'],
                                                            #area           = usuario['area'],
                                                            tipo_inscricao = usuario['tipo_inscricao'],
                                                            celular        = usuario['celular'],                                                                                                                                                                                    
                                                            estado         = usuario['estado'],
                                                            cidade         = usuario['cidade'], 
                                                            pais           = usuario['country'],
                                                            cep            = usuario['cep'],
                                                            endereco       = usuario['endereco'])                
                novo_usuario.save()
            except Exception as ex:                
                new_auth_user.delete()
                logger.error('\n\n({}) Error in create user(registration.py line 209):\n\tMsg: {}\n\t'.format(datetime.today(), ex))
                return render(request, 'user/notification.html', { 'msg': {
                    'title': 'Desculpe',
                    'msg' : 'Não foi possível realizar o cadastro. Por favor entre em contato conosco.'
                }})
                                                    
            # Gerando codigo para autenticar posteriormente o usuario e enviando email para o mesmo
            hash = novo_usuario.hash()                    
            url  = send_email.url_for_confirm_mail(hash, novo_usuario.id)  

            novo_usuario.hash_confirm_register = hash  
            novo_usuario.save()

            send_email.send_mail_for_user_confirm_mail(novo_usuario.nome, 
                                                       new_auth_user.email,
                                                       url)              
            return render(request, 'user/notification.html', { 'msg': {
                'title': 'Por favor verifique seu email para confirmar o cadastro.'
            }})                                              
        else:
            return render(request, 'user/registration.html', { 'dados': dados, 'errors': errors, 'usuario': usuario })    
    elif request.method == "GET":
        return render(request, 'user/registration.html', { 'dados': dados })


def confirm(request, hash, id):
    """Web service para confirmar a inscrição do usuario.
    
    Args:
        request (dict): Contem as informações da requisição.
        hash (str): 
            Código gerado no momento da inscrição e passado
            no link que foi enviado para o email do usuário, e inserido 
            no banco de dados para no momento de confirmar a inscrição, 
            comparar o hash do banco e o hash passado para verificar se 
            é este usuário que fez a inscrição.
        id (int): Identificador do usuário que realizou a inscrição.
    """
    msg = {}
    confirm = False
    
    try:
        # Procurando usuário no banco de dados
        usuario = models.Usuario.objects.get(pk=int(id))

        if usuario:
            # Verificando se esse usuário já não está ativo
            if usuario.user.is_active and usuario.hash_confirm_register == "":
                msg = {
                    'msg'  : 'O cadastro deste usuário já foi confirmado.', 
                    'title': 'Confirmação de Inscrição'
                }
            elif usuario.hash_confirm_register == hash:
                usuario.user.is_active = True
                usuario.hash_confirm_register = ""
                usuario.user.save()
                usuario.save()

                msg = {
                    'msg'  : 'Cadastro confirmado com sucesso',
                    'title': 'Confirmação'
                }
                confirm = True           
            else:
                msg = {
                    'msg'  : 'Url inválida, por favor se dirija a página de inscrição',
                    'title': 'Error'
                }
                logger.info('\n\n({}) Method confirm(registration.py line 249):\n\tMsg: Possível falha na confirmação de inscrição.\n\tuser date: {}\n\thash: {}'.format(datetime.today(), usuario.nome, hash))                               
    except Exception:
        msg = {
            'msg'  : 'Url inválida, por favor se dirija a página de inscrição',
            'title': 'Error'
        }
        logger.info('\n\n({}) Method confirm(registration.py line 265):\n\tMsg: Falha na confirmação de inscrição.\n\tuser date: {}'.format(datetime.today(), {'id': id, 'hash': hash}))

    return render(request, 'user/notification.html', { 'msg': msg, 'confirm': confirm })
