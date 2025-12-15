# 代码重构
- [x] Models
- [x] ModelGroups
- [x] ModelFieldGroups
- [ ] ModelFields
- [ ] ModelFieldMeta
- [x] ModelFieldPreference
- [x] ModelFieldGroups
- [x] ModelInstance
- [x] ModelInstanceGroup
- [ ] ModelInstanceGroupRelation
- [x] UniqueConstraint 
- [ ] RelationDefinition
- [ ] Relations

# 权限改造
- [x] Models
- [x] ModelGroups
- [x] ModelFieldGroups
- [ ] ModelFields
- [x] ModelFieldMeta
- [x] ModelFieldPreference
- [x] ModelFieldGroups
- [ ] ModelInstance
  - [x] 导出模板
  - [x] 导入实例
  - [x] 导出数据
- [x] ModelInstanceGroup
- [ ] ModelInstanceGroupRelation
- [x] UniqueConstraint 
- [ ] RelationDefinition
- [ ] Relations

# 需求开发
- [x] 添加ModelFieldMeta的全文检索方法
- [ ] 表格导入
- [ ] 导出添加实例组
- [ ] 后端方法校验用户按钮权限
- [ ] 添加实例树json导出导入
- [ ] 导入node_mg发送的自动扫描出来的实例

# 功能优化
- [ ] 取消现有模型的IP必填及唯一校验规则
- [ ] 取消主机名校验规则
- [x] ModelFieldPreference根据不同用户进行设置
- [ ] 用户更新字段权限时，如果删除了字段权限，同步更新ModelFieldPreference
- [ ] 用户被删除时同步清理对应的ModelFieldPreference
- [x] 导出数据时同步使用模板表头方便再次导入
- [x] 实例加载优化，预加载字段配置和值，序列化器通过上下文直接读取解析后的结果
- [x] 实例导入时校验模板所属模型

# 问题修复
- [x] instance_name_template同步unique_constraint逻辑转移到服务层
- [x] UniqueConstraint保存时审计记录异常
- [x] ModelsService在初始化时接收的用户参数异常
