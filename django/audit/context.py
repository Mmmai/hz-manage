import contextvars

_ctx = {
    "operator_id": contextvars.ContextVar("operator_id", default=None),
    "operator_name": contextvars.ContextVar("operator_name", default=None),
    "channel": contextvars.ContextVar("channel", default="api"),
    "request_id": contextvars.ContextVar("request_id", default=None),
    "correlation_id": contextvars.ContextVar("correlation_id", default=None),
    "source_ip": contextvars.ContextVar("source_ip", default=None),
}


def set_ctx(**kwargs):
    for k, v in kwargs.items():
        if k in _ctx:
            _ctx[k].set(v)


def clear():
    for k in _ctx:
        _ctx[k].set(None)


def operator_id():
    return _ctx["operator_id"].get()


def operator_name():
    return _ctx["operator_name"].get()


def channel():
    return _ctx["channel"].get()


def request_id():
    return _ctx["request_id"].get()


def correlation_id():
    return _ctx["correlation_id"].get()


def source_ip():
    return _ctx["source_ip"].get()


def get_audit_context():
    """
    获取所有审计上下文变量并返回一个字典。
    """
    return {
        "operator": _ctx["operator_name"].get(),
        "operator_ip": _ctx["source_ip"].get(),
        "request_id": _ctx["request_id"].get(),
        "correlation_id": _ctx["correlation_id"].get(),
        "channel": _ctx["channel"].get(),
    }
