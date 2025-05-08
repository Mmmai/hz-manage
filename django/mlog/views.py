from django.shortcuts import render
from django.db import models
from django.forms.models import model_to_dict

import json
from .sers import *
# Create your views here.
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from .models import LogModule,LogFlow,LogFlowModule,LogFlowMission
from .filters import (
    LogFlowMissionFilter
)
from django.http import HttpResponse,JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

# class StandardResultsSetPagination(PageNumberPagination):
#     page_size = settings.REST_FRAMEWORK.get('PAGE_SIZE', 20)
#     page_size_query_param = 'page_size'
#     max_page_size = settings.REST_FRAMEWORK.get('PAGE_MAX_SIZE', 20)
class LogModuleViewSet(ModelViewSet):
    queryset = LogModule.objects.all()
    serializer_class = LogModuleModelSerializer
class LogFlowMissionViewSet(ModelViewSet):
    queryset = LogFlowMission.objects.all()
    # serializer_class = LogFlowMissionModelSerializer
    filterset_class = LogFlowMissionFilter
    ordering_fields = ['create_time',]
    def get_serializer_class(self):
        if self.action == 'list':
            return LogFlowMissionModelSerializer
        else:
            return LogFlowMissionModelSerializerAll
    
class LogFlowViewSet(APIView):
    # queryset = LogFlow.objects.all()
    # # queryset = LogFlow.steps.through.objects.order_by('id').all()
    # serializer_class = LogFlowModelSerializer
    def get_object(self,pk):
        try:
            return LogFlow.objects.get(pk=pk)
        except LogFlow.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
    def get(self, request, *args, **kwargs):
        allRes = []
        for obj in LogFlow.objects.all():
            a = []
            for i in LogFlow.steps.through.objects.filter(flow_id_id=obj.id).order_by('order').all():
                a.append(i.step_id_id)
            # obj.steps.set = a
            bbb = model_to_dict(obj)
            bbb["steps"] = a
            bbb["id"] = obj.id
            allRes.append(bbb)
        return JsonResponse({"data":allRes})
        
    def post(self, request, *args, **kwargs):
        reqdata = json.loads(request.body.decode("utf8"))
        steps = reqdata["steps"]
        del reqdata["steps"]
        del reqdata["stepList"]
        if LogFlow.objects.filter(name=reqdata["name"]).exists():
            return JsonResponse(data={"error":"%s has been exists!!!"%reqdata["name"]},status=205)
        
        logFlow = LogFlow.objects.create(**reqdata)
        for index,item in enumerate(steps):
            LogFlowModule.objects.create(
                flow_id_id = logFlow.id,
                step_id_id = item,
                order = index+1
            )
        return JsonResponse({"code":200,"result":"success"},status=201)
    def patch(self, request, pk):
        logFlow = self.get_object(pk=pk)
        reqData = json.loads(request.body.decode("utf8"))
        # print(reqData)
        # print(json.loads(request.body))
        # 多对多关系的更新
        # 获取新的步骤列表
        newStepList = reqData["steps"]
        allStep = LogFlowModule.objects.filter(flow_id_id=pk).all()
        # 获取旧的步骤列表
        oldStepList = []
        for index,item in enumerate(allStep):
            oldStepList.append(model_to_dict(item)['step_id'])
        # 新的比旧长
        if len(newStepList) >= len(oldStepList):
            if newStepList != oldStepList:
                for index,item in enumerate(newStepList):
                    if index+1 <= len(oldStepList):
                        if item == oldStepList[index]:
                            pass
                        else:
                            # 更新
                            oLogFlowModule = LogFlowModule.objects.filter(flow_id_id=pk,step_id_id=oldStepList[index],order=index+1)
                            oLogFlowModule.update(step_id_id=item)
                    else:
                        #新增
                        LogFlowModule.objects.create(flow_id_id=pk,step_id_id=item,order=index+1)

        else:
            # 新比旧短
            for index,item in enumerate(oldStepList):
                # 处理新列表的内容
                if index+1 <= len(newStepList):
                    if item == newStepList[index]:
                        pass
                    else:
                        oLogFlowModule = LogFlowModule.objects.filter(flow_id_id=pk,step_id_id=item,order=index+1)
                        oLogFlowModule.update(step_id_id=newStepList[index])                   
                # 处理旧列表的内容
                else:
                    oLogFlowModule = LogFlowModule.objects.filter(flow_id_id=pk,step_id_id=item,order=index+1)
                    oLogFlowModule.delete()
        # 其他更新
        logFlow = LogFlow.objects.filter(id=reqData["id"])
        del reqData["steps"]
        del reqData["stepList"]
        logFlow.update(**reqData)

        return JsonResponse({"code":200,"result":"success"},status=200)    
    def delete(self,request,pk):
        logFlow = self.get_object(pk)
        logFlow.delete()
        return JsonResponse({"code":200,"result":"success"},status=204)



def get_model(name, fields=None, app_label=None, module='', options=None, admin_opts=None):
    """
    Create specified model
    """
    class Meta:
        db_table = name
    if app_label:
        setattr(Meta, 'app_label', app_label)
        models.loading.register_models(app_label, model)

    if options is not None:
        for key, value in options.items():
            setattr(Meta, key, value)
    attrs = {'__module__': module, 'Meta': Meta}
    if fields:
        attrs.update(fields)
 
    model = type(name, (models.Model,), attrs)
    return model

def test(request):

    if request.method == 'GET':
        # reqUrl = request.GET.get('url')
        flowLogObj = LogFlow.objects.filter(id=51).first()
        print(flowLogObj.id)
        print(LogFlow.steps.through.objects.filter(flow_id_id=51).order_by('order').all())
        for i in LogFlow.steps.through.objects.filter(flow_id_id=51).order_by('order').all():
            print(model_to_dict(LogModule.objects.filter(id=i.step_id_id).first()))
            # def getlog(i.label_name,i.label_match,i.lalbel_value,i.)
        return HttpResponse(111)
        # for obj in LogFlow.steps.through.objects.order_by('id').all():
        #     print(obj.steps.all())
        # print(LogFlow.objects.all())
        # allRes = []
        # for obj in LogFlow.objects.all():
        #     a = []
        #     for i in LogFlow.steps.through.objects.filter(flow_id_id=obj.id).order_by('order').all():
        #         a.append(i.step_id_id)
        #     # obj.steps.set = a
        #     bbb = model_to_dict(obj)
        #     bbb["steps"] = a
        #     allRes.append(bbb)
        # return JsonResponse({"data":allRes})
    elif request.method == 'POST':
        reqdata = json.loads(request.body)
        # steps = reqdata["steps"]
        # del reqdata["steps"]
        # logFlow = LogFlow.objects.create(**reqdata)
        # print(logFlow)
        # for index,item in enumerate(steps):
        #     LogFlowModule.objects.create(
        #         flow_id_id = logFlow.id,
        #         step_id_id = item,
        #         order = index+1
        #     )
        # return HttpResponse('1111')
        al = dict(
            title=models.CharField(choices=[('MR', 'Mr.'), ('MRS', 'Mrs.'), ('MS', 'Ms.')], max_length=3),
            birth_date=models.DateField(blank=True, null=True)
            )
        model_a = get_model('test_app', app_label='mlog', fields=al)
        return HttpResponse(111222)