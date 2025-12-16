from django.http import HttpResponse,JsonResponse
from rest_framework import filters, status
from rest_framework.views import APIView
from node_mg.utils.zabbix import ZabbixAPI
import re,time
from datetime import datetime,timedelta
from .utils.process_data_tools import process_zabbix_history_data,align_series_in_backend
# Create your views here.


class ZabbixData(APIView):
    authentication_classes = []
    def post(self, request, *args, **kwargs):
        hostIp = request.data.get('ip',None)
        keys = request.data.get('keys',None)
        chart_type = request.data.get('chart_type','line')
        decimal = request.data.get('decimal',4)
        zapi = ZabbixAPI()
        allItems = zapi.get_item_by_host(hostIp)
        # 根据keys 过滤，使用re过滤
        # 根据reItems 获取历史数据
        # 获取当前和一小时前的时间戳
        start_time = int(time.time()) - 3600
        end_time = int(time.time())
        if chart_type == 'line':
            raw_data = {}
            reItems = [i for i in allItems if re.search(keys,i['key_'])]
            _legend = [i['name'] for i in reItems]
            for item in reItems:
                res = zapi.get_history(itemid=item["itemid"],history=item["value_type"],start_time=start_time,end_time=end_time)
            # item['history'] = res
                raw_data[item['name']] = res
            # 时间轴对齐处理
            aligned_result = align_series_in_backend(raw_data, start_time, end_time, 60)
            aligned_result['legend'] = {'data':_legend}
        elif chart_type == 'gauge':
            aligned_result = {}
            item = [i for i in allItems if re.search(f'^{keys}$',i['key_'])][0]
            res = zapi.get_history(itemid=item["itemid"],history=item["value_type"],start_time=start_time,end_time=end_time)
            aligned_result[item['name']] = process_zabbix_history_data(history_data=res,decimal_places=decimal)
            # item['history'] = res

        return JsonResponse(aligned_result)
    def get(self, request):
        """
        获取Zabbix模板列表
        """
        try:
            # 创建ZabbixAPI实例
            zapi = ZabbixAPI()
            result = zapi.get_all_templates()
            if result:
                # 检查结果并返回
                templates = [{"label": i["host"], "value":i["templateid"]} for i in result]
                templates = [{"label": i["host"], "value":i["host"]} for i in result]

                return JsonResponse({
                    'code': 200,
                    'data': templates,
                    'message': 'success'
                }, status=status.HTTP_200_OK)
            else:
                return JsonResponse({
                    'code': 500,
                    'message': 'Failed to get templates from Zabbix',
                    'data': result.get('error', {})
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return JsonResponse({
                'code': 500,
                'message': f'Error occurred: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


