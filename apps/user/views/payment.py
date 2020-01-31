from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from apps.user import models
import requests
import xmltodict
import logging

logger = logging.getLogger('django')

def payment_is_available():
    # TODO: Desenvolver condição
    return True


def pagamento(request):
    if request.user.is_authenticated:
        try:
            usuario = models.Usuario.objects.get(user=request.user.id)
        except models.Usuario.DoesNotExist:
            return redirect('user_login')

        if request.method == 'POST':
            # Criar pagamento no banco
            pagamento = models.Pagamento.objects.create(usuario=usuario)
            pagamento.save()

            headers = {
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
            }

            # Preenchendo os dados da compra
            dados = {
                'email'           : settings.PAGSEGURO_EMAIL,
                'token'           : settings.PAGSEGURO_TOKEN,
                'currency'        : 'BRL',
                'reference'       : pagamento.id, 
                'senderName'      : usuario.nome,   
                'senderEmail'     : usuario.user.email,
                'itemId1'         : usuario.tipo_inscricao.id,
                'itemQuantity1'   : '1',
                'itemDescription1': "Inscrição no evento Genomics and Bioinfomatics - 20 years",
                'itemAmount1'     : usuario.tipo_inscricao.valor,
                'timeout'         : 25,
                'enableRecovery'  : False,
                'notificationURL' : "http://bioinfo.imd.ufrn.br/genobio20_userarea/user/pagamento/notification/",
            }            

            # Enviando requisição ao pagseguro            
            response = requests.post("https://ws.sandbox.pagseguro.uol.com.br/v2/checkout", data=dados, headers=headers)

            root = xmltodict.parse(response.text)

            if response.status_code == 200:
                data = {
                    'code': root['checkout']['code'],
                    'status_code': response.status_code,
                    'date': root['checkout']['date'],
                    'success': True
                }

                return render(request, 'user/pagamento.html', { 'transacao': data['code'] })            
            else:
                data = {
                    'status_code': response.status_code,
                    'message': root["errors"]["error"]["message"],
                    'success': False,
                }

                return render(request, 'user/pagamento.html', { 'error': data['message'] })

        elif request.method == 'GET':
            last_payment = models.Pagamento.objects.filter(usuario=usuario).last()

            # Casos em que o usuário já efetivou o pagamento
            # ou que estamos aguardando a finalização do mesmo.
            if last_payment is not None and last_payment.status is not None:                
                if last_payment.status in [3, 4]:
                    return render(request, 'user/pagamento.html', { 'can_pay': False,
                                                                    'msg': 'Pagamento confirmado',
                                                                    'alert_class': 'sucess' })
                elif last_payment.status in [1, 2, 5, 9]:
                    return render(request, 'user/pagamento.html', { 'can_pay': False,
                                                                    'msg': 'Inscrições Encerradas',
                                                                    'alert_class': 'warning' })
            # Caso em que o usuário pode realizar o pagamento
            else:
                if payment_is_available():
                    return render(request, 'user/pagamento.html', { 'can_pay': True,
                                                                    'subscription_value': usuario.tipo_inscricao.valor }) # TODO: Enviar o valor e alguma mensagem
                else:
                    return render(request, 'user/pagamento.html', { 'can_pay': False,
                                                                    'msg': 'Inscrições Encerradas',
                                                                    'alert_class': 'warning' })            
        
    else:
        return redirect('user_login')


@csrf_exempt
@require_http_methods(['POST'])
def notification(request):
    notification_code = request.POST.get('notificationCode', None)
    
    if notification_code :        
        response = requests.get(
            'https://ws.sandbox.pagseguro.uol.com.br/v3/transactions/notifications/{}'.format(notification_code),
            params = {
                'email': settings.PAGSEGURO_EMAIL,
                'token': settings.PAGSEGURO_TOKEN,
            }
        )   

        if response.status_code == 200:
            root = xmltodict.parse(response.text)
            status       = root['transaction']['status']
            code         = root['transaction']['code']
            reference    = root['transaction']['reference']
            payment_type = root['transaction']['paymentMethod']['type']
            payment_code = root['transaction']['paymentMethod']['code']
            
            try:
                pagamento = models.Pagamento.objects.get(pk=reference)
                pagamento.codigo_transacao = code
                pagamento.status = models.Situacao_de_pagamento.objects.get(pk=status)
                pagamento.save()

                # Envio de email de confirmação de pagamento 
                if pagamento.status.id == 3:                                                           
                    user_email = pagamento.usuario.user.email
                    user_name  = pagamento.usuario.nome
                    titulo     = "Genomics and Bioinfomatics - 20 years"                                                     
                    texto      = "Recebemos o seu pagamento para participação no evento Genomics and Bioinfomatics - 20 years"                    
                    send_email.send_mail_notification_for_user(user_email, user_name, texto, titulo)                                    
                    
                    return HttpResponse("OK")
            except Exception as ex:
                logger.error('\n\n({}) Error in notification(payment.py line 100):\n\tMsg: {}\n\trequest date: {}'.format(datetime.today(), ex, root))
        else:
            logger.error('\n\n({}) Error in notification(payment.py line 104):\n\tMsg: {}\n\trequest date: {}'.format(datetime.today(), "Não foi possível enviar requisição get para o pagseguro para receber o status de pagamento", root))                              

    return HttpResponse("ERROR")    
