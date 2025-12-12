from datetime import datetime
from typing import List, Dict, Any, Optional, Union
import statistics

def process_zabbix_history_data(
    history_data: List[Dict[str, str]], 
    value_type: str = 'float',
    time_format: str = 'unix_timestamp'
) -> Dict[str, Union[float, int, None]]:
    """
    处理 Zabbix API 历史数据并提取统计信息
    
    Args:
        history_data: Zabbix API 返回的历史数据列表
                    格式: [{'clock': '1717020000', 'value': '23.5'}, ...]
        value_type: 数值类型 ('float', 'int', 'str')
        time_format: 时间格式 ('unix_timestamp', 'iso_string')
    
    Returns:
        包含统计数据的字典
    """
    if not history_data:
        return {
            'max_value': None,
            'min_value': None,
            'avg_value': None,
            'latest_value': None,
            'earliest_value': None,
            'latest_time': None,
            'earliest_time': None,
            'count': 0,
            'std_dev': None,
            'median': None
        }
    
    # 转换数据类型并排序
    processed_data = []
    for item in history_data:
        try:
            # 处理时间戳
            if time_format == 'unix_timestamp':
                timestamp = int(item['clock'])
                time_obj = datetime.fromtimestamp(timestamp)
            elif time_format == 'iso_string':
                time_obj = datetime.fromisoformat(item['clock'].replace('Z', '+00:00'))
            else:
                raise ValueError(f"Unsupported time format: {time_format}")
            
            # 处理数值
            if value_type == 'float':
                value = float(item['value'])
            elif value_type == 'int':
                value = int(float(item['value']))  # 先转float再转int，处理字符串数字
            elif value_type == 'str':
                value = str(item['value'])
            else:
                raise ValueError(f"Unsupported value type: {value_type}")
            
            processed_data.append({
                'timestamp': timestamp,
                'value': value,
                'datetime': time_obj
            })
        except (ValueError, KeyError) as e:
            print(f"Warning: Skipping invalid data item {item}: {e}")
            continue
    
    if not processed_data:
        return {
            'max_value': None,
            'min_value': None,
            'avg_value': None,
            'latest_value': None,
            'earliest_value': None,
            'latest_time': None,
            'earliest_time': None,
            'count': 0,
            'std_dev': None,
            'median': None
        }
    
    # 按时间排序
    processed_data.sort(key=lambda x: x['timestamp'])
    
    # 提取数值列表（只对数值类型计算统计信息）
    numeric_values = [item['value'] for item in processed_data if isinstance(item['value'], (int, float))]
    
    # 计算统计信息
    stats = {
        'max_value': max(numeric_values) if numeric_values else None,
        'min_value': min(numeric_values) if numeric_values else None,
        'avg_value': sum(numeric_values) / len(numeric_values) if numeric_values else None,
        'latest_value': processed_data[-1]['value'],
        'earliest_value': processed_data[0]['value'],
        'latest_time': processed_data[-1]['datetime'].isoformat(),
        'earliest_time': processed_data[0]['datetime'].isoformat(),
        'count': len(processed_data),
        'std_dev': statistics.stdev(numeric_values) if len(numeric_values) > 1 else None,
        'median': statistics.median(numeric_values) if numeric_values else None
    }
    
    # 添加更多统计信息
    if numeric_values:
        stats.update({
            'sum_value': sum(numeric_values),
            'range': (stats['max_value'] - stats['min_value']) if stats['max_value'] is not None and stats['min_value'] is not None else None,
            'first_quartile': calculate_percentile(numeric_values, 25) if len(numeric_values) >= 4 else None,
            'third_quartile': calculate_percentile(numeric_values, 75) if len(numeric_values) >= 4 else None,
            'percentile_95': calculate_percentile(numeric_values, 95) if len(numeric_values) >= 20 else None,
            'percentile_99': calculate_percentile(numeric_values, 99) if len(numeric_values) >= 100 else None
        })
    
    return stats

def calculate_percentile(data: List[float], percentile: float) -> Optional[float]:
    """
    计算百分位数
    """
    if not data or len(data) == 0:
        return None
    
    sorted_data = sorted(data)
    index = (percentile / 100) * (len(sorted_data) - 1)
    
    if index.is_integer():
        return sorted_data[int(index)]
    else:
        lower_index = int(index)
        upper_index = lower_index + 1
        weight = index - lower_index
        
        if upper_index >= len(sorted_data):
            return sorted_data[lower_index]
        
        return sorted_data[lower_index] * (1 - weight) + sorted_data[upper_index] * weight

def extract_specific_stats(
    history_data: List[Dict[str, str]], 
    stat_types: List[str] = None
) -> Dict[str, Any]:
    """
    提取指定的统计类型
    
    Args:
        history_data: Zabbix 历史数据
        stat_types: 需要提取的统计类型列表
                   如 ['max_value', 'min_value', 'avg_value', 'latest_value']
    
    Returns:
        指定统计类型的字典
    """
    all_stats = process_zabbix_history_data(history_data)
    
    if stat_types is None:
        return all_stats
    
    return {key: all_stats.get(key) for key in stat_types if key in all_stats}

def get_time_based_stats(
    history_data: List[Dict[str, str]],
    time_window_minutes: int = 60
) -> Dict[str, Any]:
    """
    获取指定时间窗口内的统计信息
    
    Args:
        history_data: Zabbix 历史数据
        time_window_minutes: 时间窗口（分钟），默认60分钟
    
    Returns:
        时间窗口内的统计数据
    """
    if not history_data:
        return process_zabbix_history_data([])
    
    # 获取最新的时间点
    latest_timestamp = max(int(item['clock']) for item in history_data)
    time_threshold = latest_timestamp - (time_window_minutes * 60)
    
    # 过滤时间窗口内的数据
    filtered_data = [
        item for item in history_data 
        if int(item['clock']) >= time_threshold
    ]
    
    return process_zabbix_history_data(filtered_data)

# 使用示例
if __name__ == "__main__":
    # 模拟 Zabbix API 返回的历史数据
    sample_data = [
        {'clock': '1717020000', 'value': '23.5'},
        {'clock': '1717020600', 'value': '25.1'},
        {'clock': '1717021200', 'value': '22.8'},
        {'clock': '1717021800', 'value': '26.0'},
        {'clock': '1717022400', 'value': '24.2'},
        {'clock': '1717023000', 'value': '27.5'},
        {'clock': '1717023600', 'value': '21.9'},
    ]
    
    # 获取全部统计信息
    all_stats = process_zabbix_history_data(sample_data)
    print("全部统计信息:")
    for key, value in all_stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*50 + "\n")
    
    # 获取特定统计信息
    specific_stats = extract_specific_stats(
        sample_data, 
        ['max_value', 'min_value', 'avg_value', 'latest_value']
    )
    print("特定统计信息:")
    for key, value in specific_stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*50 + "\n")
    
    # 获取最近30分钟的统计信息
    recent_stats = get_time_based_stats(sample_data, time_window_minutes=30)
    print("最近30分钟统计信息:")
    for key, value in recent_stats.items():
        print(f"  {key}: {value}")