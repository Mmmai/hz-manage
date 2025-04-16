from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
import requests,json,re,datetime
from datetime import timezone,timedelta
from .models import LogModule,LogFlow,LogFlowMission
from django.forms.models import model_to_dict
from mapi.models import UserInfo,Datasource
from .tasks import lokiAnalysis
from celery.result import AsyncResult
from django.http import StreamingHttpResponse
import time,json
def lokiLabels(request):
    #print(1111)
    if request.method == 'GET':
        reqUrl = request.GET.get('url')
        labelsRes = requests.get('%s/loki/api/v1/labels' %reqUrl).json()
        #print(labelsRes)
        labelsJson = {}
        _data = []
        for i in labelsRes['data']:
            _data.append({'value':i,"label":i})
        labelsJson = {"status":labelsRes['status'],"data":_data}
        # print(labelsJson)
        return JsonResponse(labelsJson)
    elif request.method == 'POST':
        #print(123)
        print(request.POST)    
def lokiLabelValue(request):
    #print(1111)
    if request.method == 'GET':
        #print(request.GET)
        label = request.GET.get('label')
        reqUrl = request.GET.get('url')
        labelsRes = requests.get('%s/loki/api/v1/label/%s/values' %(reqUrl,label)).json()
        #print(labelsRes)
        labelsJson = {}
        _data = []
        for i in labelsRes['data']:
            _data.append({'value':i,"label":i})
        labelsJson = {"status":labelsRes['status'],"data":_data}
        # print(labelsJson)
        return JsonResponse(labelsJson)
    elif request.method == 'POST':
        #print(123)
        print(request.POST)    
def lokiQuery(request):
    if request.method == 'POST':
        #print(123)
        reqdata = json.loads(request.body)
        limit = reqdata['limit']
        reqUrl = reqdata['dataSourceUrl']
        # 格式化查询时间,补全到19位
        endTime =  int(str(reqdata['dateValue'][1]).ljust(19,'0'))
        startTime = int(str(reqdata['dateValue'][0]).ljust(19,'0'))
        #startTime = dateRange[0]
        matchKey = reqdata['matchKey']
        matchKeyMethod = reqdata['matchKeyMethod']
        # 处理标签值
        labelFilters = reqdata['labelFilters']
        labelKeyList = labelFilters.keys()
        labelStartStr = '{'
        labelStrList = []
        for k,v in reqdata['labelFilters'].items():
            labelName = v['labelName']
            if isinstance(v['labelValue'], list):
                labelValue = '|'.join(v['labelValue'])
            else:
                labelValue = v['labelValue']
            matchMethod = v['matchMethod']
            _labelStr = "%s%s\"%s\"" %(labelName,matchMethod,labelValue)
            labelStrList.append(_labelStr)

        labelStr = "{" + ','.join(labelStrList) +"}"
        #print(reqdata)
        if matchKey != '':
            query_str = "%s%s`%s`" %(labelStr,matchKeyMethod,matchKey)
        else:
            query_str = labelStr
        print(query_str)
        res = requests.get('%s/loki/api/v1/query_range?start=%s&end=%s&limit=%s&query=%s' %(reqUrl,startTime,endTime,limit,query_str)).json()
        # print(res)
        logQueryLists = []
        logLevelLists = []
        for i in res['data']['result']:
            streamRes = i['stream']
            logLineList = i['values']
            for _v in logLineList:
                # logTime = datetime.datetime.fromisoformat(logJson['time'][:23])
                logTime = datetime.datetime.fromtimestamp(int(_v[0])/(1* 10**9)).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.%f')
                # logLine = logJson['log']
                # 判断是否是k8s的日志
                if 'pod' in streamRes.keys():
                    logJson = json.loads(_v[1])
                    logLine = logJson['log']
                else:
                    logLine = _v[1]
                #判断日志等级
                if re.match('.*(=|\[|\"|\'| )DEBUG.*',str(logLine),re.IGNORECASE):
                    logLevel = 'DEBUG'
                elif re.match('.*(=|\[|\"|\'| )INFO.*',str(logLine),re.IGNORECASE):
                    logLevel = 'INFO'
                elif re.match('.*(=|\[|\"|\'| )WARN.*',str(logLine),re.IGNORECASE):
                    logLevel = 'WARN'
                elif re.match('.*(=|\[|\"|\'| )ERROR.*',str(logLine),re.IGNORECASE):
                    logLevel = 'ERROR'
                elif re.match('.*(=|\[|\"|\'| )FATAL.*',str(logLine),re.IGNORECASE):
                    logLevel = 'FATAL'
                else:
                    logLevel = 'UNKNOWN'
                logQueryLists.append({"lokiTime":_v[0],"logTime":logTime,"level":logLevel,"logLine":logLine.strip('\n').strip('\n'),"stream":streamRes})
                if logLevel not in logLevelLists:
                    logLevelLists.append(logLevel)
        logQueryRes = {"queryInfo":res['data']['stats']['summary'],"queryLogLevel":list(set(logLevelLists)),"queryResult":logQueryLists}
        # print(logQueryLists)
        return JsonResponse(logQueryRes)

