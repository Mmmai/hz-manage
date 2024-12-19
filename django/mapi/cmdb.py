from django.http import HttpResponse,JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response

class ciModelGroup(APIView):
    # def post(self,request,*args,**kwargs):
    #     owner = request.data.get('owner')
    #     orderRes = request.data.get('orderRes')
    #     orderObj = orderMethod.objects.filter(owner=owner).first()
    #     orderObj.update(orderList={"orderList":orderRes})
    #     return Response({'code':200,'results':'success'})
    def post(self,request,*args,**kwargs):
        # owner = request.query_params.get('owner')
        # orderRes =  orderMethod.objects.filter(owner=owner).first()
        modelGroup = [
                        { "id": 1,"obj_id": 'hostmanage', "name": '主机管理',"edit":False },
                        { "id": 2, "obj_id": 'network',"name": '网络设备',"edit":False },
                        { "id": 3, "obj_id": 'other',"name": '其他',"edit":True }
                    ]
        print('add sucess')
        return Response(modelGroup)



    def get(self,request,*args,**kwargs):
        # owner = request.query_params.get('owner')
        # orderRes =  orderMethod.objects.filter(owner=owner).first()
        modelGroup = [
                        { "id": 1,"obj_id": 'hostmanage', "name": '主机管理',"edit":False },
                        { "id": 2, "obj_id": 'network',"name": '网络设备',"edit":False },
                        { "id": 3, "obj_id": 'other',"name": '其他',"edit":True }
                    ]
        return Response(modelGroup)
    def delete(self,request,gid):
        modelGroup = [
                        { "id": 1,"obj_id": 'hostmanage', "name": '主机管理',"edit":False },
                        { "id": 2, "obj_id": 'network',"name": '网络设备',"edit":False },
                        { "id": 3, "obj_id": 'other',"name": '其他',"edit":True }
                    ]
        # print(request.data.get('id'))
        print(gid)
        return Response(modelGroup)
    def put(self,request,gid):
        modelGroup = [
                        { "id": 1,"obj_id": 'hostmanage', "name": '主机管理',"edit":False },
                        { "id": 2, "obj_id": 'network',"name": '网络设备',"edit":False },
                        { "id": 3, "obj_id": 'other',"name": '其他',"edit":True }
                    ]
        print(request.data.get('id'))
        print(gid)
        return Response(modelGroup)
class cimodel(APIView):
    # def post(self,request,*args,**kwargs):
    #     owner = request.data.get('owner')
    #     orderRes = request.data.get('orderRes')
    #     orderObj = orderMethod.objects.filter(owner=owner).first()
    #     orderObj.update(orderList={"orderList":orderRes})
    #     return Response({'code':200,'results':'success'})
    def get(self,request,*args,**kwargs):
        print(args)
        print(kwargs)
        # request.data.get('cid')
        # owner = request.query_params.get('owner')
        print(request.GET)
        # pid = request.GET.get('id')
        # tab = request.GET.get('tab')
            
        # print(pid,tab)
        if 'mid' in kwargs.keys():
            pid = kwargs['mid']
        # orderRes =  orderMethod.objects.filter(owner=owner).first()
            modelDict = {
               1: { "id": 1, "obj_id": "host", "isDelete": False, "group": 1, "name": "主机" ,"icon":"Box" ,"edit":False},

                2:{ "id": 2, "obj_id": "switch", "isDelete": False, "group": 2, "name": "交换机" ,"icon":"Box","edit":False},
                3:{ "id": 3, "obj_id": "security", "isDelete": False, "group": 2, "name": "安全设备","icon":"Box" ,"edit":False},

                4:{ "id": 4, "obj_id": "other", "isDelete": True, "group": 3, "name": "其他" ,"icon":"Menu","edit":False}
            }
            return Response(modelDict[int(pid)])
        else:
            modelList = [
            { "id": 1, "obj_id": "host", "group": 1, "name": "主机" ,"icon":"Box" ,"edit":False,
            "field":[
                   {"name":"业务IP","field_id":'busy_ip',"id":1,"edit":False}
            ],
             },

            { "id": 2, "obj_id": "switch", "isDelete": False, "group": 2, "name": "交换机" ,"icon":"Box","edit":False},
            { "id": 3, "obj_id": "security", "isDelete": False, "group": 2, "name": "安全设备","icon":"Box" ,"edit":False},

            { "id": 4, "obj_id": "other", "isDelete": True, "group": 3, "name": "其他" ,"icon":"Menu","edit":False}
                    ]
            return Response(modelList)

    def post(self,request,*args,**kwargs):
        # owner = request.query_params.get('owner')
        # orderRes =  orderMethod.objects.filter(owner=owner).first()

        print('add sucess')
        modelList = [
            { "id": 1, "obj_id": "host", "isDelete": False, "group": 1, "name": "主机" ,"icon":"Box" ,"edit":False},

            { "id": 2, "obj_id": "switch", "isDelete": False, "group": 2, "name": "交换机" ,"icon":"Box","edit":False},
            { "id": 3, "obj_id": "security", "isDelete": False, "group": 2, "name": "安全设备","icon":"Box" ,"edit":False},

            { "id": 4, "obj_id": "other", "isDelete": True, "group": 3, "name": "其他" ,"icon":"Menu","edit":False}
                    ]
        return Response(modelList)

    def delete(self,request,gid):
        # print(request.data.get('id'))
        print(gid)
        modelList = [
            { "id": 1, "obj_id": "host", "isDelete": False, "group": 1, "name": "主机" ,"icon":"Box" ,"edit":False},

            { "id": 2, "obj_id": "switch", "isDelete": False, "group": 2, "name": "交换机" ,"icon":"Box","edit":False},
            { "id": 3, "obj_id": "security", "isDelete": False, "group": 2, "name": "安全设备","icon":"Box" ,"edit":False},

            { "id": 4, "obj_id": "other", "isDelete": True, "group": 3, "name": "其他" ,"icon":"Menu","edit":False}
                    ]
        return Response(modelList)
    def put(self,request,mid):
        print(request.data.get('id'))
        print(mid)
        modelList = [
            { "id": 1, "obj_id": "host", "isDelete": False, "group": 1, "name": "主机" ,"icon":"Box" ,"edit":False},

            { "id": 2, "obj_id": "switch", "isDelete": False, "group": 2, "name": "交换机" ,"icon":"Box","edit":False},
            { "id": 3, "obj_id": "security", "isDelete": False, "group": 2, "name": "安全设备","icon":"Box" ,"edit":False},

            { "id": 4, "obj_id": "other", "isDelete": True, "group": 3, "name": "其他" ,"icon":"Menu","edit":False}
                    ]
        return Response(modelList)
    
