import pandas as pd
import urllib
from sklearn.svm import SVR
import numpy as np
import talib
from matplotlib import pyplot as plt
from sklearn.svm import SVR
import sys, os

class algo_trading(object):
    
    def __init__(self,stock):
        ticker = stock
        stock=ticker+".csv"
        try:
            data = pd.read_csv(stock)
        except:    
            try:
                url="https://www.google.com/finance/historical?output=csv&q="+ticker
                stock=ticker+".csv"
                urllib.request.urlretrieve(url,stock)
            except:
                try:
                    print("Retrying..")
                    url="https://www.google.com/finance/historical?output=csv&q="+ticker
                    stock=ticker+".csv"
                    urllib.request.urlretrieve(url,stock)
                except:
                    print("Connection Error..")
                    exit(0)
        data = pd.read_csv(stock)
        self.data = data
        
    def deviation_trade(self):
        data = self.data
        close = ((data['Close'].values.astype(float))[::-1])[-10:]
        clf = SVR(C= 1e3, gamma= 0.1,kernel='linear')
        X = np.arange(1,len(close)+1,1.0).reshape(-1,1)
        y = clf.fit(X,close).predict(X)
        r_squared = clf.score(X,close)
        grad = (y[-1]-y[0])/y[0]
        deviations = [ abs(y[i]-close[i])/close[i] for i in range(len(y))]
        std = np.std(deviations)
        rating = grad * std
        return rating
        
    def cci_trade(self,x,y,a,b):  
        data = self.data
        close = (data['Close'].values.astype(float))[::-1]
        high = (data['High'].values.astype(float))[::-1]
        low = (data['Low'].values.astype(float))[::-1]
        cci_14 = talib.CCI(high,low,close,timeperiod=14)
        rsi_14 = talib.RSI(close,timeperiod=14)
        fee = []
        present = False
        buy=[]
        sell=[]
        volume = 2000
        activity = []
        for i in range(len(cci_14)):  
            if i == len(cci_14)-1 and present==True:
                sell.append(volume*close[i])
                if (volume*close[i]*0.0028)<5000:
                    fee.append(5000)
                else:
                    fee.append(volume*close[i]*0.0028)    
                present = False    
                print("sell at: ",close[i],i,cci_14[i])
                activity.append(i)
            elif cci_14[i]<x and present==False and rsi_14[i]<a and i != len(cci_14)-1:
                buy.append(volume*close[i]) 
                present = True
                print("buy at: ",close[i],i,cci_14[i])  
                if (volume*close[i]*0.0018)<5000:
                    fee.append(5000)
                else:
                    fee.append(volume*close[i]*0.0018)
                activity.append(i)    
            elif cci_14[i]>y and present==True and rsi_14[i]>b and i != len(cci_14)-1:
                sell.append(volume*close[i])
                print("sell at: ",close[i],i,cci_14[i])
                if (volume*close[i]*0.0028)<5000:
                    fee.append(5000)
                else:
                    fee.append(volume*close[i]*0.0028)
                present = False
                activity.append(i)
            else:
                pass   
        
        # Ensure trade lists are balanced. It's possible to end the loop with a
        # buy that was never sold, which previously raised an IndexError when
        # trying to access ``sell[-1]``. Drop any unmatched trades along with
        # their associated fees and activity markers.
        while len(buy) > len(sell):
            buy.pop()
            if fee:
                fee.pop()
            if activity:
                activity.pop()
        while len(sell) > len(buy):
            sell.pop()
            if fee:
                fee.pop()
            if activity:
                activity.pop()
        
            
        trading = len(buy)+len(sell)    
        tot_fee = sum(fee)
        returns = (sum(sell)-sum(buy))/sum(buy)
        fee_rat = tot_fee/(sum(sell)-sum(buy))
        net_returns = (sum(sell)-(sum(buy)+tot_fee))/sum(buy)
        print("\nreturns: ",returns*100,"%")
        print("total fee:",tot_fee)
        print("fee ratio: ",fee_rat)
        print("net returns: " ,net_returns*100,"%")
        print("trading count: ",trading)
        plt.plot(close,'-D',markevery=activity)
        return returns
# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__

blockPrint()

def optimize(stock):
    x = range(-100,-150,-5)
    y = range(100,160,5)
    a = range(20,40,5)
    b = range(60,80,5)
    stock = algo_trading(stock)
    rets = []
    for i in x:
        for j in y:
            for k in a:
                for l in b:
                    try:
                        r = stock.cci_trade(j,i,k,l)
                        rets.append([r,i,j,k,l])
                    except:
                        pass
    sorted_rets = sorted(rets,key=lambda x:x[0])  
    return sorted_rets[-1] 
             
stock = algo_trading('lq45')
r = stock.cci_trade(-145,155,30,75)
                