def lokiNearLogQuery(request):

    if request.method == 'POST':
        #print(123)
        #{某一行的log，limit}
        reqdata = json.loads(request.body)
        limit = reqdata['limit']
        # print(reqdata)
        reqUrl = reqdata['url']
        url = '%s/loki/api/v1/query_range' %reqUrl

        targetLog = reqdata['targetLog']
        targetLogTime = targetLog['lokiTime']
        # 方向，往前还是往后
        direction = reqdata['direction']
        if direction == 'backward':
            startTime = int(targetLogTime)-7200*1000*1000*1000
            endTime = int(targetLogTime)
        elif direction == 'forward':
            startTime = int(targetLogTime)
            endTime = int(targetLogTime)+7200*1000*1000*1000
        # elif direction == 'all':
        #     startTime = int(targetLogTime)-7200*1000*1000*1000
        #     endTime = int(targetLogTime)+7200*1000*1000*1000
        #     limit = 2*int(limit)
        else:
            return HttpResponse('error')
        
        # 处理标签值
        labelStrList = []
        for k,v in targetLog['stream'].items():
            _labelStr = "%s=\"%s\"" %(k,v)
            labelStrList.append(_labelStr)

        query_str = "{" + ','.join(labelStrList) +"}"
        #print(reqdata)
        #print(query_str)
        queryParams = {
            "limit":limit,
            "direction":direction,
            "start":startTime,
            "end":endTime,
            "query":query_str
        }
        # res = requests.get('http://192.168.163.100:30187/loki/api/v1/query_range?start=%s&end=%s&limit=%s&query=%s' %(startTime,endTime,limit,query_str)).json()
        # print(res)
        res = requests.get(url,queryParams,verify=False).json()

        logQueryLists = []
        logQueryDict = {}
        logLevelLists = []
        for i in res['data']['result']:
            streamRes = i['stream']
            logLineList = i['values']
            for _v in logLineList:
                # logTime = datetime.datetime.fromisoformat(logJson['time'][:23]).strftime('%Y-%m-%d %H:%M:%S.%f')
                logTime = datetime.datetime.fromtimestamp(int(_v[0])/(1* 10**9)).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S.%f')
                # 判断是否是k8s的日志
                if 'pod' in streamRes.keys():
                    logJson = json.loads(_v[1])
                    logLine = logJson['log']
                else:
                    logLine = _v[1]
                #判断日志等级
                if re.match('.*(=|\[|\"|\'| )DEBUG.*',str(logLine),re.IGNORECASE):
                    logLevel = 'DEBUG'
                elif re.match('.*(=|\[|\"|\'| )INFO.*',str(logLine),re.IGNORECASE):
                    logLevel = 'INFO'
                elif re.match('.*(=|\[|\"|\'| )WARN.*',str(logLine),re.IGNORECASE):
                    logLevel = 'WARN'
                elif re.match('.*(=|\[|\"|\'| )ERROR.*',str(logLine),re.IGNORECASE):
                    logLevel = 'ERROR'
                elif re.match('.*(=|\[|\"|\'| )FATAL.*',str(logLine),re.IGNORECASE):
                    logLevel = 'FATAL'
                else:
                    logLevel = 'UNKNOWN'
                logQueryDict[_v[0]] = {"lokiTime":_v[0],"logTime":logTime,"level":logLevel,"logLine":logLine.strip('\n'),"stream":streamRes}
                logQueryLists.append({"lokiTime":_v[0],"logTime":logTime,"level":logLevel,"logLine":logLine.strip('\n'),"stream":streamRes})
                if logLevel not in logLevelLists:
                    logLevelLists.append(logLevel)
            # #往前看就
            if direction == 'backward':
                logQueryListRes = sorted(logQueryLists, key=lambda x: x['lokiTime'])
            else:
                logQueryListRes = logQueryLists
            
        logQueryRes = {"queryInfo":res['data']['stats']['summary'],"queryLogLevel":list(set(logLevelLists)),"queryResult":logQueryListRes}
        #print(log)
        return JsonResponse(logQueryRes)


# 同用的获取日志的接口
# 日志等级获取
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

