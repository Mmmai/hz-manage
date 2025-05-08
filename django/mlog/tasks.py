from celery import chain, shared_task
import time,re,requests,datetime,json
from .models import LogModule,LogFlow,LogFlowMission
from django.forms.models import model_to_dict

def reLogLevel(logLine):
    #判断日志等级
    # reStr = 
    isError = False
    if re.match('.*(=|\[|\"|\'| )DEBUG.*',str(logLine),re.IGNORECASE):
        logLevel = 'DEBUG'
    elif re.match('.*(=|\[|\"|\'| )INFO.*',str(logLine),re.IGNORECASE):
        logLevel = 'INFO'
    elif re.match('.*(=|\[|\"|\'| )WARN.*',str(logLine),re.IGNORECASE):
        logLevel = 'WARN'
    elif re.match('.*(=|\[|\"|\'| )ERROR.*',str(logLine),re.IGNORECASE):
        logLevel = 'ERROR'
        isError = True

    elif re.match('.*(=|\[|\"|\'| )FATAL.*',str(logLine),re.IGNORECASE):
        logLevel = 'FATAL'
        isError = True
    else:
        logLevel = 'UNKNOWN'
    return logLevel,isError
def getLokiQuery(reqUrl=None,dateValue=[],limit=100,labelStr='',matchKeyMethod='|~',matchKey=None):
    endTime =  int(str(dateValue[1]).ljust(19,'0'))
    startTime = int(str(dateValue[0]).ljust(19,'0'))
    if matchKey != '':
        query_str = "%s%s`%s`" %(labelStr,matchKeyMethod,matchKey)
    else:
        query_str = labelStr
    # print(query_str)
    try:
        res = requests.get('%s/loki/api/v1/query_range?start=%s&end=%s&limit=%s&query=%s' %(reqUrl,startTime,endTime,limit,query_str)).json()
        # print(res)
        logQueryLists = []
        logLevelLists = []
        errorCount = 0
        for i in res['data']['result']:
            streamRes = i['stream']
            logLineList = i['values']
            for _v in logLineList:
                # logTime = datetime.datetime.fromisoformat(logJson['time'][:23])
                logTime = datetime.datetime.fromtimestamp(int(_v[0])/(1* 10**9)).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.%f')
                # logLine = logJson['log']
                # logLine = _v[1]
                # 判断是否是k8s的日志
                if 'pod' in streamRes.keys():
                    logJson = json.loads(_v[1])
                    logLine = logJson['log']
                else:
                    logLine = _v[1]
                logLevel,isError = reLogLevel(logLine)
                if isError:
                    errorCount += 1
                logQueryLists.append({"lokiTime":_v[0],"logTime":logTime,"level":logLevel,"logLine":logLine.strip('\n'),"stream":streamRes})
                if logLevel not in logLevelLists:
                    logLevelLists.append(logLevel)
        resSummary = res['data']['stats']['summary']
        resSummary["errorCount"] = errorCount
        logQueryRes = {"queryInfo":resSummary,"queryLogLevel":list(set(logLevelLists)),"queryResult":logQueryLists,"status":True}
        return logQueryRes
        # print(res)
    except Exception as e:
        print(e)
        return {"queryInfo":{"errorCount":0},"queryLogLevel":[],"queryResult":[],"status":False}

@shared_task
def lokiAnalysis(params={}):
    # time.sleep(duration)  # 模拟耗时操作
    try:
        # time.sleep(5)
        # print(type(params))
        stime = time.time()
        missionId = params["missionId"]
        allRes = {}
        flowSort = []
        for i in LogFlow.steps.through.objects.filter(flow_id_id=params["flow_id"]).order_by('order').all():
            stepInfo = model_to_dict(LogModule.objects.filter(id=i.step_id_id).first())
            label_name = stepInfo["label_name"]
            label_value = stepInfo["label_value"]
            label_match = stepInfo["label_match"]
            label_str = "{%s%s\"%s\"}" %(label_name,label_match,label_value)
            # print(label_str)
            # 查询loki
            res = getLokiQuery(reqUrl=params["reqUrl"],dateValue=params["dataValue"],limit=params["limit"],labelStr=label_str,matchKeyMethod='|~',matchKey=params["match_key"])
            # print(res)
            allRes[str(i.step_id_id)] = res
            # print(res)
            flowSort.append(str(i.step_id_id))
        result = {"info":allRes,"sort":flowSort} 

        LogFlowMission.objects.filter(mission_id=params["missionId"]).update(results=result,status=1)
        # missionObj.results = result
        # missionObj.status = 1
        # missionObj.save()
        # print(missionObj)

    except Exception as e:
    #     print(e)
        missionObj = LogFlowMission.objects.get(mission_id=params["missionId"])
        missionObj.results = {}
        missionObj.status = 2
        missionObj.save()
    finally:
        costTime = time.time() - stime
        return {"detail": f"任务[{missionId}]已完成，执行时间 {costTime} 秒。"}