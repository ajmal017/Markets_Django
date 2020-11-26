from django.shortcuts import render
from django.http import HttpResponse
import json
import pandas as pd
from bokeh.plotting import figure, output_file, show 
from bokeh.embed import components
from sector_analysis.models import Holdings,ltp_tikrs
import time
from datetime import datetime
from django.shortcuts import render
from plotly.offline import plot
from plotly.graph_objs import Scatter
import plotly.express as px
import json

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
def get_sectors_list(sector_img_path):
	import os
	s = os.getcwd()+sector_img_path
	sectors = [x[0] for x in os.walk(s)][1:]
	sectors = [x.split(s+'\\')[1] for x in sectors]
	return sectors

def find_ltp(holdings):
    def get_ltp_dict(tikr_list):
        def get_gsheet():
            #        import json
            import gspread
            #        import pandas as pd
            from oauth2client.service_account import ServiceAccountCredentials
            scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_name(r'C:\Users\prave\Documents\GitHub\Market-Analysis\Money App-a10f1f368e5b.json', scope)
            # authorize the clientsheet 
            client = gspread.authorize(creds)
            # get the instance of the Spreadsheet
            sheet = client.open('Strategic Calls').worksheet('Sheet1')
            return sheet              
        sheet = get_gsheet()
        r=2
        for i in range(2,1000):
            val = sheet.cell(i,1).value
            sheet.update_cell(i,1,'')
            if val=='':
                break
        r=2
        for i in tikr_list:
            sheet.update_cell(r,1,i)
            r+=1

        time.sleep(2)
        df = sheet.get_all_records()
        tikr_lst=[]
        ltp_lst=[]
        for i in df:
            tikr_lst.append(i['TIKR'])
            ltp_lst.append(i['LTP'])
        dict={}
        for tikr,ltp in zip(tikr_lst,ltp_lst):
            dict[tikr]=ltp
        print(dict) 

        for key in tikr_list:
            obj = ltp_tikrs.objects.get(tikr=key)
            obj.ltp = dict[key]
            obj.save()
        print('updated LTP from shts')
        return dict
    tikr_list =list(holdings.tikr.value_counts().index)   
        #cell_list = sheet.range("A2:A1000")
    try:
        print("using shts")
        dict = get_ltp_dict(tikr_list)
        return dict
    except:
        print("Not able to fetch shts")
    

def find_ltp2(holdings):
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
    holdings['Reward'] = (holdings['t']-holdings['sl'])
    holdings['Risk'] = (holdings['sl']-holdings['buy'])*holdings['qty']
    holdings['R1'] = -(holdings['sl']-holdings['buy'])*holdings['qty']    
    holdings['R2'] = -2*(holdings['sl']-holdings['buy'])*holdings['qty']
    holdings['R3'] = -3*(holdings['sl']-holdings['buy'])*holdings['qty']

    holdings['Risk_p'] = (holdings['Risk']/holdings['qty'])+holdings['buy']    
    holdings['R1_p'] = (holdings['R1']/holdings['qty'])+holdings['buy']    
    holdings['R2_p'] = (holdings['R2']/holdings['qty'])+holdings['buy']    
    holdings['R3_p'] = (holdings['R3']/holdings['qty'])+holdings['buy']
    holdings['entry'] = [x.strftime("%d-%b-%Y (%H:%M)") for x in holdings['entrydate']]    
    holdings['exit'] = [x.strftime("%d-%b-%Y (%H:%M)") for x in holdings['exitdate']]
    holdings['button_id'] = ["btn_" + str(x) for x in holdings['id']]
    holdings['sell_button_id'] = ["sell_button_" + str(x) for x in holdings['id']]    
    holdings['sell_text_id'] = ["sell_text_" + str(x) for x in holdings['id']]
    holdings['final_p_l'] = (holdings['sell']-holdings['buy'])*holdings['qty']
    return holdings
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
            print(t, " is available")
            dict[t] = obj.ltp
            pass
        except:
            print(t," not available")
            ltp_tikrs.objects.create(tikr=t)
            dict[t] = 0.0
    return dict
