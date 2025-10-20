import json
import uuid
import hashlib
from typing import Any, Dict, Tuple
from datetime import date, datetime

IGNORED_FIELDS = {"updated_at"}

class CustomJSONEncoder(json.JSONEncoder):
    """
    自定义JSON编码器，用于处理UUID、datetime等特殊类型。
    """
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        
        # 其他类型使用默认编码器
        return super().default(obj)


def clean_for_json(data: dict) -> dict:
    if not isinstance(data, dict):
        return data
    json_string = json.dumps(data, cls=CustomJSONEncoder)
    return json.loads(json_string)


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'))


def calc_integrity(prev_hash, payload) -> str:
    base = (prev_hash or '') + canonical_json(payload)
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def snapshot_model(instance, include_fields=None, exclude_fields=None) -> dict:
    data = {}
    for f in instance._meta.fields:
        name = f.name
        if exclude_fields and name in exclude_fields:
            continue
        if include_fields and name not in include_fields:
            continue
        val = getattr(instance, name)
        data[name] = val
    return data


def diff_dict(before, after) -> dict:
    if before is None and after is None:
        return {}
    if before is None:
        return {k: {"old": None, "new": v} for k, v in (after or {}).items()}
    if after is None:
        return {k: {"old": v, "new": None} for k, v in (before or {}).items()}
    diff = {}
    keys = set(before) | set(after)
    for k in keys:
        if k in IGNORED_FIELDS:
            continue
        if before.get(k) != after.get(k):
            diff[k] = {"old": before.get(k), "new": after.get(k)}
    return diff


def diff_instance(before_snap, after_snap) -> dict:
    """
    对实例：拆分静态字段与 attrs.*
    """
    if before_snap is None:
        return diff_dict(None, after_snap)
    if after_snap is None:
        return diff_dict(before_snap, None)
    # attrs 单独展开
    before_attrs = (before_snap.get("attrs") or {}) if before_snap else {}
    after_attrs = (after_snap.get("attrs") or {}) if after_snap else {}

    static_before = {k: v for k, v in before_snap.items() if k != "attrs"}
    static_after = {k: v for k, v in after_snap.items() if k != "attrs"}

    static_diff = diff_dict(static_before, static_after)

    attr_diff = {}
    for k in set(before_attrs) | set(after_attrs):
        if before_attrs.get(k) != after_attrs.get(k):
            attr_diff[k] = {"old": before_attrs.get(k), "new": after_attrs.get(k)}

    result = {}
    if static_diff:
        result["__static__"] = static_diff
    if attr_diff:
        result["__attrs__"] = attr_diff
    return result
