def compare_interfaces(old, new):
    """比较两个接口列表，找出新增、删除和修改的接口"""
    def to_hashable(d):
        return d['type']  # 仅以 'type' 作为唯一标识

    # 按 'type' 分组，快速定位新增/删除
    old_dict = {to_hashable(d): d for d in old}
    new_dict = {to_hashable(d): d for d in new}

    # 新增和删除的接口
    added = [d for t, d in new_dict.items() if t not in old_dict]
    removed = [d for t, d in old_dict.items() if t not in new_dict]

    # 修改的接口（仅比较 'type' 相同的项）
    modified = []
    common_types = set(old_dict.keys()) & set(new_dict.keys())
    for t in common_types:
        old_d = old_dict[t]
        new_d = new_dict[t]
        # 排除 'type' 自身，比较其他字段是否有差异
        #1
        if old_d != new_d:
            modified.append(new_d)  # 返回完整的 new_dict
    return added, removed, modified