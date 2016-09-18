#coding:utf-8

import requests,os,re,time,pprint
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
            train_no=i['train_no']
            from_station_no=i['from_station_no']
            to_station_no=i['to_station_no']
            seat_types=i['seat_types']
            train_date=i['start_train_date']
            train_date="-".join((train_date[:4],train_date[4:6],train_date[6:]))
            ticket_price_url=ticketPriceUrl % (train_no,from_station_no,to_station_no,seat_types,train_date)
            ticket_price=requests.get(ticket_price_url,verify=False).json()['data']
            yw_price=ticket_price['A3'] if ticket_price.has_key("A3") else '-'
            yz_price=ticket_price['A1'] if ticket_price.has_key("A1") else '-'
            wz_price=ticket_price['WZ'] if ticket_price.has_key("WZ") else '-'
            yield i['station_train_code'],i['from_station_name'],i['to_station_name'],i['start_time'],i['arrive_time'],i['lishi'],"/".join((i['yw_num'],yw_price)),"/".join((i['yz_num'],yz_price)),"/".join((i['wz_num'],wz_price))

    def getStationCode(self,stationCode,filepath='.'):
        path=os.path.join(filepath,self.__stationConf)
        if os.path.exists(path) and ((time.time()-os.stat(path).st_mtime)/60)<360:
            f=open(path,'r')
            data=eval(f.read())
            try:
                print data[stationCode]
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