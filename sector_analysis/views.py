from django.shortcuts import render

from django.http import HttpResponse
import json
sectors = ["FMCG", "IT", "BANKING"]
dict={}
dict["FMCG"] = ["BRITANNIA","ITC","HINDUNILVR","MARICO"]


# Create your views here.
def index(request):
    return render(request,"sector_analysis/index.html",
    {"sectors": sectors,
    "dict":json.dumps(dict)}
    )