from django.urls import path, include
from apps.manager import views

urlpatterns = [
    path('admin_area/', views.admin_area, name = 'admin_area' ),
    path('information/<int:id>', views.information, name='admin_information'),

]