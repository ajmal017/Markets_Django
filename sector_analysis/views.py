from django.shortcuts import render

from django.http import HttpResponse

sectors = ["FMCG", "IT", "BANKING"]
# Create your views here.
def index(request):
    return render(request,"sector_analysis/index.html",
    {"sectors": sectors}
    )