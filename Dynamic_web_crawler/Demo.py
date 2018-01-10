from bs4 import BeautifulSoup
from DBUtils.PooledDB import PooledDB
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import requests
import random
import time,os
import sys
import io
import json
import redis
import pymysql
import datetime
import Hero_dic


MySql_pool = PooledDB(pymysql,5,host='localhost',user='root',passwd='killteemo4869123aASD!@#-=',db='loldata',port=3306,charset="utf8")
Redis_pool = redis.ConnectionPool(host='127.0.0.1', port=6379)

"""=======================
Get Ip Proxy List
======================="""
def get_ip_list(url, headers):
    web_data = requests.get(url, headers=headers)
    soup = BeautifulSoup(web_data.text, 'lxml')
    ips = soup.find_all('tr')
    ip_list = []
    for i in range(1, len(ips)):
        ip_info = ips[i]
        tds = ip_info.find_all('td')
        result = os.system('ping -n 1 -w 1 %s'%tds[1].text)
        print('Speeding Ip : %s'%(tds[1].text))
        if not result:
            print('Successful Ip : %s'%(tds[1].text))
            ip_list.append(tds[1].text + ':' + tds[2].text)
    return ip_list

"""=======================
Retrun random Proxy Ip Http
======================="""
def get_random_ip(ip_list):
    proxy_list = []
    for ip in ip_list:
        proxy_list.append('http://' + ip)
    proxy_ip = random.choice(proxy_list)
    proxies = {'http': proxy_ip}
    return proxies

"""=======================
Insert Mysqldb 
======================="""
def Inset_Mysql(sql_str):
    conn = MySql_pool.connection()
    cur=conn.cursor()
    r=cur.execute(sql_str)
    r=cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    print('Insert mysql Successful ! \033[0m!')

"""=======================
Updata Redis 
======================="""
def Set_Redis(t_key,t_value):
    r = redis.Redis(connection_pool=Redis_pool)
    r.set(t_key,t_value.encode('utf8'))
    print('Updata Redis Succesful ! \033[0m!')

"""=======================
Crawler www.laoyuegou.com Data
======================="""
def get_herotrend(url,heders,tier,pos,Tierpox):
    List_json = []
    web_data = requests.get(url,headers=heders)
    if web_data.status_code == 200:
        soup = BeautifulSoup(web_data.text, 'lxml')
        Hero_icon_name = soup.select('span.hero-img > img')
        pro_List = soup.select('span.progreesNum')
        length=len(Hero_icon_name)
        for i in range(length):
            List_json.append('{"HeroName":"%s","HeroIcon":"%s","Win":%s,"Appearance":%s,"Ban":%s}'%(Hero_icon_name[i].attrs["alt"],Hero_dic.dict[Hero_icon_name[i].attrs["alt"]],pro_List[i*3].attrs["data-val"].replace('%',''),pro_List[i*3+1].attrs["data-val"].replace('%',''),pro_List[i*3+2].attrs["data-val"].replace('%','')))
        if len(List_json)< 1:
            sle_time = random.randint(80,100)
            time.sleep(sle_time)
            get_herotrend(url,heders,tier,pos,Tierpox)
        else:
            result = '['+','.join(List_json)+']'
            sql_s = 'INSERT into hero_trend(tierPox,dataJson,UpdateTime,dataFrom)Values(\'%s\',\'%s\',\'%s\',\'%s\')'%(Tierpox,result,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'Crawler')
            Inset_Mysql(sql_s)
            Set_Redis('tierpox:'+Tierpox,result)
    else:
        timeS = random.randint(80,100)
        print('Failed to crawl , Repeatedly obtained , Sleep %s Second'%(timeS))
        time.sleep(timeS)
        get_herotrend(url,heders,tier,pos,Tierpox)



