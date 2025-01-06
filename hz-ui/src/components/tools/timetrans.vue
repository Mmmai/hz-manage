<template>
  <div class="container">
    <div class="title">
      <el-row :gutter="20">
        <el-tag type="primary">时间戳转换工具</el-tag>
      </el-row>
    </div>
    <div class="parsetype">
      <el-select
        v-model="value"
        placeholder="Select"
        style="width: 240px"
      >
        <el-option
          v-for="item in options"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
    </div>
    <div class="input">
      <el-input
        v-model="input_time"
        style="width: 240px"
        :formatter="(value) => `${value}`.replace(/[^\d.\-/ :]/g, '')"
        :parser="(value) => value.replace(/[^\d.\-/ :]/g, '')"
      />
      <el-button type="primary" plain tag="b" @click="parse" >转换</el-button>

    </div>
    <div class="output">
      <el-text tag="mark">{{ output_time }}</el-text>
    </div>
  </div>
</template>
  
<script setup>
import { ref } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'


const input_time = ref('')
const value = ref('type1')
const output_time=ref('')



let options = [
  {
    value: 'type1',
    label: '时间戳转日期时间',
  },
  {
    value: 'type2',
    label: '日期时间转时间戳',
  },
]


// 判断时间小于10前面加0
const addZero = (str) => {
  return str < 10 ? '0' + str : str
}

// const timestamp = 1626832597790;
const parse = () => {
  if (value.value=='type1') {
    let timestamp = input_time.value

    if (timestamp.length==10){
      timestamp = timestamp*1000
    } else if (timestamp.length==13){
      timestamp = timestamp
    } else {
      ElMessage.error(timestamp + "  输入时间戳长度有误！")
      return false;
    }
    const date = new Date(parseInt(timestamp));
 
    // 获取日期信息
    const year = addZero(date.getFullYear());
    const month = addZero(date.getMonth() + 1); // 月份是从0开始的
    const day = addZero(date.getDate());
    const hours = addZero(date.getHours());
    const minutes = addZero(date.getMinutes());
    const seconds = addZero(date.getSeconds());
    const Milliseconds = addZero(date.getMilliseconds());

    // 格式化日期
    output_time.value = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}.${Milliseconds}`;

  }else if(value.value=='type2'){
    // 日期转换为时间戳
    output_time.value = +new Date(input_time.value)
  }
 

}



// 在组件模板中使用过滤器


</script>

<style>
.container{
    display: flex;
    flex-direction: column;
}

.title {
  flex: 1;
  margin-top:5px;
}

.parsetype {
  flex: 2;
  /* margin-left: auto; */
  margin-top:5px;
}
.input {
  margin-top:5px;
  flex: 3;
}
.output {
  margin-top:5px;
  flex: 3;
}
.comments {
  width: 100%; /* 自动适应父布局宽度 */
  overflow: auto;
  word-break: break-all; /* 解决 IE 中断行问题 */
}

.el-row {
  margin-bottom: 20px;
}
.el-row:last-child {
  margin-bottom: 0;
}
.el-col {
  border-radius: 4px;
}

.grid-content {
  border-radius: 4px;
  min-height: 36px;
}
</style>