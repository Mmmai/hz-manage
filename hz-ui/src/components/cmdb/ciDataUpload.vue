<template>
  <el-dialog v-model="uploadDia" title="导入" width="800">
    <el-upload
      class="upload-demo"
      drag
      action="https://run.mocky.io/v3/9d059bf9-4660-45f2-925d-ce80ad6c4d15"
      multiple
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">拖拽文件到此或者 <em>点击上传文件</em></div>
      <template #tip>
        <el-row justify="space-between" align="middle">
          <el-col :span="18">
            <div>jpg/png files with a size less than 500kb</div>
          </el-col>
          <el-col :span="4">
            <el-button link type="primary" @click="downloadTemplate()"
              >点击下载模板</el-button
            >
          </el-col>
        </el-row>
      </template>
    </el-upload>
  </el-dialog>
</template>
<script lang="ts" setup>
import {
  ref,
  reactive,
  watch,
  getCurrentInstance,
  nextTick,
  onActivated,
  computed,
  onMounted,
} from "vue";
const { proxy } = getCurrentInstance();
const props = defineProps(["ciModelId"]);
// 导入导出
const uploadDia = defineModel("isShowUpload");
const downloadTemplate = async () => {
  let res = await proxy.$api.downloadImportTemplate({ model: props.ciModelId });
  // let res = await proxy.$commFunc.downloadFile({ model: props.ciModelId });
  console.log(res);
};
</script>