"""=======================
Crawler www.laoyuegou.com Humen
======================="""
def get_Humen(url,heders):
    List_json = []
    web_data = requests.get(url,headers=heders)
    if web_data.status_code == 200:
        soup = BeautifulSoup(web_data.text, 'lxml')
        Aero_name = soup.select('div.item2.serverlogo > span')
        Play_num = soup.select('div.row > div.item3')
        P_mode = soup.select('div.item4 > div.progrees-wrap > span.progreesNum')
        Man_Tate = soup.select('div.item5 > div.contrast-progrees-wrap > div.contrast-bar1 > span') 
        Woman_Tate = soup.select('div.item5 > div.contrast-progrees-wrap > div.contrast-bar2 > span') 
        length=len(Aero_name)
        for i in range(length):
            List_json.append('{"AeroName":"%s","Num":%s,"Mode":%s,"Man":%s,"Women":%s}'%(Aero_name[i].text,Play_num[i].text.replace('人','').replace(',',''),P_mode[i].attrs['data-val'].replace('%',''),Man_Tate[i].attrs['data-val'].replace('%',''),Woman_Tate[i].attrs['data-val'].replace('%','')))
        if len(List_json) < 1:
            sle_time = random.randint(80,100)
            time.sleep(sle_time)
            get_Humen(url,heders)
        else:
            result = '['+','.join(List_json)+']'
            sql_s = 'INSERT into aero_census(dataJson,UpdateTime,dataFrom)VALUES(\'%s\',\'%s\',\'%s\')'%(result,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'Crawler')
            Inset_Mysql(sql_s)
            Set_Redis('aeronum:num',result)
    else:
        timeS = random.randint(80,100)
        print('Failed to crawl , Repeatedly obtained , Sleep %s Second'%(timeS))
        time.sleep(timeS)
        get_Humen(url,heders)


"""=======================
Crawler Champion Info URL
======================="""
def get_Champion_URL(url,heders):
    web_data = requests.get(url,headers = heders)
    if web_data.status_code == 200:
        soup = BeautifulSoup(web_data.text,'lxml')
        List_heroinfo_address = soup.select('a.lol_champion')
        return List_heroinfo_address
    else:
        timeS = random.randint(80,100)
        print('Failed to crawl , Repeatedly obtained , Sleep %s Second'%(timeS))
        time.sleep(timeS)
        get_Champion_URL(url,heders)

"""=======================
Crawler Champion Info Text
======================="""
def get_Champion_Text(url_list,num):
    if num < 137:
        browers = webdriver.Chrome('E:\\ChromeDrive\\chromedriver.exe')
        browers.set_page_load_timeout(80)
        try:
            if num == 5:
                browers.get('http://lol.duowan.com/kled/')
            else:
                browers.get(url_list[num].attrs['href'].replace(' ',''))
            print('Browers is load successful ! \033[0m! ')
            t_info(browers.page_source,num)
            browers.close()
            get_Champion_Text(url_list,num+1)
        except:
            browers.close()
            print('Error : Browers is load Timeout ! \033[0m!')
            get_Champion_Text(url_list,num)
            
            

                