def color_risk_reward(holdings,ocheck):
    for i in holdings.index:
            if ocheck=='ltp':
                price_comparison = holdings.loc[i,'ltp']
            else:
                price_comparison = holdings.loc[i,'sell']

            if price_comparison>holdings.loc[i,'Risk_p']:
                holdings.loc[i,'Risk_color'] = 'rgb(78, 247, 78)'
            else:
                holdings.loc[i,'Risk_color'] = 'rgb(255, 0, 0)'

            if price_comparison>holdings.loc[i,'R1_p']:
                holdings.loc[i,'R1_color'] = 'rgb(78, 247, 78)'
            else:
                holdings.loc[i,'R1_color'] = 'rgb(255, 0, 0)'

            if price_comparison>holdings.loc[i,'R2_p']:
                holdings.loc[i,'R2_color'] = 'rgb(78, 247, 78)'
            else:
                holdings.loc[i,'R2_color'] = 'rgb(255, 0, 0)'

            if price_comparison>holdings.loc[i,'R3_p']:
                holdings.loc[i,'R3_color'] = 'rgb(78, 247, 78)'
            else:
                holdings.loc[i,'R3_color'] = 'rgb(255, 0, 0)'
            if price_comparison>holdings.loc[i,'t']:
                holdings.loc[i,'t_color'] = 'rgb(78, 247, 78)'
            else:
                holdings.loc[i,'t_color'] = 'rgb(255, 0, 0)'
            if holdings.loc[i,'pl']>0:
                holdings.loc[i,'pl_color'] = 'rgb(78, 247, 78)'
            else:
                holdings.loc[i,'pl_color'] = 'rgb(255, 0, 0)'
            if holdings.loc[i,'final_p_l']>0:
                holdings.loc[i,'final_pl_color'] = 'rgb(78, 247, 78)'
            else:
                holdings.loc[i,'final_pl_color'] = 'rgb(255, 0, 0)'
            
            sl = holdings.loc[i,'sl']
            target = holdings.loc[i,'t']
            # ltp = holdings.loc[i,'ltp']
            total_dist = target-sl
            travelled_dist = price_comparison-sl
            travelled_perc = travelled_dist/total_dist
            remaining_perc = 1 - travelled_perc
            holdings.loc[i,'t_perc'] = travelled_perc*100
            holdings.loc[i,'rem_perc'] = remaining_perc*100 
    return holdings
def holdings_df_prep_to_html(latest_ltp,sell_status,ocheck):
    holdings = gen_pd_holding()
    dict = get_or_create_ltp()
    if latest_ltp:
        dict = find_ltp(holdings)
    else:
        pass
    holdings['ltp'] = [dict[x] for x in holdings['tikr']]   
    holdings['pl'] = (holdings['ltp']-holdings['buy'])*holdings['qty']
    holdings = color_risk_reward(holdings,ocheck)
    holdings = holdings.copy()[holdings['sell_status']==sell_status]
    return holdings
def portfolio(request):
    if request.method=="POST":
        # print(list(request.POST.keys()))
        keys_ = list(request.POST.keys())
        print(keys_)
        # check if update_ltp was clicked 
        if 'update_ltp' in keys_:
            print('Updating LTP')
            holdings = holdings_df_prep_to_html(latest_ltp=True,sell_status=False,ocheck='ltp')            
            time_happen="Last updated on " + get_live_time()
            json_records = holdings.to_json(orient ='records')
            data = []
            data = json.loads(json_records)
            context = {'d': data,'time_happen':time_happen}
            return render(request,"sector_analysis/portfolio.html",
            context)        
        btn_ids_ = [x for x in keys_ if 'btn' in x ]     
        if len(btn_ids_)>0:            
            print('clicked del button')
            ids_= (list(request.POST.keys()))
            id_ = [x for x in ids_ if 'btn' in x ][0]
            id_ = int(id_.replace('btn_',''))         
            time_happen= str(Holdings.objects.get(pk=id_)) + "-------------> Deleted"
            Holdings.objects.get(pk=id_).delete()
            holdings = holdings_df_prep_to_html(latest_ltp=False,sell_status=False,ocheck='ltp')
            json_records = holdings.to_json(orient ='records')
            data = []
            data = json.loads(json_records)
            context = {'d': data,'time_happen':time_happen}
            return render(request,"sector_analysis/portfolio.html",
            context)
        sell_ids_ = [x for x in keys_ if 'sell_button_' in x ]     
        if len(sell_ids_)>0:
            print('clicked sell button')
            ids_= (list(request.POST.keys()))
            id_ = [x for x in ids_ if 'sell_button' in x ][0]
            id_ = int(id_.replace('sell_button_',''))
            # print(request.POST)
            time_happen= str(Holdings.objects.get(pk=id_)) + "-------------> Sold at " #+ str()
            if (request.POST['sell_text_'+str(id_)]==''):
                print('Need sell value')
            else:
                sell = float(request.POST['sell_text_'+str(id_)])
                print('Sell:',sell)
                h = Holdings.objects.get(pk=id_)
                h.sell = sell
                h.sell_status = True
                # h.exitdate = datetime.now
                time_happen = "Sold " + h.tikr + " at " + str(h.sell)
                h.save()

                holdings = holdings_df_prep_to_html(latest_ltp=False,sell_status=False,ocheck='ltp')
                json_records = holdings.to_json(orient ='records')
                data = []
                data = json.loads(json_records)                
                context = {'d': data,'time_happen':time_happen}
                return render(request,"sector_analysis/portfolio.html",
                context)

    holdings = pd.DataFrame(Holdings.objects.values()).reset_index()
    if len(holdings)>0:
        holdings = holdings_df_prep_to_html(latest_ltp=False,sell_status=False,ocheck='ltp')            
    json_records = holdings.to_json(orient ='records') 
    data = [] 
    data = json.loads(json_records) 
    time_happen = "Values from database"
    context = {'d': data,'time_happen':time_happen} 
    return render(request,"sector_analysis/portfolio.html",
    context)