def lokiStepQuery_bak(request):
    if request.method == 'POST':
        reqdata = json.loads(request.body)
        print(type(reqdata))
        flow_id = reqdata['flowId']
        mission_id = reqdata['missionId']
        
        match_key = reqdata['matchKey']
        missionObj = LogFlowMission.objects.filter(mission_id=mission_id).first()
        # 获取数据源的url
        dataSourceId = reqdata['dataSourceId']
        dataSourceObj = Datasource.objects.filter(id=dataSourceId).first()
        reqUrl = dataSourceObj.url
        dataValue = reqdata["dateValue"]
        username = reqdata["username"]
        # 通过flowid获取stepid
        # flowLogObj = LogFlow.objects.filter(id=flow_id).first()
        allRes = {}
        flowSort = []
        for i in LogFlow.steps.through.objects.filter(flow_id_id=flow_id).order_by('order').all():
            stepInfo = model_to_dict(LogModule.objects.filter(id=i.step_id_id).first())
            print(stepInfo)
            label_name = stepInfo["label_name"]
            label_value = stepInfo["label_value"]
            label_match = stepInfo["label_match"]
            label_str = "{%s%s\"%s\"}" %(label_name,label_match,label_value)
            # print(label_str)
            # 查询loki
            res = getLokiQuery(reqUrl=reqUrl,dateValue=dataValue,limit=500,labelStr=label_str,matchKeyMethod='|~',matchKey=match_key)
            # print(res)
            allRes[i.step_id_id] = res
            print(res)
            flowSort.append(i.step_id_id)
        # allRes["flowSort"] = flowSort
        # print(allRes)
        # print(flow_id)
        result = {"info":allRes,"sort":flowSort}
        # 记录入库
        if not missionObj:
            flowLogObj = LogFlow.objects.filter(id=flow_id).first()
            userObj = UserInfo.objects.filter(username=username).first()
            LogFlowMission.objects.create(
                mission_id = mission_id,
                task_id = match_key,
                flow_id = flowLogObj,
                user_id = userObj,
                dataSource_id = dataSourceObj,
                status = 0,
                mission_query = reqdata,
                # results = json.loads(json.dumps(allRes))
                results = result
                # flow_sort = flowSort

            )
        return JsonResponse(result)

        # 通过stepid获取日志检索条件，传入时间和关键字，返回结果，并存储

def lokiStepQuery(request):
    if request.method == 'POST':
        reqdata = json.loads(request.body)
        flow_id = reqdata['flowId']
        # mission_id = reqdata['missionId']
        
        match_key = reqdata['matchKey']
        # missionObj = LogFlowMission.objects.filter(mission_id=mission_id).first()
        # 获取数据源的url
        dataSourceId = reqdata['dataSourceId']
        dataSourceObj = Datasource.objects.filter(id=dataSourceId).first()
        reqUrl = dataSourceObj.url
        dataValue = reqdata["dateValue"]
        username = reqdata["username"]
        flowLogObj = LogFlow.objects.filter(id=flow_id).first()
        userObj = UserInfo.objects.filter(username=username).first()
        # 通过flowid获取stepid
        # flowLogObj = LogFlow.objects.filter(id=flow_id).first()
                # 记录入库
        LogFlowMissionObj,created = LogFlowMission.objects.get_or_create(
                # mission_id = mission_id,
                search_key = match_key,
                # task_id = ,
                flow_id = flowLogObj,
                user_id = userObj,
                dataSource_id = dataSourceObj,
                status = 0,
                mission_query = reqdata,
                results = {}
                # flow_sort = flowSort

            )
        # print(LogFlowMissionObj.mission_id)
        task = lokiAnalysis.delay(params={
                                "reqUrl": reqUrl,
                                "match_key": match_key,
                                "flow_id": flow_id,
                                "dataValue": dataValue,
                                "limit": 500,
                                "missionId": LogFlowMissionObj.mission_id
                               })

        LogFlowMissionObj.task_id = task.id
        LogFlowMissionObj.save()
        return JsonResponse({"missionId": LogFlowMissionObj.mission_id,"task_id":task.id,"result":"任务提交成功！"})

        # 通过stepid获取日志检索条件，传入时间和关键字，返回结果，并存储

def get_lokiAnalysis_status(request, task_id):
    result = AsyncResult(task_id)
    def event_stream():
        is_finish = False
        while not is_finish:
            time.sleep(1)
            if result.ready():
                if result.successful():
                    # 更新状态
                    # result.missionObj.status = 
                    is_finish = True
                    res = {"is_finish": True}
                    yield f"data: {json.dumps(res)}\n\n"

                    # return JsonResponse({'status': 'SUCCESS', 'result': result.result.detail})
                else:
                    is_finish = True
                    res = {"is_finish": True}
                    yield f"data: {json.dumps(res)}\n\n"

                    # return JsonResponse({'status': 'FAILURE', 'result': str(result.info)})
            else:
                # return JsonResponse({'status': 'PENDING'})
                is_finish = False
                res = {"is_finish": False}

                yield f"data: {json.dumps(res)}\n\n"
    return StreamingHttpResponse(event_stream(), content_type="text/event-stream")
