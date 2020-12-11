from django.urls import path

from . import views

urlpatterns = [
    path('start', views.index, name='start'),
    path('', views.StatusView.as_view(), name='index'),
]