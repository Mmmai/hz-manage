<template>
  <el-dialog v-model="uploadDia" title="导入" width="800">
    <el-upload
      class="upload-demo"
      drag
      action
      multiple
      ref="refUpload"
      :headers="headers"
      :http-request="uploadFile"
      :file-list="fileList"
      :before-upload="beforeUpload"
      :limit="20"
      show-file-list
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">拖拽文件到此或者 <em>点击上传文件</em></div>
      <template #tip>
        <el-row justify="space-between" align="middle">
          <el-col :span="18">
            <div>只支持从此系统下载的模板导入，请按右侧按钮下载模板!</div>
          </el-col>
          <el-col :span="4">
            <el-button link type="primary" @click="downloadTemplate()"
              >点击下载模板</el-button
            >
          </el-col>
        </el-row>
      </template>
      <!-- <template #file="{ file, index }">
        <div>{{ file }}</div>
      </template> -->
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
import axios from "axios";
import { ElMessage } from "element-plus";
// 导入导出
const uploadDia = defineModel("isShowUpload");
// 导入
const fileList = ref([]);
const refUpload = ref(null);
const fileType = ["xlsx"];
const headers = reactive({
  "Content-Type": "multipart/form-data",
});
const uploadFile = async (item) => {
  let formDatas = new FormData();
  formDatas.append("file", item.file);
  formDatas.append("model", props.ciModelId);
  //上传文件
  let res = await proxy.$api.importCiData(formDatas, headers);
  console.log(res);
};
const beforeUpload = (file) => {
  let fileName = file.name;
  if (file.type != "" || file.type != null || file.type != undefined) {
    //截取文件的后缀，判断文件类型
    const fileExt = file.name.replace(/.+\./, "").toLowerCase();
    console.log(fileExt);
    //计算文件的大小
    const isLt5M = file.size / 1024 / 1024 < 50; //这里做文件大小限制
    //如果大于50M
    if (!isLt5M) {
      this.$showMessage("上传文件大小不能超过 50MB!");
      return false;
    }
    //如果文件类型不在允许上传的范围内
    if (fileType.includes(fileExt)) {
      let found = fileList.value.find((file) => file.name == fileName);
      if (found) {
        ElMessage({
          type: "error",
          message: "该文件已上传！",
          showClose: true,
        });
        return false;
      }
      return true;
    } else {
      ElMessage({
        message: `不能上传${fileExt}类型的文件`,
        type: "error",
        showClose: true,
      });
      return false;
    }
  }
};

// 导出
const downloadTemplate = async () => {
  let res = await proxy.$api.downloadImportTemplate({ model: props.ciModelId });
  // let res = await proxy.$commFunc.downloadFile({ model: props.ciModelId });
  console.log(res);
};
</script>