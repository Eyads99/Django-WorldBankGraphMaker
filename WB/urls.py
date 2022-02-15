from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'WB'

# /WB/
urlpatterns = [
    # /WB/+url path , view to use, name
    path(r"", views.index, name='index'),
    path(r"index1", views.index1, name='index1'),
    path(r"getname", views.get_name, name='name'),
    path(r"graph", views.graph, name='graph'),
    path(r'download_CSV', views.download_CSV, name="download_CSV"),
]
