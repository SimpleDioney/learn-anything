from django.contrib import admin
from django.urls import path
from learn import views

urlpatterns = [
    path('', views.home, name='home'),
    path('ask/', views.ask_question, name='ask_question'),
    path('questions/', views.get_questions, name='get_questions'),
    path('questions/category/<int:category_id>/', views.get_questions_by_category, name='get_questions_by_category'),
    path('search/', views.search_questions, name='search_questions'),
]
