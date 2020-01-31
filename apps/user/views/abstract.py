import json
from django.shortcuts import render
from apps.user.models import *

def abstract(request):
    return render(request, 'user/abstract.html')


def resumo(request):
    if request.user.is_authenticated:
        try:
            user_usuario = Usuario.objects.get(user=request.user)
            trabalho_resumo = Resumo.objects.get(usuario=user_usuario)
            trabalho_autores = Autores.objects.filter(resumo=trabalho_resumo)

            autores = {}
            for i in range(len(trabalho_autores)):
                autores[str(i)] = {"nome": trabalho_autores[i].nome,
                                   "email": trabalho_autores[i].email,
                                   "instituicao": trabalho_autores[i].instituicao.nome
                                   }  # Tranformando o query set em um dicionario

            res = {'titulo': trabalho_resumo.titulo,
                   'texto': trabalho_resumo.texto,
                   'palavras_chave': trabalho_resumo.palavras_chave,
                   'autores': autores
                   }

            #abstract = models.Resumo.objects.filter(usuario=usuario).last()
            aval = Avaliacoes.objects.filter(resumo=trabalho_resumo).last()
            tipo_aval = None
            if aval is not None:
                tipo_aval = aval.status.tipo

            return render(request, 'user/abstract.html', {'res': res, 'ja_enviado': True, 'tipo_aval' : tipo_aval})
    
        except Resumo.DoesNotExist:
            errors = {}
            if request.POST:
                res = {'titulo': request.POST['inputTitle'],
                       'texto': request.POST['inputText'],
                       'palavras_chave': request.POST['inputKeywords'],
                       'autores': json.loads(request.POST['autores']),
                       }

                reg_bool = True
                if res['titulo'].replace(" ", "") == "":
                    errors['titulo_nao_encontrado'] = "Please inform the title of the abstract"
                    reg_bool = False
                if res['texto'].replace(" ", "") == "":
                    errors['texto_invalido'] = "Please fill in the abstract."
                    reg_bool = False
                if res['palavras_chave'].replace(" ", "") == "":
                    errors['palavras_chave_vazia'] = "Please enter the keywords of your abstract."
                    reg_bool = False
                elif len(list(filter(None, res['palavras_chave'].split(",")))) <3 and len(list(filter(None, res['palavras_chave'].split(";")))) <3 :
                    errors['palavras_chave_vazia'] = "Minimum of three words"
                    reg_bool = False
                if res['autores'] == {}:
                    errors['autores_vazio'] = " Please add the author(s)."
                    reg_bool = False
                for i in res['autores'].keys():
                    if res['autores'][i]['instituicao'].replace(" ", "") == "":
                        print(i)
                        errors['inst_vazia'] = " Add institution(s) to the author(s)."
                        reg_bool = False
                if reg_bool == True:
                    user_usuario = Usuario.objects.get(user=request.user)
                    novo_res = Resumo.objects.create(titulo=res['titulo'],
                                                     texto=res['texto'],
                                                     palavras_chave=res['palavras_chave'],
                                                     usuario=user_usuario)
                    novo_res.save()
                    for i in res['autores'].keys():
                        nova_int = Instituicao.objects.create(nome=res['autores'][i]['instituicao'],
                                                              resumo=Resumo.objects.get(id=novo_res.id),
                                                              ordem=int(i))
                        nova_int.save()

                        novo_aut = Autores.objects.create(nome=res['autores'][i]['nome'],
                                                          email=res['autores'][i]['email'],
                                                          ordem=int(i),
                                                          instituicao=Instituicao.objects.get(id=nova_int.id),
                                                          resumo=Resumo.objects.get(id=novo_res.id))
                        novo_aut.save()

                    nova_aval = Avaliacoes.objects.create(status=Status_avaliacoes.objects.get(id=1),
                                                          observacao=None,
                                                          resumo=Resumo.objects.get(id=novo_res.id))

                    return render(request, 'user/abstract.html', {'res': res, 'ja_enviado': True})
                else:
                    return render(request, 'user/abstract.html', {'errors': errors, 'res': res})

            return render(request, 'user/abstract.html')
    else:
        return redirect('url_user_login')
