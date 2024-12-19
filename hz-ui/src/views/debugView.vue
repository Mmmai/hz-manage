<template>
  <div class="card">
    <div v-for="item, index in tmpFormData" :key="index">
      <li>
        <el-input v-model="item.name" style="width: 120px;margin-right: 10px;" />
        <el-input v-model="item.value" style="width: 220px;margin-right: 10px;" />
        <el-button circle type="danger" size="small" :icon="CircleClose" @click="rmField(index)"
          v-if="tmpFormData.length !== 1"></el-button>
        <el-button circle type="primary" size="small" :icon="CirclePlus" @click="addField(index)"></el-button>

      </li>

    </div>

    <el-button @click="submitForm">提交</el-button>
  </div>
</template>
<script setup>
import { CircleClose, CirclePlus, Delete } from '@element-plus/icons-vue';
import { computed, ref, onMounted, watch } from 'vue';
const formData = ref({

});
const tmpFormData = ref([
  { name: '', value: '' }
]);
const arrayJson = computed(() => {
  let tempArr = {}
  tmpFormData.value.forEach(item => {
    if (item.name !== '' && item.value !== '') {
      tempArr[item.name] = item.value
    }
  })
  return tempArr
})
const newKey = ref('');
const newValue = ref('');
const addField = (index) => {
  tmpFormData.value.splice(index + 1, 0, { name: '', value: '' })

};
const rmField = (index) => {
  tmpFormData.value.splice(index, 1)
  console.log(tmpFormData.value)
}
const submitForm = () => {
  console.log(arrayJson.value);
};

</script>