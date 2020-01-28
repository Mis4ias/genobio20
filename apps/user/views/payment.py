from django.shortcuts import render
from apps.user import models

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
            response = requests.post("https://ws.pagseguro.uol.com.br/v2/checkout", data=dados, headers=headers)

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
            pass
            
        return render(request, 'user/pagamento.html')
    else:
        return redirect('user_login')