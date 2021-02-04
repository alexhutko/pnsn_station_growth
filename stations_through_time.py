#!/home/ahutko/anaconda3/bin/python

import requests
import sys
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.dates import DateFormatter,drange

#----- read latest PNSN SA chanfile
url = 'https://seismo.ess.washington.edu/ahutko/ShakeAlert_Chanfiles/chanfile_uw.dat'
f = requests.get(url)
n = 0
shakealert = []
for line in f.iter_lines():
    try:
        line = line.decode('utf-8')
        sta = line.split()[1]
        lat = line.split()[4]
        if ( lat > 20. and lat < 60. ):
            shakealert.append(sta)
    except:
        pass

nowtime = datetime.datetime.now()
dict_SMA = {}
dict_BB = {}
url = 'http://service.iris.edu/fdsnws/station/1/query?level=channel&network=_PACNW&starttime=2100-01-01T00:00:00&format=text'
f = requests.get(url)
n = 0
for line in f.iter_lines():
    n = n + 1
    if ( n > 1 ):
        line = line.decode('utf-8')
#        print(line)
        net = line.split('|')[0]
        sta = line.split('|')[1]
        cha = line.split('|')[3]
        if ( sta[0:1] != 'Q' and cha[0:2] in [ 'EN', 'HN', 'BH', 'HH' ] ):
            lat = line.split('|')[4]
            lon = line.split('|')[5]
            try:
                startT = datetime.datetime.strptime(line.split('|')[15], '%Y-%m-%dT%H:%M:%S')
                endT = datetime.datetime.strptime(line.split('|')[16], '%Y-%m-%dT%H:%M:%S')
            except:
                endT = datetime.datetime(2100,1,1,0,0,0)
            print(net, sta, cha, lat, lon, startT, endT )
            if ( cha[0:2] in [ 'EN', 'HN' ] ):
                if ( sta in dict_SMA ):
                    if ( startT < dict_SMA[sta][0] ):
                        dict_SMA[sta] = [ startT, net ]
                else:
                    dict_SMA[sta] = [ startT, net ]
            if ( cha[0:2] in [ 'BH', 'HH' ] ):
                if ( sta in dict_BB ):
                    if ( startT < dict_BB[sta][0] ):
                        dict_BB[sta] = [ startT, net ]
                else:
                    dict_BB[sta] = [ startT, net ]

print(len(dict_BB),len(dict_SMA))

ndays =  (nowtime - datetime.datetime(2013,1,1,0,0,0)).days
print(ndays)
nets = [ 'UW', 'UO', 'CC']#,'IU','US','OO','BK' ]
SMAcount = []
BBcount = []
sixchancount = []
dates = []
ySMA = []
yBB = []
ysixchan = []
ytotal = []
for n in range(0,ndays):
    thisday = datetime.datetime(2013,1,1,0,0,0) + datetime.timedelta(days=n)
    dates.append(thisday)
    SMAcount = {'UW':0,'UO':0,'CC':0}#,'IU':0,'US':0,'OO':0,'BK':0}
    BBcount = {'UW':0,'UO':0,'CC':0}#,'IU':0,'US':0,'OO':0,'BK':0}
    sixchancount = {'UW':0,'UO':0,'CC':0}#,'IU':0,'US':0,'OO':0,'BK':0} 
    for sta in dict_SMA:
        net = dict_SMA[sta][1]
        if ( dict_SMA[sta][0] < thisday and net in nets ):
            SMAcount[net] +=1
    for sta in dict_BB:
        net = dict_BB[sta][1]
        if ( sta in dict_SMA ):
            if ( dict_SMA[sta][0] < thisday and net in nets ):
                sixchancount[net] += 1
                SMAcount[net] -=1
        else:
            if ( dict_BB[sta][0] < thisday and net in nets ):
                BBcount[net] +=1

    ySMA.append(sum(SMAcount.values()))
    yBB.append(sum(BBcount.values()))
    ysixchan.append(sum(sixchancount.values()))
    ytotal.append(sum(BBcount.values()) + sum(SMAcount.values()) + sum(sixchancount.values()) )
##    print(thisday,SMAcount['UW'], sum(BBcount.values()) )

ystack = [ ySMA, yBB, ysixchan ]
figname = 'stations_through_time.png'
fig = plt.figure(figsize=(8,5),dpi=180)
ax = fig.add_subplot(111)
ax.stackplot(dates,ystack,labels=['Strong Motion','Broadband','Strong Motion + Broadband 6 channel'])
plt.legend(loc='upper left')
plt.title('Station growth at PNSN (UW, UO, CC)')
plt.savefig(figname)
plt.close("all")


