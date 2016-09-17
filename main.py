#coding:utf-8

import requests,os,re,time
from docopt import docopt
from prettytable import PrettyTable

stationCodeUrl='https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.8966'
searchUrl='https://kyfw.12306.cn/otn/lcxxcx/query?purpose_codes=ADULT&queryDate=%s&from_station=%s&to_station=%s'
ticketPriceUrl='https://kyfw.12306.cn/otn/leftTicket/queryTicketPrice?train_no=%s&from_station_no=%s&to_station_no=%s&seat_types=%s&train_date=%s'

paramStr='''
12306 tickets info query via command-line.

Usage:
    main <from> <to> <date>

Options:
    -h,--help show help menu

Examples:
    main beijing datong 2016-08-25
'''

class search(object):
    headers_C=u'''
    车次 出发 到达 出发时间 到达时间 历时 硬卧 硬座 无座'''
    headers_E=u'''
    train start arrive startT arriveT lishi yw yz wz'''
    def __init__(self,fromCode,toCode,date='2016-10-02'):
        self.stationCodeUrl=stationCodeUrl
        self.__stationConf='stationCode.ini'
        fromCode=self.getStationCode(fromCode)
        toCode=self.getStationCode(toCode)
        self.__searchUrl=searchUrl % (date,fromCode,toCode)
    @property
    def data(self):
        data=requests.get(self.__searchUrl,verify=False)
        data=data.json()['data']['datas']
        for i in data:

        #data=[(i['station_train_code'],i['from_station_name'],i['to_station_name'],i['start_time'],i['arrive_time'],i['lishi'],i['yw_num'],i['yz_num'],i['wz_num']) for i in data]
        return data

    def getStationCode(self,stationCode,filepath='.'):
        path=os.path.join(filepath,self.__stationConf)
        if os.path.exists(path) and ((time.time()-os.stat(path).st_mtime)/60)<360:
            f=open(path,'r')
            data=eval(f.read())
            try:
                #print data[stationCode]
                return data[stationCode]
            except KeyError:
                raise Exception,"请输入正确的地点拼音"
        else:
            f=open(self.__stationConf,'w')
            stations=requests.get(stationCodeUrl,verify=False)
            data=re.findall(r'([A-Z]+)\|([a-z]+)',stations.text)
            data=dict(data)
            data=dict(zip(data.values(),data.keys()))
            pprint.pprint(data,stream=f,indent=4)
            try:
                return data[stationCode]
            except KeyError:
                raise Exception,"请输入正确的地点拼音"
def parseParam(paramStr):
    param=docopt(paramStr)
    fr=param['<from>'].decode("utf-8")
    to=param['<to>'].decode("utf-8")
    date=param['<date>'].decode("utf-8")
    return (fr,to,date)

if __name__=="__main__":
    param=parseParam(paramStr)
    sr=search(*param)
    table=PrettyTable()
    table._set_field_names(sr.__class__.headers_C.split())
    for i in sr.data:
        table.add_row(i)
    print table