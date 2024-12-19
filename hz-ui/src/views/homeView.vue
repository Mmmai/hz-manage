<template>

  <div class="card">
    <el-scrollbar>

      <el-row justify="space-between">
        <el-col :span="18" class="group-class">
          <span style="display: flex;align-items: center;margin-right: 10px;">分组</span>

          <el-segmented v-model="group" :options="GroupOptions" size="large" />
        </el-col>
        <el-col :span="4">
          <!-- <span>过滤</span>  -->
          <el-input v-model="filterPortal" style="width: 200px" placeholder="过滤器" clearable />
        </el-col>
        <!-- <el-col :span="1">  <el-link type="primary" :href="'/#'+getPortalUrl">编辑</el-link></el-col> -->
        <el-col :span="1"> <el-link type="primary" @click="isEdit == true">编辑</el-link></el-col>
        <el-col :span="1"> <el-link type="primary" :href="'/#' + getPortalUrl">添加</el-link></el-col>

      </el-row>


      <el-divider />

      <el-space wrap :size="30" v-draggable="[portalList, { animation: 150, onUpdate }]">
        <el-card v-for="fItem, fIndex in showDataList" :key="fItem.id" class="box-card"
          style="width: 300px;height: 120px;" shadow="hover" @click="cardClick(fItem)">
          <el-tooltip class="box-item" effect="light" :content="fItem.url" placement="bottom">
            <el-space direction="vertical" alignment="end">
              <el-row>
                <el-col :span="8">
                  <el-avatar :style="{ 'background-color': getRandomColor(fItem.id + fItem.name), 'font-size': '28px' }"
                    :size="60">
                    {{ fItem.name.slice(0, 1).toUpperCase() }}
                  </el-avatar>
                </el-col>

                <el-col :span="12">

                  <el-space direction="vertical">
                    <span style="font-size: 20px;font-weight: bold;width: 200px;">{{ fItem.name }}</span>
                    <el-tooltip class="box-item" effect="light" :content="fItem.describe" placement="bottom"
                      v-if="fItem.describe === '' ? false : true">
                      <el-text class="describe-class" type="info">{{ fItem.describe }}</el-text>
                      <!-- <span class="describe-class">[{{ fItem.describe }}]</span>        -->
                    </el-tooltip>
                  </el-space>
                </el-col>

              </el-row>
              <!-- <el-row justify="end" >
        <el-col :span="12">{{ fItem.group_name}}</el-col>
      </el-row> -->
              <!-- <span>{{ fItem.group_name}}</span> -->
              <!-- <el-text type="info" @click.stop=setGroupFilter(fItem.group_name)>{{ fItem.group_name}}</el-text> -->
              <el-link type="info" @click.stop=setGroupFilter(fItem.group_name)>{{ fItem.group_name }}</el-link>

            </el-space>
          </el-tooltip>
        </el-card>
      </el-space>
    </el-scrollbar>

  </div>

  <!-- <el-button @click="getPortal">1111</el-button> -->
</template>
<script setup>
import { ref, getCurrentInstance, onMounted, watch, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { vDraggable } from 'vue-draggable-plus'

import { Search } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { el } from 'element-plus/es/locale/index.mjs';
const { proxy } = getCurrentInstance();
// import { useRoute,useRouter } from 'vue-router'
// const route = useRoute()
const router = useRouter()
const getPortalUrl = computed(() => {
  return router.resolve({ name: 'portal' }).path
  // return 111
})
const GroupOptions = ref(['所有'])
const pgroupData = ref([])
const group = ref('所有')
const getPgroup = async () => {
  let res = await proxy.$api.pgroupGet()
  console.log(res)
  pgroupData.value = res.data.results
  GroupOptions.value = ['所有']
  res.data.results.forEach(item => {
    GroupOptions.value.push(item.group)
  });
}
const portalList = ref([])
// const showDataList = ref([])

// 获取门户列表
const getPortal = async () => {
  let res = await proxy.$api.portalGet()
  console.log(res)
  portalList.value = res.data.results
  // showDataList.value = res.data
}

// 根据字符串生成颜色
const getRandomColor = (str) => {
  // var red = Math.floor(Math.random() * 32 * str.length);
  // var green = Math.floor(Math.random() * 32 * str.length);
  // var blue = Math.floor(Math.random() * 32 * str.length);
  // // console.log('rgb(' + red + ', ' + green + ', ' + blue + ')')
  // return 'rgb(' + red + ', ' + green + ', ' + blue + ')';
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  let color = "#";
  for (let i = 0; i < 3; i++) {
    let value = (hash >> (i * 8)) & 0xFF;
    color += ("00" + value.toString(16)).slice(-2);
  }
  return color;
  // let hash = 0;
  // for (let i = 0; i < str.length; i++) {
  //   hash = str.charCodeAt(i) + ((hash << 5) - hash);
  //   hash = hash & hash; // 转换为32位整数
  // }

  // // 将数字转换为一个范围在0-360的色相值
  // let hue = hash % 360;

  // // 饱和度和亮度设置为相对较低的值以减少眼睛的亮度
  // const saturation = 40 + ((hash * 0.4) % 60);
  // const lightness = 30 + ((hash * 0.7) % 40);

  // // 生成HSL颜色字符串
  // return `hsl(${hue}, ${saturation}%, ${lightness}%)`;

}
// 点击卡片跳转
const cardClick = (param) => {
  // window.location.href=param.url
  // 新页面打开
  window.open(param.url, '_blank')
}
// 监听分段选择器，显示卡片
// watch(()=> group.value,(n)=>{
//   console.log(n)
//   if (n === '所有'){
//     showDataList.value = portalList.value
//   }else{
//     showDataList.value = portalList.value.filter((item)=>{
//       console.log(item)
//    return item.group_name === n
//   })
//   }
// })
const filterPortal = ref('')
// watch(()=> filterPortal.value,(n)=>{
//   if (n!=null){
//     return
//   }else{
//     // showDataList.value = 
//     return
//   }
// })
// 分组和标签过滤
const showDataList = computed(() => {
  return portalList.value.filter(item => {
    let items = true
    if (group.value === '所有') {
      items = true
      if (filterPortal.value === '') {
        items = true
      } else {
        items = item.name.toLowerCase().includes(filterPortal.value.toLowerCase())
      }
    } else {
      items = item.group_name.includes(group.value)
      if (items) {
        if (filterPortal.value === '') {
          items = true
        } else {
          items = item.name.toLowerCase().includes(filterPortal.value.toLowerCase())
        }
      }
    }
    return items
  })
})
const setGroupFilter = (param) => {
  group.value = param
}
onMounted(() => {
  getPortal();
  getPgroup();
  // console.log(router.resolve({name:'portal'}));
})
const onUpdate = () => {
  console.log(portalList.value)

}
</script>
<style scoped lang="less">
.describe-class {
  white-space: nowrap;
  /*强制单行显示*/
  text-overflow: ellipsis;
  /*文本超出部分省略号表示*/
  overflow: hidden;
  /*文本超出部分隐藏*/
  max-width: 200px;
  /*设置文本显示的最大宽度*/
  display: inline-block
    /*设为行内块元素*/
  ;
  vertical-align: top;
  width: 200px;
}

.el-col-12 {
  display: flex;
  align-items: center;
}

.group-class {
  display: flex;
  justify-content: flex-start;
}

// .el-breadcrumb__item {
//   font-size: 20px;
// }
.el-link {
  --el-link-font-size: calc(var(--el-font-size-base) + 2px)
}

.el-container {
  flex-basis: 100%;
}
</style>