def t_info(page_text,t_num):
    if 200==200:
        if 200==200:
            if 200==200:
                soup = BeautifulSoup(page_text,'lxml')
                champion_Cname = soup.find(attrs={'class':'hero-name'}).text                                  #英雄中文名字
                if champion_Cname == '奥瑞利安索尔':
                    champion_Cname = '奥瑞利安·索尔'
                elif champion_Cname == '雷克赛':
                    champion_Cname = '雷克塞'
                elif champion_Cname == '格雷夫斯':
                    champion_Cname = '格雷福斯'
                elif champion_Cname == '瑞文':
                    champion_Cname = '锐雯'
                champion_title = soup.find(attrs={'class':'hero-title'}).text                                          #英雄称呼

                champion_tag_List = []
                for tag in soup.select('span.hero-tag'):
                    champion_tag_List.append(tag.text)                                                                        
                champion_tag = '|'.join(champion_tag_List)                                                                 #英雄定位


                bg = soup.find_all(attrs={'class':'hero-popup__txt'})
                bg_list = []
                for item in bg:
                    if item.text.find('背景故事') == -1 and len(item.text) > 10:
                        bg_list.append(item.text.replace('\r','').replace('\n','').replace(' ','').strip('“').strip('”'))


                champion_stortyBackground = '|'.join(bg_list)                                                              #背景故事

                

                abi_List = soup.select('div.hero-ability > span > em > i')
                champion_ability_List = []
                for abi in abi_List:
                    champion_ability_List.append(abi.attrs['style'].replace('width:',''))                          
                Difficulty = '|'.join(champion_ability_List)                                                                      #英雄（生存，物理，魔法，难度）
                champion_box_list = []
                champion_box_em_list = soup.select('div.hero-box.ext-attr > div.hero-box__bd > ul > li > em')
                champion_box_span_list = soup.select('div.hero-box.ext-attr > div.hero-box__bd > ul > li > span')
                for num in range(1,len(champion_box_em_list)):
                    champion_box_list.append(champion_box_em_list[num].text+'|'+champion_box_span_list[num].text)
                price = champion_box_span_list[0].text.replace('金币','').replace('点卷','').replace('/','|').replace(' ','')      #售价
                champion_box = '*'.join(champion_box_list)                                                             #英雄基本数据（魔抗属性等）


                Temp_List = []
                Temp = []

                Temp = soup.select('div.mod-tab-bd.J_content > div > div:nth-of-type(2) > div:nth-of-type(1) > div.hero-box__bd > div > div > img')
                for item in Temp:
                    if item.attrs['src'] not in Temp_List:
                        Temp_List.append(item.attrs['src'])
                hero_status = '|'.join(Temp_List)                                                                             #英雄出门装

                Temp_List.clear()
                Temp = soup.select('div.mod-tab-bd.J_content > div > div:nth-of-type(2) > div:nth-of-type(2) > div.hero-box__bd > div > div > img')
                for item in Temp:
                    if item.attrs['src'] not in Temp_List:
                        Temp_List.append(item.attrs['src'])
                hero_Metaphase = '|'.join(Temp_List)                                                                 #英雄中期核心装

                Temp_List.clear()
                Temp = soup.select('div.mod-tab-bd.J_content > div > div:nth-of-type(2) > div:nth-of-type(3) > div.hero-box__bd > div > div > img')
                for item in Temp:
                    if item.attrs['src'] not in Temp_List:
                        Temp_List.append(item.attrs['src'])
                hero_Wind = '|'.join(Temp_List)                                                                          #英雄顺风装
                
                Temp_List.clear()
                Temp = soup.select('div.mod-tab-bd.J_content > div > div:nth-of-type(2) > div:nth-of-type(4) > div.hero-box__bd > div > div > img')
                for item in Temp:
                    if item.attrs['src'] not in Temp_List:
                        Temp_List.append(item.attrs['src'])
                hero_Bad = '|'.join(Temp_List)                                                                            #英雄逆风装
                
                Temp_List.clear()
                Temp = soup.select('div.mod-tab-bd.J_content > div > div:nth-of-type(3) > div:nth-of-type(1) > div.hero-box__bd > ul > li > span > img')
                for item in Temp:
                    if item.attrs['src'] not in Temp_List:
                        Temp_List.append(item.attrs['src'])
                hero_Spells = '|'.join(Temp_List)                                                                         #核心召唤师技能
                
                Temp_List.clear()
                Temp = soup.select('div.mod-tab-bd.J_content > div > div:nth-of-type(3) > div:nth-of-type(2) > div.hero-box__bd > ul > li > div > p')
                for item in Temp:
                    Temp_List.append(item.text)
                hero_Rune = '|'.join(Temp_List)                                                                          #核心符文

                Temp_List.clear()
                Temp = soup.select('div.mod-tab-bd.J_content > div > div:nth-of-type(3) > div.hero-box.ext-other.ext-more > div.hero-box__bd > ul > li > div > p')
                for item in Temp:
                    Temp_List.append(item.text.replace('点',''))
                hero_Talent = '|'.join(Temp_List)                                                                         #天赋加点
                
                hero_Talent_text = soup.find(attrs={'class':'hero-mastery'}).text                        #天赋描述

                hero_userandunuser = soup.find_all(attrs={'class':'hero-advanced__txt'},limit=2)
                
                hero_use = hero_userandunuser[0].text                                                              #英雄优势

                hero_unuse = hero_userandunuser[1].text                                                           #英雄劣势

                hero_birthday = Hero_dic.hero_birthday[champion_title]                                    #英雄上线时间

                
                herowin_data = requests.get(Hero_dic.Win_dic[champion_title],headers=random.choice(Hero_dic.headers))
                if herowin_data.status_code == 200:
                    herowin_soup = BeautifulSoup(herowin_data.text,'lxml')
                    Temp_List.clear()
                    Temp = herowin_soup.select('div.trend-list-wrapper.trend-list-wrapper1 > ul > li > span.img > img')
                    Temp1 = herowin_soup.select('div.trend-list-wrapper.trend-list-wrapper1 > ul > li > span.tname')
                    Temp2 = herowin_soup.select('div.trend-list-wrapper.trend-list-wrapper1 > ul > li > div > span')
                    for item in range(0,5):
                        Temp_List.append(Temp[item].attrs['src']+'|'+Temp1[item].text+'|'+Temp2[item].attrs['data-val'])
                    CoreInstallation = '*'.join(Temp_List)                                                                  #核心装使用

                    Temp_List.clear()
                    for item in range(5,10):
                        Temp_List.append(Temp[item].attrs['src']+'|'+Temp1[item].text+'|'+Temp2[item].attrs['data-val'])
                    SummonerSkills = '*'.join(Temp_List)                                                                 #核心召唤师技能

                    Temp_List.clear()
                    Temp = herowin_soup.select('div.fl.trend-left > div:nth-of-type(3) > div.kezhi > div.clearfix.roles.color-win > div > img')
                    Temp1 = herowin_soup.select('div.fl.trend-left > div:nth-of-type(3) > div.kezhi > div.clearfix.roles.color-win > div > p')
                    for item in range(0,4):
                        Temp_List.append(Temp[item].attrs['src']+'|'+Temp1[item].text)
                    Restraint = '*'.join(Temp_List)                                                                             #克制

                    Temp_List.clear()
                    Temp = herowin_soup.select('div.fl.trend-left > div:nth-of-type(3) > div.kezhi > div.clearfix.roles.color-defeat > div > img')
                    Temp1 = herowin_soup.select('div.fl.trend-left > div:nth-of-type(3) > div.kezhi > div.clearfix.roles.color-defeat > div > p')
                    for item in range(0,4):
                        Temp_List.append(Temp[item].attrs['src']+'|'+Temp1[item].text)
                    Restrained = '*'.join(Temp_List)                                                                           #被克制


                    Temp_List.clear()
                    t_Q = herowin_soup.select('body > section.wrapper.clearfix.trend-wrapper > div.trend-right.fr > div > div.recommend-equipment-wrapper > div.widgets.widgets-jinnegshunxu.mb20 > div.bd > div:nth-of-type(2) > div.row-vals > span')
                    t_W = herowin_soup.select('body > section.wrapper.clearfix.trend-wrapper > div.trend-right.fr > div > div.recommend-equipment-wrapper > div.widgets.widgets-jinnegshunxu.mb20 > div.bd > div:nth-of-type(3) > div.row-vals > span')
                    t_E = herowin_soup.select('body > section.wrapper.clearfix.trend-wrapper > div.trend-right.fr > div > div.recommend-equipment-wrapper > div.widgets.widgets-jinnegshunxu.mb20 > div.bd > div:nth-of-type(4) > div.row-vals > span')
                    t_R = herowin_soup.select('body > section.wrapper.clearfix.trend-wrapper > div.trend-right.fr > div > div.recommend-equipment-wrapper > div.widgets.widgets-jinnegshunxu.mb20 > div.bd > div:nth-of-type(5) > div.row-vals > span')

                    if t_num > 5:
                        for item in range(0,18):
                            if 'current' in t_Q[item].attrs['class']:
                                Temp_List.append('Q')
                            elif 'current' in t_W[item].attrs['class']:
                                Temp_List.append('W')
                            elif 'current' in t_E[item].attrs['class']:
                                Temp_List.append('E')
                            elif 'current' in t_R[item].attrs['class']:
                                Temp_List.append('R')
                    
                    AddPoint = '|'.join(Temp_List)
                    if champion_Cname == '凯隐':
                        AddPoint = 'Q|W|E|Q|Q|R|Q|W|Q|W|R|W|W|E|E|R|E|E'
                    elif champion_Cname == '洛':
                        AddPoint = 'Q|W|E|Q|Q|R|Q|E|Q|E|R|E|E|W|W|R|W|W'
                    elif champion_Cname == '霞':
                        AddPoint = 'Q|W|E|Q|Q|R|Q|W|Q|W|R|W|W|E|E|R|E|E'
                    elif champion_Cname == '卡蜜尔':
                        AddPoint = 'Q|W|E|Q|Q|R|Q|E|Q|E|R|E|E|W|W|R|W|W'
                    elif champion_Cname == '艾翁':
                        AddPoint = 'Q|W|E|Q|Q|R|Q|W|Q|W|R|W|W|E|E|R|E|E'

                    string_json = '"cname":"{0}","title":"{1}","tag":"{2}","bg":"{3}","difficulty":"{4}","price":"{5}","box":"{6}","AddPoint":"{7}","hero_status":"{8}","hero_Metaphase":"{9}","hero_Wind":"{10}","hero_Bad":"{11}","hero_Spells":"{12}","hero_Rune":"{13}","hero_Talent":"{14}","hero_Talent_text":"{15}","hero_use":"{16}","hero_unuse":"{17}","hero_birthday":"{18}","CoreInstallation":"{19}","SummonerSkills":"{20}","Restraint":"{21}","Restrained":"{22}"'
                    
                    josn_result = string_json.format(champion_Cname,Hero_dic.t_title[champion_Cname],champion_tag,champion_stortyBackground,Difficulty,price,champion_box,AddPoint,hero_status,hero_Metaphase,hero_Wind,hero_Bad,hero_Spells,hero_Rune,hero_Talent,hero_Talent_text,hero_use,hero_unuse,hero_birthday,CoreInstallation,SummonerSkills,Restraint,Restrained)
                    
                    josn_result = '[{'+josn_result+'}]'

                    sql_str = 'INSERT into hero_info(c_name,dataJson,UpdateTime,dataFrom)Values(\'%s\',\'%s\',\'%s\',\'%s\')'%(Hero_dic.hero_cname_of_ename[champion_Cname],josn_result,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'Crawler')

                    Inset_Mysql(sql_str)
                    Set_Redis(Hero_dic.hero_cname_of_ename[champion_Cname],'\''+josn_result+'\'')
                    

                    timeS = random.randint(5,10)
                    print('Failed to crawl , Repeatedly obtained , Sleep %s Second'%(timeS))
                    time.sleep(timeS)



