from django.shortcuts import render, HttpResponse
from apps.user import models
import re, json

def select_cities(request):
    if request.GET:
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

            # Convertendo dicionario para json
            cidades_json = json.dumps(cidades)

            return HttpResponse(cidades_json)
        except models.Cidade.DoesNotExist:
            return HttpResponse()   


def register(request):
    dados = {
        'estados': models.Estado.objects.all(),
        'paises': models.Pais.objects.all(),
        'tipo_inscricoes' : models.Tipo_Inscricao.objects.all(),
        'titulos': models.Titulacao.objects.all(),
        'areas': models.Area.objects.all()
    }

    return render(request, 'user/registration.html', { 'dados': dados })
    