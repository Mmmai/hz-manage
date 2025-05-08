<template>
  <div class="home-context">
    <!-- <div class="home-context-header">
      <div class="home-context-header-left">
        <el-link href="/#/portal" :underline="false" @click="test1">
          <el-button
            type="success"
          >
            配置
          </el-button>
        </el-link>
      </div>
      <div class="home-context-header-right">
        <span style="color: var(--el-text-color-regular); display: inline-block;line-height: 30px;padding: 0px 10px;">分组 </span>
        <el-select 
        v-model="test" 
        filterable  
        clearable 
        placeholder="分组"
      >
        <el-option
          v-for="item in options"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
        </el-select>
        <span style="color: var(--el-text-color-regular); display: inline-block;line-height: 30px;padding: 0px 10px;"> 筛选 </span>
        <el-input v-model="filterObject.search" placeholder="过滤" clearable style="width: 30%;" />
      </div>
    </div> -->
    <!-- <div        
      class="div-contain"
      v-for="v,i in divlist"
      :key="i"
    >
        <el-avatar 
        class="sub-avt" 
        size="large" 
        shape="square" 

        > 
        {{ v }}
        </el-avatar>
      <span>{{ v }}</span>
      
    </div> -->
    <!-- <div  class="div-contain">    
      <span>添加</span>
    </div> -->
    <div class="home-context-body">
      <!-- <div class="div-contain"  v-for="v,i in divlist"
      :key="i"
      >     -->
    <el-link  
      v-for="v,i in divlist"
      :key="i" href="/#/user" :underline="false">
      <el-card shadow="hover">
        <el-row>
          <el-avatar 
          class="sub-avt" 
          size="large" 
          shape="square" 
          > 
        <!-- :style="extractColorByName(v)" -->
          {{ v }}
          </el-avatar>
        </el-row>
        <el-row type="flex" align="middle" justify="center">
          <span style="text-align: center;">{{ v }}</span>
          <!-- <el-link href="/#/user" target="_blank">{{ v }}</el-link> -->
        </el-row>
      </el-card>
    </el-link>
      <!-- </div> -->
      <!-- 新增按钮 -->
      <!-- <el-link href="/#/user" target="_blank" :underline="false">
      <el-card shadow="hover"> 
        <el-row>
          <el-icon size="54px" color="#DCDCDC" class="add-icon"><Plus /></el-icon> 
        </el-row>

      </el-card>
    </el-link> -->
    </div>
    <!-- <el-icon size="30px" color="#DCDCDC" class="add-icon"><Plus /></el-icon>  -->



  </div>

</template>
<script setup>
import {ref} from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import {useRouter} from 'vue-router'

import Avatar from 'vue-avatar'
const router = useRouter();

const divlist = ref([
  "ZABBIX","Grafana","测试123"
])
const handleClick = () =>{

}
// 颜色生成
const extractColorByName = (name) => {
    var temp = [];
    temp.push("#");
    for (let index = 0; index < name.length; index++) {
      temp.push(parseInt(name[index].charCodeAt(0), 10).toString(16));
    }
    let colorCcode =  temp.slice(0, 5).join('').slice(0, 4);
    return {background:colorCcode}
  }
// 分组选项
const options = ref([
  {
    value: 'Option1',
    label: 'Option1',
  },
  {
    value: 'Option2',
    label: 'Option2',
  },
  {
    value: 'Option3',
    label: 'Option3',
  },
  {
    value: 'Option4',
    label: 'Option4',
  },
  {
    value: 'Option5',
    label: 'Option5',
  },
  ])
const test1 = () => {
  
}
// 过滤
const filterObject = ref({
  search:null
})

</script>
<style scoped>
.home-context{
  height: 100%;
  width: 100%;
  display: flex;
  flex-wrap: wrap;


}
.home-context-header {
  height: 30px;
  width: 100%;
  display: flex;
  border-bottom: 1px solid #DCDCDC  ;
  padding: 10px;
  justify-content: space-between;

}
.home-context-header-right .home-context-header-left{
  display: flex;
  width: 600px;

  justify-content: space-between;

}
.home-context-body{
    height: 90%;
    width: 100%;
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-start;
    align-content: flex-start;
    align-items: flex-start;
}
.div-contain {
  display: flex;
  height: 100px;
  width: 100px;
  flex-direction: column;
  justify-content: center;
  align-items: center;

}
.sub-avt {
  /* height: 50px;
  width: 50px; */
  
  border: 1px solid #DCDCDC  ;
  margin: 20px;
  margin-bottom: 5px;
  background: var(--el-color-primary);
  color: var(--el-color-white)
}
.add-icon {
  border: 1px solid #DCDCDC  ;
  margin: 20px;
  margin-bottom: 5px;
}
.el-card {
  margin: 10px;
}
</style>