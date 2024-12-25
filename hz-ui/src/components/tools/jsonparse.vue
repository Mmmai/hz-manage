<template>

  <div class="container">
    <el-tag type="primary">JSON格式化工具</el-tag>
    <div class="input">
      <el-input
        v-model="jsonStr"
        style="width: 100%"
        :rows="10"
        type="textarea"
        placeholder="输入要转换的JSON文本"
      />
    </div>
    <div class="button">
      <el-row :gutter="20">
        <el-col :span="2" >
          <el-button type="warning" plain tag="b" @click="change" >格式化JSON</el-button>
        </el-col>
        <el-col :span="1" :offset="1">
          <el-button type="warning" plain tag="b" @click="jsonStr = '',jsonData = ''">清空</el-button>
        </el-col>
      </el-row>
    </div>

    <div class="standard">
      <json-viewer
      :value="jsonData"
      :expand-depth=5
      copyable
      boxed
      sort></json-viewer>
      </div>
    </div>
</template>
  
<script setup>
  import { JsonViewer } from "vue3-json-viewer"
  import "vue3-json-viewer/dist/index.css";
  import { ref } from "vue";
  import { ElMessageBox, ElMessage } from 'element-plus'
  // import { ElMessage } from 'element-plus'
  const jsonStr = ref('')
  // let jsonStr = ''
  const jsonData = ref('')
  const jsonErr = ref('')

  const change = async () => {
    if (typeof jsonStr.value == 'string') {
        try {
            var obj=JSON.parse(jsonStr.value);

            if(typeof obj == 'object' && obj ){
                jsonData.value  = obj;
                return true;
            }else{
                jsonErr.value  = 'error：'+jsonStr.value+ " can't be translated"
            }

        } catch(e) {
            jsonErr.value  = 'error：'+jsonStr.value +'!!!'+e
        }
    }else{
          jsonErr.value = 'It is not a string!'
    }


    if (jsonErr.value != '') {
      ElMessage.error(jsonErr.value)
      return false;
    }

  };
</script>

<style>
.container{
    display: flex;
    flex-direction: column;
}

.input {
  flex: 1;
  margin-top:5px;
}

.button {
  flex: 2;
  /* margin-left: auto; */
  margin-top:5px;
}
.standard {
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