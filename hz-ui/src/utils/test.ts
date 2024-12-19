// 假设初始form
const multiForm = reactive({
    // ...其他属性省略
    updatePrams: {}
  });
  // 定义一个map用来知道每一行对应哪个name
  const paramNameLineMap = {};
  // 由于你要选择name后才知道应该赋值为什么key,所以当添加行时，你可以给个临时key
  // 假设是你的添加参数的方法
  function addParams () {
    // 临时key,最终要被替换的
    const index = Object.keys(multiForm.updateParams).length;
    const tempKey = `__temp_param_${index}`;
    paramNameLineMap[index] = tempKey;
    multiForm.updateParams[tempKey] = '';
  }
  // 假设是你的选择named的方法, 这个时候你需要知道选择的是第几个
  function selectName(index, name) {
    // 这里你需要考虑重新选择name，需不需要清空value值
    // 把name替换进去, 把原来那个删掉
    // 删掉原来的key
  
    // 保留原值
    multiForm.updateParams[name] = multiForm.updateParams[paramNameLineMap[index]];
    // or 清空值
    multiForm.updateParams[name] = '';
  
    // 删除原来的key, 并且更新map
    delete multiForm.updateParams[paramNameLineMap[index]];
    paramNameLineMap[index] = name;
  }
  // 定义一个computed用来渲染form-items
  const formItemKeys = computed(() => Object.keys(multiForm.updateParams));
  // form-item那里
  <FormItem v-for="key in formItemKeys" :key="`param-${key}`" :prop="`updateParams.${key}`">
      // ...内容
      // Input的v-model="multiForm.updatePrams[key]"
  </FormItem>
  // rule也使用computed定义
  const formRule = computed(() => {
    const rule = {};
    // 这里应该使用已选择的name作为验证key
    const needValidKeys = formItemKeys.value.filter(key => !key.startsWith('__temp_param'));
    // 循环遍历needValidKeys, 跟modelInfo.value?.field groups
    modelInfo.value?.field_groups?.forEach(item => {
      item.fields.forEach(field =>{
        if (needValidKeys.includes(field.name)) {
          // 只保留能匹配到的。
          rule[`updateParams.${field.name}`] = [/*.. 你的验证规则 ..*/]
        }
      });
    });
    return rule;
  })
  