from django.urls import path
from . import views
app_name = "sector_analysis"

urlpatterns = [
    path("",views.index,name="index"),
    path("portfolio",views.portfolio,name="portfolio"),
    path("charts",views.charts,name="charts"),
]