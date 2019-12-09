from django.urls import path, include
from apps.user.views import views, registration, payment

urlpatterns = [
    path('login/', views.login_and_forgot_password, name="user_login"),
    # path('sair/', views.sair, name = "user_sair"),
    # path('painel/', views.painel, name = "user_painel"),
    # path('pagamento/', payment.pagamento, name = "user_pagamento"),
    # path('pagamento/notification/', payment.notification),
    # path('certificado/', views.certificado, name = "user_certificado"),
    # path('changepassword/', views.change_password, name = "user_change_password"),
    # path('changepassword/authenticate/<slug:hash>/<int:id>/', views.change_password_authenticate),
    path('registration/', registration.register, name="user_registration_register"),
    # path('registration/confirm/<slug:hash>/<int:id>/', registration.confirm ),
    # path('registration/select/cities/', registration.select_cities_this_state, name="user_select_cities")
]