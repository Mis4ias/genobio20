from django.shortcuts import render, redirect
from django.http import HttpResponse
from datetime import date
from apps.user import models, send_email
import requests
import csv

def registration_is_available():
    today = date.today()
    registration_limit_day = date(2020, 11, 11)

    if today <= registration_limit_day:
        return True
    return False

def get_payment(usuario):
    try:
        payment = models.Pagamento.objects.filter(usuario = usuario).last()
        if payment is not None and payment.status is not None:
            return payment
        else:
            return None
    except models.Pagamento.DoesNotExist:
        return None

def export_db_csv (request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="alldata.csv"'
    writer = csv.writer(response)
    
    columns = [ "name",                
                "tel",
                "email",
                "country",
                "state",
                "city",
                "zip",
                "address",
                #"profile",
                "academic_degree",
                "institution",
                #"position",
                #"company",
                "payment",
                "observation",
                "abstract" ]
       

    writer.writerow(columns) # Inserindo colunas na tabela

    for usuario in models.Usuario.objects.all():

        # Capturando a última inscrição
        #last_subscription = models.Inscricao.objects.filter(usuario = usuario).last()
        
        # Capturando a situação de pagamento
        payment = get_payment(usuario)
        
        try:
            abstract = models.Resumo.objects.get(usuario=usuario)            
        except models.Resumo.DoesNotExist:
            abstract = None
        # Capturando os cursos inscrito
        #subscription_courses = models.Inscricao_curso.objects.filter(inscricao = last_subscription)
        
        data_user = {
            "name"   : usuario.nome,
            "payment": payment.status.descricao if payment is not None else "",
            "observation": payment.observacao if payment is not None else "",        
            "tel"    : usuario.celular,
            "email"  : usuario.user.email,
            "country": usuario.pais.nome,
            "state"  : usuario.estado.sigla if usuario.estado is not None else "",
            "city"   : usuario.cidade.nome if usuario.cidade is not None else "",
            "zip"    : usuario.cep,
            "address": usuario.endereco,
            #"profile": usuario.perfil.nome,
            "academic_degree": usuario.titulacao.titulo,
            "course": usuario.curso_formacao ,
            "institution": usuario.instituicao if usuario.instituicao is not None else "",
            #"position": usuario.cargo if usuario.perfil.id == 2 else "",
            #"company": usuario.nome_empresa if usuario.perfil.id == 2 else "",         
            "abstract": abstract.titulo if abstract is not None else "",
        }
        #for course in courses:
        #    data_user[course.descricao[:-1]] = "" 

        #if payment is not None and payment.status.id in [3, 4 ,10, 11]:
        #    for subscription_course in subscription_courses:
        #        data_user[subscription_course.curso.descricao[:-1]] = 'Pago'

        writer.writerow([ data_user[column] for column in columns ])

    return response

def admin_area( request ):    
    if request.user.is_authenticated and request.user.is_staff :
        all_users = models.Usuario.objects.all()
        all_data_users = []
        all_data_courses = {}

        for user in all_users:
            

            data_user = {}
            data_user["id"] = user.id
            data_user["name"] = user.nome
            data_user["email"] = user.user.email
            try:
                payment = models.Pagamento.objects.filter(usuario = user.id).last()
            except models.Pagamento.DoesNotExist:
                payment = None
            
            if payment is not None and payment.status is not None:
                data_user["payment"] = payment.status.descricao
            else:
                data_user["payment"] = "-"
            #data_user["payment"] = payment.status.descricao if payment is not None else "-"            
            
            
            all_data_users.append( data_user )            

        return render(request, "manager/admin_area.html", { "users": all_data_users })
    else:
        return redirect('user_login')

def information(request, id):
    if request.user.is_authenticated and request.user.is_staff :
        try:
            usuario = models.Usuario.objects.get(pk=id)
            try:
                payment = models.Pagamento.objects.filter(usuario = usuario.id).last()
                
            except models.Pagamento.DoesNotExist:
                payment = None
            #print(payment)
            data_user = {
                "id"     : usuario.id,
                "name"   : usuario.nome,
                #"payment": payment.status.descricao if payment is not None else "-",
                "comment": payment.observacao if payment is not None else "-",
                #"observation": payment.observacao if payment is not None else "",        
                "tel"    : usuario.celular,
                "email"  : usuario.user.email,
                "country": usuario.pais.nome,
                "state"  : usuario.estado.nome,
                "city"   : usuario.cidade.nome,
                "zip"    : usuario.cep,
                "address": usuario.endereco,   
                "subscription_type" : usuario.tipo_inscricao.tipo,
                "institution": usuario.instituicao,                
            }
            try:
                data_user["payment"] = payment.status.descricao
            except:
                data_user["payment"] = "-"

            user_paid = False
            show_color = ''

            #payment.status nulo ou n
            try:
                if payment is not None and payment.status is not None:
                    if payment.status.id in [3, 4, 10, 11]:
                        show_color = 'success'
                        user_paid = True
                    elif payment.status.id == 1:
                        show_color = 'warning'
                        user_paid = True
            except:
                if payment is not None:
                    if payment.status.id in [3, 4, 10, 11]:
                        show_color = 'success'
                        user_paid = True
                    elif payment.status.id == 1:
                        show_color = 'warning'
                        user_paid = True
            
            

            return render(request, "manager/information.html", {"dados": data_user, 
                                                                "payment_status": models.Situacao_de_pagamento.objects.filter(pk__in=[3, 4, 10, 11]),
                                                                "show_color": show_color,
                                                                "user_paid": user_paid})
        except models.Usuario.DoesNotExist:
            msg = { 
                'msg': "User do not found.", 
                'title': "Error" 
            } 
            return render(request, 'user/notification.html', { 'msg': msg })
    else:
        return redirect('user_login')


def change_payment(request, id):
    if request.user.is_authenticated and request.user.is_staff:

        if request.method == 'POST':
            usuario = models.Usuario.objects.get(pk=id)
            payment = models.Pagamento.objects.filter(usuario=usuario.id).last()
            status = models.Situacao_de_pagamento.objects.get(pk=3)

            if payment is not None:
                payment.status = status        
            else:
                payment = models.Pagamento(usuario=usuario, status=status)
          
            payment.observacao = request.POST.get('observation', "")
            payment.save()

            return information(request, id)
            
            '''except models.Usuario.DoesNotExist:
                msg = { 
                    'msg': "User do not found.", 
                    'title': "Error" 
                } 
                return render(request, 'user/notification.html', { 'msg': msg })'''
        
    return redirect('user_login')
