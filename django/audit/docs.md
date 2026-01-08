# 应用模型审计

## 导入审计注册装饰器
- 参考样例
```python
from audit.decorators import register_audit

# 注册关联定义审计
@register_audit(
    # 在Relations模型中，本模型作为外键进行审计快照时，将以下字段生成为字典快照保存
    snapshot_fields={'id', 'name', 'source_model', 'target_model', 'topology_type'},
    # 不审计这些字段
    ignore_fields={'update_time', 'create_time', 'create_user', 'update_user'},
    # 指定ManyToMany字段审计
    m2m_fields={'source_model', 'target_model'},
    # 审计内部使用及API调用时的模型对外名称
    public_name='relation_definition',
    # 对source_model和target_model特殊处理时调用的函数
    field_resolvers={
        'source_model': resolve_model,
        'target_model': resolve_model
    }
)
class RelationDefinition(models.Model):
    pass
```

## 添加字段特殊解析器（如有需要）
- 在注册时如果使用了`field_resolvers`需要同步添加处理器
- 参考样例
```python
# cmdb/resolvers.py

def resolve_model(value):
    """
    一个“值解析器”，专门用于处理指向Models的ManyToManyField。
    它接收一个 ManyRelatedManager 对象并返回一个包含所有关联模型信息的 JSON 字符串。
    """
    models = value.all()
    if not models:
        return []
    # logger.debug(f'Resolved models: {models}')

    return [
        {
            'id': str(model.id),
            'name': model.name,
            'verbose_name': model.verbose_name
        }
        for model in models
    ]
```

## 添加回退及加锁函数（如有需要）
- 具体参照cmdb/restorer.py和cmdb/locker.py，在不需要回退时无需处理