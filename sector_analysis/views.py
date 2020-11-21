from django.shortcuts import render
from django.http import HttpResponse
import json
import pandas as pd
from bokeh.plotting import figure, output_file, show 
from bokeh.embed import components
from sector_analysis.models import Holdings

mdf_15m = pd.read_csv(r'C:\Users\prave\Documents\GitHub\Market-Analysis\mdf_15m.csv')
mdf_15m = pd.read_csv(r'C:\Users\prave\Documents\GitHub\Market-Analysis\mdf_15m.csv')
mdf_15m = pd.read_csv(r'C:\Users\prave\Documents\GitHub\Market-Analysis\mdf_15m.csv')

sector_img_path = '\\sector_analysis\\static\\sector_analysis\\images'
def get_sectors_list(sector_img_path):
	import os
	s = os.getcwd()+sector_img_path
	sectors = [x[0] for x in os.walk(s)][1:]
	sectors = [x.split(s+'\\')[1] for x in sectors]
	return sectors
sectors = get_sectors_list(sector_img_path)
import os
from django.templatetags.static import static
s = os.getcwd()+sector_img_path+'\\'
dict = {}
sectors_filenames = [x[0] for x in os.walk(s)][1:]
sectors = [x.split(s)[1] for x in sectors_filenames]

for text in sectors_filenames:
    sector = text.split(s)[1]
    companies = os.listdir(text)
    companies = [x.split('.png')[0] for x in companies]
    dict[sector] = companies

def index(request):
    if request.method=="POST":
        tikr = request.POST['tkr']
        buy = float(request.POST['B'])
        qty = int(request.POST['Q'])
        sl = float(request.POST['SL'])
        target = float(request.POST['T'])
        Holdings.objects.create(
            tikr = tikr,
            buy = buy,
            qty = qty,
            sl = sl,
            t=target
        )
        return HttpResponse(str(tikr)+"|"+str(buy)+"|"+str(qty)+"|"+str(sl)+"|"+str(target))

    return render(request,"sector_analysis/index.html",
    {"sectors": sectors,
    "dict":json.dumps(dict) ,
    "img_path":sectors,
    }
    )