"""=======================
Crawler Hero_Win
======================="""
def get_Hero_Win():
    web_data  = requests.get('http://www.laoyuegou.com/x/zh-cn/lol/lol/herotrend.html',headers=random.choice(Hero_dic.headers))
    if web_data.status_code == 200:
        soup = BeautifulSoup(web_data.text,'lxml')
        List_heroinfo_address = soup.find_all(attrs={'class':'row'})
        List_name = soup.select('div.item2 > span.hero-img > img')
        f=open('G:\\f.txt','w')
        for num in range(0,137):
            f.write('\''+List_name[num].attrs['alt']+'\''+':'+'\''+List_heroinfo_address[num].attrs['onclick'].replace('javascript:window.location.href=\'','').replace('\'','')+'\','+'\n')
        f.close()

"""=======================
Select Mysql Update Redis
======================="""
def Select_Mysql():
    conn = MySql_pool.connection()
    cur=conn.cursor()
    r=cur.execute('select concat(\'hero_title_id:\',Title),id from allchampion')
    conn.commit()
    row=cur.fetchall()
    anti = 0
    for i in row:
        anti+=1
        Set_Redis(i[0],i[1])
        print(str(anti) +' ----- successful')


    conn.commit()
    cur.close()
    conn.close()

"""=======================
Crawler free champion
======================="""
def get_free():
    browers = webdriver.Chrome('E:\\ChromeDrive\\chromedriver.exe')
    browers.set_page_load_timeout(160)
    try:
        browers.get('http://lol.qq.com/main.shtml')
        soup = BeautifulSoup(browers.page_source,'lxml')

        free_champion_icon = soup.select('#J_freeList > a > img ')
        free_champion_name = soup.select('#J_freeList > a > span > span')

        new_skin_img = soup.select('#J_skinNew > a > img')
        new_skin_url = soup.select('#J_skinNew > a')

        new_hero_img = soup.select('#J_heroNew > a > img')
        new_hero_name = soup.select('#J_heroNew > a > span > span')

        temp_list = []

        for i in range(0,len(free_champion_icon)):
            temp_list.append('{"img":"%s","name":"%s"}'%(free_champion_icon[i].attrs['src'],free_champion_name[i].text))
    
        free_champion_json = ','.join(temp_list)

        temp_list.clear()
        for i in range(0,len(new_skin_img)):
            temp_list.append('{"img":"%s","url":"%s"}'%(new_skin_img[i].attrs['src'],new_skin_url[i].attrs['href']))
    
        new_skin_json = ','.join(temp_list)

        temp_list.clear()
        for i in range(0,len(new_hero_img)):
            temp_list.append('{"img":"%s","name":"%s"}'%(new_hero_img[i].attrs['src'],new_hero_name[i].text))
    
        new_hero_json = ','.join(temp_list)


        result_json = '{"free":[%s],"skin":[%s],"new":[%s]}'%(free_champion_json,new_skin_json,new_hero_json)

        Set_Redis('free_new_skin:result',result_json)
    except:
        browers.close()
        get_free()


