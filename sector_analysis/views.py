from django.shortcuts import render
from django.http import HttpResponse
import json
import pandas as pd
from bokeh.plotting import figure, output_file, show 
from bokeh.embed import components
from sector_analysis.models import Holdings,ltp_tikrs
import time
mdf_15m = pd.read_csv(r'C:\Users\prave\Documents\GitHub\Market-Analysis\mdf_15m.csv')
mdf_15m = pd.read_csv(r'C:\Users\prave\Documents\GitHub\Market-Analysis\mdf_15m.csv')
mdf_15m = pd.read_csv(r'C:\Users\prave\Documents\GitHub\Market-Analysis\mdf_15m.csv')
import bs4,requests
def parsePrice(FB):
    url = requests.get('https://finance.yahoo.com/quote/' + FB + '?p=' + FB)
    soup = bs4.BeautifulSoup(url.text, features="html.parser")
    price = soup.find_all("div", {'class': 'My(6px) Pos(r) smartphone_Mt(6px)'})[0].find('span').text
    price = float(price.replace(',',''))
    return price
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

holdings = Holdings.objects.all()
def find_ltp_render(holdings):
    import yfinance as yf
    tikr_list =list(holdings.tikr.value_counts().index)
    dict={}
    ltp_tikrs_ = ltp_tikrs.objects.all()
    for key in tikr_list:
        try:
            obj = ltp_tikrs_.objects.get(tikr=key)
            dict[key] = obj.ltp
        except:
            print('yf render')
            obj = ltp_tikrs.objects.create(tikr=key)
            obj.ltp =round(yf.download(key+".NS",period="5d",interval="1d").dropna().tail(1)['Close'][0],2)
            dict[key]=obj.ltp     
            time.sleep(1)
    return dict

def find_ltp(holdings):
    import yfinance as yf
    tikr_list =list(holdings.tikr.value_counts().index)
    dict={}
    for key in tikr_list:
        try:
            obj = ltp_tikrs.objects.get(tikr=key)            
            print('yf')
            dict[key]=round(yf.download(key+".NS",period="5d",interval="1d").dropna().tail(1)['Close'][0],2)
            obj.ltp = dict[key]
            obj.save()
            time.sleep(1)
        except:
            obj = ltp_tikrs.objects.get(tikr=key) 
            print('parse')
            dict[key]=parsePrice(key+".NS")
            obj.ltp = dict[key]
            obj.save()
            time.sleep(1)
    return dict

def gen_pd_holding():
    holdings = pd.DataFrame(Holdings.objects.values()).reset_index()
    holdings['buy_value'] = holdings['buy']*holdings['qty']
    holdings['Risk'] = (holdings['sl']-holdings['buy'])*holdings['qty']
    holdings['R1'] = -(holdings['sl']-holdings['buy'])*holdings['qty']    
    holdings['R2'] = -2*(holdings['sl']-holdings['buy'])*holdings['qty']
    holdings['R3'] = -3*(holdings['sl']-holdings['buy'])*holdings['qty']

    holdings['Risk_p'] = (holdings['Risk']/holdings['qty'])+holdings['buy']    
    holdings['R1_p'] = (holdings['R1']/holdings['qty'])+holdings['buy']    
    holdings['R2_p'] = (holdings['R2']/holdings['qty'])+holdings['buy']    
    holdings['R3_p'] = (holdings['R3']/holdings['qty'])+holdings['buy']
    holdings['entry'] = [x.strftime("%d-%b-%Y (%H:%M)") for x in holdings['entrydate']]
    holdings['button_id'] = ["btn_" + str(x) for x in holdings['id']]
    return holdings

def charts(request):
    return HttpResponse("Live charts using Bokeh/Plotly")
from datetime import datetime
def get_live_time():
    from datetime import datetime
    now = datetime.now() # current date and time
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    return date_time

def get_or_create_ltp():
    from sector_analysis.models import Holdings,ltp_tikrs
    holdings = pd.DataFrame(Holdings.objects.values()).reset_index()
    tikr_list =list(holdings.tikr.value_counts().index)
    dict = {}
    for t in tikr_list:
        try:
            obj = ltp_tikrs.objects.get(tikr=t)
            print(t, "is available")
            dict[t] = obj.ltp
            pass
        except:
            print(t," not available")
            ltp_tikrs.objects.create(tikr=t)
            dict[t] = 0.0
    return dict

def portfolio(request):
    if request.method=="POST":
        if 'update_ltp' in request.POST:
            holdings = gen_pd_holding()
            dict = find_ltp(holdings)
            holdings['ltp'] = [dict[x] for x in holdings['tikr']]   
            holdings['pl'] = (holdings['ltp']-holdings['buy'])*holdings['qty']
            time_happen="Last updated on " + get_live_time()
            json_records = holdings.to_json(orient ='records')
            data = []
            data = json.loads(json_records)
            context = {'d': data,'time_happen':time_happen}

            return render(request,"sector_analysis/portfolio.html",
            context)
        else:
            time_happen= (list(request.POST.keys()))
            time_happen = [x for x in time_happen if 'btn' in x ][0]
            id_ = int(time_happen.replace('btn_',''))
            # t = "entry " + str(id_) + " deleted with tikr " + Holdings.objects.get(pk=id_).tikr
            Holdings.objects.get(pk=id_).delete()

            holdings = gen_pd_holding()
            dict = get_or_create_ltp()
            holdings['ltp'] = [dict[x] for x in holdings['tikr']]   
            holdings['pl'] = (holdings['ltp']-holdings['buy'])*holdings['qty']
           

            # time_happen = time_happen['btn' in time_happen]
            json_records = holdings.to_json(orient ='records')
            data = []
            data = json.loads(json_records)
            context = {'d': data,'time_happen':time_happen}

            return render(request,"sector_analysis/portfolio.html",
            context)

    # get_or_create_ltp()
    holdings = gen_pd_holding()
    dict = get_or_create_ltp()
    holdings['ltp'] = [dict[x] for x in holdings['tikr']]
    holdings['pl'] = (holdings['ltp']-holdings['buy'])*holdings['qty']
    json_records = holdings.to_json(orient ='records') 
    data = [] 
    data = json.loads(json_records) 
    time_happen = "Values from database"
    context = {'d': data,'time_happen':time_happen} 
    return render(request,"sector_analysis/portfolio.html",
    context)



    
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
            t=target,
            entrydate=datetime.now()    ,
        )
        return HttpResponse(str(tikr)+"|"+str(buy)+"|"+str(qty)+"|"+str(sl)+"|"+str(target))

    return render(request,"sector_analysis/index.html",
    {
    "sectors": sectors,
    "dict":json.dumps(dict) ,
    "img_path":sectors,
    }
    )

