
from django.contrib import admin

from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("generate_plot/", views.generate_plot, name="generate_plot"),
]
