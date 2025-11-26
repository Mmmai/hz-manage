# 代码重构
- [x] Models
- [x] ModelGroups
- [x] ModelFieldGroups
- [ ] ModelFields
- [ ] ModelFieldMeta
- [ ] ModelFieldPreference
- [ ] ModelFieldGroups
- [ ] ModelInstance
- [ ] ModelInstanceGroup
- [x] UniqueConstraint 

# 权限改造
- [x] Models
- [x] ModelGroups
- [x] ModelFieldGroups
- [ ] ModelFields
- [ ] ModelFieldMeta
- [ ] ModelFieldPreference
- [ ] ModelFieldGroups
- [ ] ModelInstance
  - [ ] 导出模板、导入实例、创建实例校验用户权限
- [x] ModelInstanceGroup
- [x] UniqueConstraint 

# 需求开发
- [ ] 添加ModelFieldMeta的全文检索方法

# 功能优化
- [ ] 取消现有模型的IP必填及唯一校验规则
- [ ] 取消主机名校验规则

# 问题修复
- [x] instance_name_template同步unique_constraint逻辑转移到服务层
- [x] UniqueConstraint保存时审计记录异常
- [x] ModelsService在初始化时接收的用户参数异常
- [ ] ModelFieldPreference根据不同用户进行设置
