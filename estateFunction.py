import pandas as pd
import json
import requests

def preprocessing(data):
    data.columns=data.iloc[15]
    data=data[16:]
    data=data.reset_index()
    del data['index']
    del data.columns.name
    data['latitude']=1.1
    data['longitude']=1.1
    
    data.loc[data['단지명']=='천왕이펜하우스1단지','도로명']='천왕로 91'    
    data.loc[data['단지명']=='래미안포레','본번']='361'
    data.loc[data['단지명']=='강남한양수자인(4단지)','본번']='77'
    data.loc[data['단지명']=='강남한신휴플러스8단지','본번']='217'
    data.loc[data['단지명']=='강남한신휴플러스6단지','본번']='336'
    data.loc[data['단지명']=='천왕이펜하우스2단지','도로명']='천왕로 92'
    data.loc[data['단지명']=='천왕이펜하우스3단지','도로명']='천왕로 56'
    data.loc[data['단지명']=='천왕이펜하우스4단지','도로명']='천왕로 29'
    data.loc[data['단지명']=='천왕이펜하우스5단지','도로명']='천왕로 10'
    data.loc[data['단지명']=='천왕이펜하우스6단지','도로명']='천왕로 9'
    data.loc[data['단지명']=='코지한주','도로명']='덕릉로123길 53'
    return data

def changeObjectToNumber(train,column):
    def removeComma(data):
        return "".join(data.split()[0].split(','))
    train[column]=train[column].apply(removeComma).astype('float')
    return train


def changeSomeData(data):
    data['big']=data['시군구'].apply(lambda e:e.split(' ')[1])
    data['small']=data['시군구'].apply(lambda e:e.split(' ')[2])
    del data['계약일']
    def makingMonth(date):
        date=str(date)
        return str(date[4])+str(date[5])
    data['month']=data['계약년월'].apply(makingMonth)
    return data


def getPlace(start,train):
    
    def getLatLng(addr):                                    ###give a address and then get the latitude, longitude
        url = 'https://dapi.kakao.com/v2/local/search/address.json?query='+addr
        headers = {"Authorization": "API신청후 얻은 KEY를 입력"}
        result = json.loads(str(requests.get(url,headers=headers).text))
        match_first = result['documents'][0]['address']
        return float(match_first['y']),float(match_first['x'])

    def getLatLng2(addr):                                   ###도로명으로 반환할경우 값이  반환형태가 아주 약간다름
        url = 'https://dapi.kakao.com/v2/local/search/address.json?query='+addr
        headers = {"Authorization": "API신청후 얻은 KEY를 입력"}
        result = json.loads(str(requests.get(url,headers=headers).text))
        match_first = result['documents'][0]                ###요차이 밖에 없다
        return float(match_first['y']),float(match_first['x'])

    def getLatLng3(addr):    ###오류 확인활때 전체 값 볼려고 
        url = 'https://dapi.kakao.com/v2/local/search/address.json?query='+addr
        headers = {"Authorization": "API신청후 얻은 KEY를 입력"}
        result = json.loads(str(requests.get(url,headers=headers).text))
        return result

    for i in range(start,len(train)):                                            ###에러 다시 해야될때 range옆에 숫자로 시작지점 조절
        try:
            place=getLatLng(str(train['시군구'][i])+' '+str(train['본번'][i])+'-'+str(train['부번'][i]))
            train['latitude'][i]=place[0]
            train['longitude'][i]=place[1]
        except IndexError :
            try:
                place=getLatLng(str(train['시군구'][i])+' '+str(train['번지'][i]))
                train['latitude'][i]=place[0]
                train['longitude'][i]=place[1]
            except IndexError :
                try:
                    place=getLatLng2(str(train['시군구'][i])+' '+str(train['도로명'][i]))
                    train['latitude'][i]=place[0]
                    train['longitude'][i]=place[1]
                except IndexError:
                    pass
    return train

###3개월에 2번 거래된거 나중에 거래된거 삭제
def deleteOutlier(data):
    i=0
    while(True):
        try:
            if (data["단지명"][i]==data["단지명"][i+1]) and (data["전용면적(㎡)"][i]==data["전용면적(㎡)"][i+1]) and (data["층"][i]==data["층"][i+1]):
                if data.iloc[i+1]["계약년월"]-data.iloc[i]["계약년월"]<4:
                    data=data.drop(i+1,0)
                    data=data.reset_index()
                    del data["index"]
                    continue                             ###i값 증가시키면안됨.
            i=i+1  
        except KeyError:
            break
    return data

###전판매가 5배 이상인거 삭제 
def deleteOutlier2(data):
    i=0
    while(True):
        try:
            if (data["단지명"][i]==data["단지명"][i+1]) and (data["전용면적(㎡)"][i]==data["전용면적(㎡)"][i+1]) and (data["층"][i]==data["층"][i+1]):
                if data.iloc[i+1]["거래금액(만원)"]>data.iloc[i]["거래금액(만원)"]*5:
                    data=data.drop(i+1,0)
                    data=data.reset_index()
                    del data["index"]
                    continue
            i=i+1
        except KeyError:
            break
    return data