"""=======================
Main
======================="""
if __name__ == '__main__':
    get_Humen(Hero_dic.census_url,random.choice(Hero_dic.headers))
    print('Sleep ............')
    time.sleep(random.randint(10,15))
    for i in [255,0,6,1,2,3,4,5]:
        for j in [0,1,2,3,4,5]:
            get_herotrend(Hero_dic.laoyuegou_url%(i,j),random.choice(Hero_dic.headers),i,j,'t%sp%s'%(i,j))
            sle_time = random.randint(15,25)
            print('T%sP%s'%(i,j)+': Successful !')
            print('Crawler Sleep %s  .............'%(sle_time))
            time.sleep(sle_time)
    
    # List_heroinfo_url = get_Champion_URL(Hero_dic.hero_info_url,random.choice(Hero_dic.headers))
    # get_Champion_Text(List_heroinfo_url,58)

    # if datetime.datetime.now().weekday() == 4:
    #     print('4444')

    # Select_Mysql()

    # get_free()


    # for i in Hero_dic.sele_div.keys():
    #     conn = MySql_pool.connection()
    #     cur=conn.cursor()
    #     r=cur.execute(Hero_dic.sele_div[i])
    #     conn.commit()
    #     row=cur.fetchone()
    #     kyes = i
    #     Set_Redis('hero_list:'+kyes,row[0])





        
        

            


    


    