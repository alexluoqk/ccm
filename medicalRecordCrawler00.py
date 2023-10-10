import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import os
import pandas as pd

def main():
    fileSeries = 'originalFile366'
    medicalRecord = str(fileSeries) + '.csv'
    wb = pd.read_csv(medicalRecord)
    res = pd.DataFrame(columns = [
        'lastMod',
        'url',
        'bingchengId', 
        'type',
        'physName',
        'patientVote',
        'onlineCons',
        'patientAge',
        #病例信息patientSubjective
        'diseaseInfoList',
        #'diseDesc',
        #'heigWeight',
        #'diseases',
        #'pregnancy',
        #'duration',
        #'prevHosp',
        #'prevDrug',
        #'allergy',
        #'inquiry',
        #问诊建议consultingAdvice
        'recordSum',
        'dispAdvice',
        #患者交流patient-physician conversation
        ## 助理
        ## 医生本人
        ## 患者本人
        'askList',
        'answerList',
        'checkInList'
        ])
    
    driver = webdriver.Firefox(executable_path = os.getcwd() + '/geckodriver')
    driver.maximize_window()


    for index, row in wb.iterrows():
  
        url = str(row[1])
        lastMod = str(row[0])
        abandonedList = list()
        #url = 'https://www.haodf.com/bingcheng/8887929998.html'
        #lastMod = '2022.0.1'

        try:
            data_dict = {
                'lastMod':[],
                'url':[],
                'bingchengId':[], 
                'type':[],
                'physName':[],
                'patientVote':[],
                'onlineCons':[],
                'patientAge':[],
                #病例信息patientSubjective
                'diseaseInfoList':[],
                # 'diseDesc':[],
                # 'heigWeight':[],
                # 'diseases':[],
                # 'pregnancy':[],
                # 'duration':[],
                # 'prevHosp':[],
                # 'prevDrug':[],
                # 'allergy':[],
                # 'inquiry':[],
                #问诊建议consultingAdvice
                'recordSum':[],
                'dispAdvice':[],
                #患者交流patient-physician conversation
                ## 助理
                ## 医生本人
                ## 患者本人
                'askList':[],
                'answerList':[],
                'checkInList':[]
                }
            
            driver.get(url)
            data = driver.page_source
            soup = BeautifulSoup(data, 'lxml')

            data_dict['lastMod'].append(lastMod)

            data_dict['url'].append(url)
            
            bingchengId = re.match(r'.*bingcheng/(\d+).html', url).group(1)
            data_dict['bingchengId'].append(bingchengId)
            
            item_type = str(soup.find_all('span', class_ = "bc-title-type"))
            rule_type = re.compile(r'<span class="bc-title-type">(.*?)</span>')
            type = re.findall(rule_type, item_type)
            data_dict['type'].append(type)

            item_physName = str(soup.find_all('span', class_="info-text-name"))
            rule_physName = re.compile(r'<span class="info-text-name">(.*?)</span>')
            physName = re.findall(rule_physName, item_physName)
            data_dict['physName'].append(physName)  

            item_patientVote = str(soup.find_all('div', class_="item-detail")[0]).replace('\n', '').replace('\r', '').replace(' ', '').replace('\t', '')
            item_onlineCons = str(soup.find_all('div', class_="item-detail")[1]).replace('\n', '').replace('\r', '').replace(' ', '').replace('\t', '')
            rule_p_o = re.compile(r'<divclass="item-detail">(.*?)</div>')
            patientVote = re.findall(rule_p_o, item_patientVote)
            onlineCons = re.findall(rule_p_o, item_onlineCons)
            data_dict['patientVote'].append(patientVote)
            data_dict['onlineCons'].append(onlineCons)

            item_patientAge = str(soup.find_all('p', class_="patient-card-info"))
            rule_patientAge = re.compile(r'<p class="patient-card-info">(.*?)</p>')
            patientAge = re.findall(rule_patientAge, item_patientAge)
            data_dict['patientAge'].append(patientAge)  

            str_diseaseinfo = str(soup.find_all('p', class_="diseaseinfo")).replace('\n', '').replace('\r', '').replace(' ', '').replace('\t', '')
            rule_diseaseDesc = re.compile(r'<spanclass="info3-valuenewline">(.*?)</span>')
            rule_prevHospAllergy = re.compile(r'<spanclass="info3-valueinfo3-pointnewline">(.*?)</span>')
            rule_prevDiseList = re.compile(r'<spanclass="info3-valueinfo3-point">(.*?)</span>')
            diseaseDesc = re.findall(rule_diseaseDesc, str_diseaseinfo)
            prevHospAllergy = re.findall(rule_prevHospAllergy, str_diseaseinfo)
            prevDiseList = re.findall(rule_prevDiseList, str_diseaseinfo)
            diseaseInfoList = list()
            diseaseInfoList.append([diseaseDesc, prevHospAllergy, prevDiseList])
            data_dict['diseaseInfoList'].append(diseaseInfoList)

            if len(soup.find_all('span', class_="suggestions-text-value")) == 0:
                data_dict['recordSum'].append(0)
                data_dict['dispAdvice'].append(0)
            else:
                item_recordSum = str(soup.find_all('span', class_="suggestions-text-value")[0]).replace('\n', '').replace('\r', '').replace(' ', '').replace('\t', '')
                item_dispAdvice = str(soup.find_all('span', class_="suggestions-text-value")[1]).replace('\n', '').replace('\r', '').replace(' ', '').replace('\t', '')
                rule_r_d = re.compile(r'<spanclass="suggestions-text-value">(.*?)</span>')
                recordSum = re.findall(rule_r_d, item_recordSum)
                dispAdvice = re.findall(rule_r_d, item_dispAdvice)
                data_dict['recordSum'].append(recordSum)
                data_dict['dispAdvice'].append(dispAdvice)
            #print('recordSum:' + str(data_dict['recordSum']) + ' and dispAdvice:' + str(data_dict['dispAdvice']))

            #'Physician':[]
            if len(soup.find_all('div', class_="item-left")) == 0:
                data_dict['answerList'].append(0)
            else:
                for i, detail in enumerate(soup.find_all('div', class_="item-left")):
                    rule_detail_answerTimeStamp = re.compile(r'<divclass="msg-time">(.*?)</div>')
                    rule_detail_answerTitle = re.compile(r'<spanclass="content-com-title">(.*?)</span>')
                    rule_detail_answerText = re.compile(r'<spanclass="content-com-text">(.*?)</span>|<spanclass="content-himcontent-text".*>(.*?)</span>|<spanclass="content-himcontent-privacy".*>(.*?)</span>')
                    rule_detail_answerAudio = re.compile(r'<spanclass="content-audio-time">(.*?)</span>|<spanclass="content-audio-text">(.*?)</span>')
                    detail = str(detail).replace('\n', '').replace('\r', '').replace(' ', '').replace('\t', '')
                    answerTimeStamp = re.findall(rule_detail_answerTimeStamp, detail)
                    answerTitle = re.findall(rule_detail_answerTitle, detail)
                    answerText = re.findall(rule_detail_answerText, detail)
                    answerAudio = re.findall(rule_detail_answerAudio, detail)
                    answerList = list()
                    answerList.append([i, answerTimeStamp, answerTitle, answerText, answerAudio])
                    data_dict['answerList'].append(answerList)
            #print('answerList:' + str(data_dict['answerList']))

            #'Patient':[]
            if len(soup.find_all('div', class_="item-right")) == 0:
                data_dict['askList'].append(0)
            else:
                for i, detail in enumerate(soup.find_all('div', class_="item-right")):
                    rule_detail_askTimeStamp = re.compile(r'<divclass="msg-time">(.*?)</div>')
                    rule_detail_askText = re.compile(r'<spanclass="content-himcontent-text.*>(.*?)</span>|<spanclass="content-himcontent-privacy.*>(.*?)</span>')
                    detail = str(detail).replace('\n', '').replace('\r', '').replace(' ', '').replace('\t', '')
                    askTimeStamp = re.findall(rule_detail_askTimeStamp, detail)
                    askText = re.findall(rule_detail_askText, detail)
                    askList = list()
                    askList.append([i, askTimeStamp, askText])
                    data_dict['askList'].append(askList)
            #print('askList:' + str(data_dict['askList']))

            #Online check-in
            if len(soup.find_all('li', class_="shared-article-item")) == 0:
                data_dict['checkInList'].append(0)
            else:
                for i, detail in enumerate(soup.find_all('li', class_="shared-article-item")):
                    rule_detail_title = re.compile(r'<aclass.*>(.*?)</a>')
                    rule_detail_timeLine = re.compile(r'<spanclass="item-time">(.*?)</span>')
                    rule_detail_relatedType = re.compile(r'<divclass="article-item-info">.*</span>(.*?)</div>')
                    detail = str(detail).replace('\n', '').replace('\r', '').replace(' ', '').replace('\t', '')
                    title = re.findall(rule_detail_title, detail)
                    timeLine = re.findall(rule_detail_timeLine, detail)
                    relatedType = re.findall(rule_detail_relatedType, detail)
                    checkInList = list()
                    checkInList.append([i, title, timeLine, relatedType])
                    data_dict['checkInList'].append(checkInList)     
            #print('checkInList:' + str(data_dict['checkInList']))

            res_items = pd.DataFrame.from_dict(data_dict, orient='index').transpose()
            dt = datetime.datetime.now().strftime('%Y%m%d-%H')
            print('目前爬取量：',index+1 ,'/', int((wb.size)/2))
            res = pd.concat([res, res_items], axis=0)              
            if index%11000 == 0:            
                #res.reset_index(drop=True, inplace=True)     
                res.to_csv('wenzhen_' + str(fileSeries) + str(dt) +'.csv', index=True, encoding='utf-8') 
            if int(index+1) == int(((wb.size)/2)):
                res.to_csv('wenzhen_END' + str(fileSeries) + str(dt) +'.csv', index=True, encoding='utf-8')

        except:
            # data_dict = {
            #     'lastMod':[lastMod],
            #     'url':[url],
            #     'bingchengId':[bingchengId],
            #     'type':[0],
            #     'physName':[0],
            #     'patientVote':[0],
            #     'onlineCons':[0],
            #     'patientAge':[0],
            #     'diseaseInfoList':[0],
            #     'recordSum':[0],
            #     'dispAdvice':[0],
            #     'askList':[0],
            #     'answerList':[0],
            #     'checkInList':[0]
            #     }
            # res = pd.concat([res, pd.DataFrame.from_dict(data_dict, orient='index').transpose()], axis=1)
            # dt = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S')
            # res.to_csv('abandoned_' + str(dt) +'.csv', index=True)    
            abandonedList.append([lastMod, url, bingchengId, fileSeries])
            print(abandonedList)

            f = open(r'abandonedList.txt', 'a+')
            for line in abandonedList:                
                f.write(str(line) + '\n')
                f.close()
            continue
    
if __name__ == "__main__":
        main()