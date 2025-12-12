from cacheops import transaction


class CacheopsUserContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 检查用户是否已认证
        if request.user and request.user.username:
            # 使用 as_condition 将用户名作为所有 cacheops 操作的附加条件
            # 这会改变所有后续查询的缓存键，使其对每个用户都唯一
            with transaction.as_condition(username=request.user.username):
                response = self.get_response(request)
        else:
            # 对于匿名用户，不添加额外条件
            response = self.get_response(request)

        return response
