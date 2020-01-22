from django.shortcuts import render

def pagamento(request):
    return render(request, 'user/pagamento.html')