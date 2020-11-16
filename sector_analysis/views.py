from django.shortcuts import render

from django.http import HttpResponse
import json
sector_img_path = '\\sector_analysis\\static\\sector_analysis\\images'
def get_sectors_list(sector_img_path):
	import os
	s = os.getcwd()+sector_img_path
	sectors = [x[0] for x in os.walk(s)][1:]
	sectors = [x.split(s+'\\')[1] for x in sectors]
	return sectors
sectors = get_sectors_list(sector_img_path)
# sectors = ["FMCG", "IT", "BANKING"]
# dict={}
# dict["FMCG"] = ["BRITANNIA","ITC","HINDUNILVR","MARICO"]
import os
from django.templatetags.static import static


import os
s = os.getcwd()+sector_img_path+'\\'
dict = {}
sectors_filenames = [x[0] for x in os.walk(s)][1:]
sectors = [x.split(s)[1] for x in sectors_filenames]

for text in sectors_filenames:
    sector = text.split(s)[1]
    companies = os.listdir(text)
    companies = [x.split('.png')[0] for x in companies]
    dict[sector] = companies

# import settings
# url = settings.STATIC_URL   
# from os import listdir
from os.path import isfile, join
# fldrs = [static(f) for f in listdir(url) if isfile(join(mypath, f))]
# url = isfile(''.join(url))
# Create your views here.

def index(request):
    return render(request,"sector_analysis/index.html",
    {"sectors": sectors,
    "dict":json.dumps(dict),
    "img_path":sectors
    }
    )


