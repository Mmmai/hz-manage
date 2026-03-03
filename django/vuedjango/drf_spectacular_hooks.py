def remove_params(result, generator, request, public):
    """
    postprocessing hook:
    在 OpenAPI schema 生成后，统一删除不需要的参数(search、ordering)。
    """
    for path_key, path_item in result.get('paths', {}).items():
        for operation_key, operation in path_item.items():
            if 'parameters' in operation:
                operation['parameters'] = [
                    p for p in operation['parameters'] if p.get('name') not in [
                        'search',
                        'ordering',
                        'create_time_before',
                        'create_time_after',
                        'update_time_before',
                        'update_time_after']]

    return result


def preprocessing_filter_spec(endpoints):
    """
    移除路径过滤，展示所有模块的 API 接口
    """
    return endpoints