def dict_sect_comps():
    import os
    s=r'C:\Users\prave\Documents\GitHub\Market-Analysis'
    files = os.listdir(s)
    files = [x for x in files if '.csv' in x]
    files = [x for x in files if '15m_' in x]
    files = [x.split('mdf_15m_')[1].split('.csv')[0] for x in files]
    dict = {}
    for sect in files:
        mdf = pd.read_csv(r"C:\Users\prave\Documents\GitHub\Market-Analysis\mdf_15m_"+sect+".csv")
        mdf = mdf[['industry','tikr']].copy().drop_duplicates()
        dict[sect] = list(mdf.tikr)
    return dict
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
    dict = dict_sect_comps()
    sectors = list(dict.keys())
    return render(request,"sector_analysis/index.html",
    {
    "sectors": sectors,
    "dict":json.dumps(dict) ,
    "img_path":sectors,
    }
    )
def gen_bokeh_chart_for_interval(interval_,tikr):
    from bokeh.plotting import figure, output_file, show 
    from bokeh.embed import components
    from bokeh.models.tools import HoverTool, WheelZoomTool, PanTool, CrosshairTool
    df = pd.read_csv(r"C:\Users\prave\Documents\GitHub\Market-Analysis\f_mdf_"+interval_ +".csv")
    df = df[df.tikr==tikr].copy()
    x=df.index
    y=df.Close
    title=tikr + " " + interval_
    plot = figure(title= title , 
        x_axis_label= 'Candle #', 
        y_axis_label= 'Close', 
        plot_width =400,
        plot_height =400)
    plot.line(x, y, line_width = 2)
    plot.toolbar.active_scroll = plot.select_one(WheelZoomTool)
    script, div = components(plot)
    return script,div
def gen_all_scripts_divs(tikr):
    interval_ = '1wk'
    script_1w,div_1w = gen_bokeh_chart_for_interval(interval_,tikr) 
    interval_ = '1d'
    script_1d,div_1d = gen_bokeh_chart_for_interval(interval_,tikr) 
    interval_ = '15m'
    script_15,div_15 = gen_bokeh_chart_for_interval(interval_,tikr)
    return script_1w,div_1w,script_1d,div_1d,script_15,div_15
def get_sect_comps():
    mdf = pd.read_csv(r"C:\Users\prave\Documents\GitHub\Market-Analysis\f_mdf_15m.csv")
    mdf = mdf.copy()[['tikr','industry']].drop_duplicates()
    mdf = mdf.set_index('industry')
    dict = {}
    for ind in mdf.index:
        dict[ind] = []
    mdf = mdf.reset_index()
    for i in mdf.index:
        dict[mdf.loc[i,'industry']].append(mdf.loc[i,'tikr'])
    return dict
def find_sect_for_tikr(tikr):
    mdf = pd.read_csv(r"C:\Users\prave\Documents\GitHub\Market-Analysis\f_mdf_15m.csv")
    industry= list(mdf[mdf['tikr']==tikr].industry)
    return industry[0]
def gen_btn_ids_comps(tikr):
    # tikr = "MARICO"
    sect = find_sect_for_tikr(tikr)
    sect_comps = get_sect_comps()
    companies = sect_comps[sect]
    btn_ids_comps = ['comp_'+x+'_sector_'+sect for x in companies]
    return btn_ids_comps
