from django.http import HttpResponse,JsonResponse
from rest_framework import filters, status
from rest_framework.views import APIView
from node_mg.utils.zabbix import ZabbixAPI
import re,time
from datetime import datetime,timedelta
import pandas as pd
from .utils.process_data_tools import process_zabbix_history_data
# Create your views here.


class ZabbixData(APIView):
    authentication_classes = []
    def post(self, request, *args, **kwargs):
        hostIp = request.data.get('ip',None)
        keys = request.data.get('keys',None)
        chart_type = request.data.get('chart_type','line')
        zapi = ZabbixAPI()
        allItems = zapi.get_item_by_host(hostIp)
        # 根据keys 过滤，使用re过滤
        # 根据reItems 获取历史数据
        # 获取当前和一小时前的时间戳
        start_time = int(time.time()) - 3600
        end_time = int(time.time())
        print(chart_type)
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
            aligned_result['legend'] = _legend
        elif chart_type == 'gauge':
            aligned_result = {}
            item = [i for i in allItems if re.search(f'^{keys}$',i['key_'])][0]
            res = zapi.get_history(itemid=item["itemid"],history=item["value_type"],start_time=start_time,end_time=end_time)
            aligned_result[item['name']] = process_zabbix_history_data(res)
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


def align_series_in_backend(data_map, start_ts, end_ts, interval):
    """
    后端对齐算法 - 修正版本
    """
    # ✅ 正确使用 datetime.datetime.fromtimestamp()
    start_dt = datetime.fromtimestamp(start_ts)
    end_dt = datetime.fromtimestamp(end_ts)
    
    # 创建统一时间轴
    time_index = pd.date_range(
        start=start_dt,
        end=end_dt,
        freq=f'{interval}S'
    )
    
    # 转换为 DataFrame 并对齐
    aligned_df = pd.DataFrame(index=time_index)
    
    for item_id, raw_values in data_map.items():
        # ✅ 正确转换时间戳
        timestamps = [datetime.fromtimestamp(int(x['clock'])) for x in raw_values]
        values = [float(x['value']) for x in raw_values]
        
        series = pd.Series(values, index=timestamps)
        # 重采样对齐
        aligned_series = series.reindex(time_index, method='nearest', tolerance=pd.Timedelta(seconds=interval))
        
        aligned_df[item_id] = aligned_series
    
    # 转换为前端所需格式
    result = {
        'time_labels': [ts.strftime('%H:%M') for ts in time_index],
        'series': []
    }
    
    for col in aligned_df.columns:
        result['series'].append({
            'name': col,
            'data': aligned_df[col].tolist()
        })
    
    return result