from django.urls import path
from . import views

app_name = "sector_analysis"

urlpatterns = [
    path("",views.index,name="index"),
    path("portfolio",views.portfolio,name="portfolio"),
    path("charts/", views.redirect_view,name="charts_ind"),
    path("charts/<str:tikr_>",views.charts,name="charts"), 
    path("completed",views.completed,name="completed"),
]