def charts(request):
    if request.method=="POST":
        import numpy as np
        req_post_keys = (list(request.POST.keys()))
        comp = [x for x in req_post_keys if 'comp_' in x]
        if  len(comp)>0:
            # btn = [x for x in s if 'comp_' in req_post_keys][0].split('comp_')[1]
            s = comp[0]
            company = s[:s.find('_sector')].strip('comp_')
            sector = s[s.find('_sector'):].strip('_sector_')            
            print(company)
            print(sector)
            tikr = company
            sect = find_sect_for_tikr(tikr)
            script_1w,div_1w,script_1d,div_1d,script_15,div_15 = gen_all_scripts_divs(tikr)   
            sect_comps = get_sect_comps()
            sectors = list(sect_comps.keys())
            dict = json.dumps(sect_comps)
            btn_id_comps = gen_btn_ids_comps(tikr)
            companies =  sect_comps[sect]
            
            #Feed them to the Django template.
            return render(request, 'sector_analysis/charts.html',
                    {'script_15' : script_15 , 'div_15' : div_15 ,
                    'script_1d' : script_1d , 'div_1d' : div_1d ,
                    'script_1w' : script_1w , 'div_1w' : div_1w ,
                    'sectors': sectors,
                    'dict' : dict,
                    'sect' : sect,
                    'btn_sets':zip(btn_id_comps,companies),
                    'company':tikr
                    } ) 
        else:
            if 'tkr' in req_post_keys:
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
                print(req_post_keys)
    tikr = "MARICO"
    sect = find_sect_for_tikr(tikr)
    script_1w,div_1w,script_1d,div_1d,script_15,div_15 = gen_all_scripts_divs(tikr)   
    sect_comps = get_sect_comps()
    sectors = list(sect_comps.keys())
    dict = json.dumps(sect_comps)
    btn_id_comps = gen_btn_ids_comps(tikr)
    companies =  sect_comps[sect]
    
    #Feed them to the Django template.
    return render(request, 'sector_analysis/charts.html',
            {'script_15' : script_15 , 'div_15' : div_15 ,
            'script_1d' : script_1d , 'div_1d' : div_1d ,
            'script_1w' : script_1w , 'div_1w' : div_1w ,
            'sectors': sectors,
            'dict' : dict,
            'sect' : sect,
            'btn_sets':zip(btn_id_comps,companies),
            'company':tikr
            } ) 
def completed(request):
    if request.method=="POST":
        import numpy as np
        keys_ = list(request.POST.keys())
        btn_ids_ = [x for x in keys_ if 'btn' in x ]     
        if len(btn_ids_)>0:            
            print('clicked del button')
            ids_= (list(request.POST.keys()))
            id_ = [x for x in ids_ if 'btn' in x ][0]   
            id_ = int(id_.replace('btn_',''))         
            time_happen= str(Holdings.objects.get(pk=id_)) + "-------------> Deleted"
            Holdings.objects.get(pk=id_).delete()
            holdings = holdings_df_prep_to_html(latest_ltp=False,sell_status=True,ocheck='sell')
            json_records = holdings.to_json(orient ='records')
            data = []
            data = json.loads(json_records)
            context = {'d': data,'time_happen':time_happen}
            return render(request,"sector_analysis/completed.html",
            context)
        
        if 'update_ltp' in keys_:
            print('Updating LTP')
            holdings = holdings_df_prep_to_html(latest_ltp=True,sell_status=True,ocheck='sell')            
            time_happen="Last updated on " + get_live_time()
            json_records = holdings.to_json(orient ='records')
            data = []
            data = json.loads(json_records)
            context = {'d': data,'time_happen':time_happen}
            return render(request,"sector_analysis/completed.html",
            context)

    holdings = pd.DataFrame(Holdings.objects.values()).reset_index()
    if len(holdings)>0:
        holdings = holdings_df_prep_to_html(latest_ltp=False,sell_status=True,ocheck='sell')
    # holdings = holdings.copy()      
    json_records = holdings.to_json(orient ='records') 
    data = [] 
    data = json.loads(json_records) 
    time_happen = "Values from database"
    context = {'d': data,'time_happen':time_happen} 
    return render(request,"sector_analysis/completed.html",
    context)

# Work on bringing calculations to charts - completed
# Add sell and exit date to Portfolio - completed
# Develop page for closed trade - completed

# LTP with google sheets

# Work on highlighting selected industry (no priority)
# Link portfolio to charts 
# Develop Summary of trading 
# Develop scanner for important trade observations
# Add candlestick to bokeh 
# Add volume candles
# Add indicators
# Add technical analysis-live signals 
# Rename x index in charts with datetimes
# Create watchlist
# On charts : Create a line for entry if already present and also point the date on 1d and time in 15m based on entry time
# Link charts with tikr on website link

# def find_ltp_render(holdings):
#     import yfinance as yf
#     tikr_list =list(holdings.tikr.value_counts().index)
#     dict={}
#     ltp_tikrs_ = ltp_tikrs.objects.all()
#     for key in tikr_list:
#         try:
#             obj = ltp_tikrs_.objects.get(tikr=key)
#             dict[key] = obj.ltp
#         except:
#             print('yf render')
#             obj = ltp_tikrs.objects.create(tikr=key)
#             obj.ltp =round(yf.download(key+".NS",period="5d",interval="1d").dropna().tail(1)['Close'][0],2)
#             dict[key]=obj.ltp     
#             time.sleep(1)
#     return dict