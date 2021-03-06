from django.urls import path, include
from apps.user.views import views, registration, payment, certification, abstract

urlpatterns = [
    path('login/', views.login_and_forgot_password, name="user_login"),
    path('sair/', views.sair, name="user_sair"),
    path('painel/', views.painel, name = "user_painel"),
    path('pagamento/', payment.pagamento, name = "user_pagamento"),
    path('abstract/', abstract.resumo, name="user_resumo"),
    path('pagamento/notification/', payment.notification),
    path('certificado/', certification.certificate, name = "user_certificado"),
    path('changepassword/', views.change_password, name = "user_change_password"),
    path('changepassword/authenticate/<slug:hash>/<int:id>/', views.authenticate_change_password),
    path('registration/', registration.register, name="user_registration_register"),
    path('registration/confirm/<slug:hash>/<int:id>/', registration.confirm ),
    path('registration/select/cities/', registration.select_cities, name="user_select_cities")
]
