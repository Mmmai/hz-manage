<template>
  <el-dialog v-model="uploadDia" title="导入" width="800">
    <el-upload
      class="upload-demo"
      drag
      action
      ref="refUpload"
      :headers="headers"
      :http-request="uploadFile"
      :file-list="fileList"
      :before-upload="beforeUpload"
      :limit="maxFiles"
      @on-change="handleChange"
      show-file-list
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">拖拽文件到此或者 <em>点击上传文件</em></div>
      <template #tip>
        <el-row justify="space-between" align="middle">
          <el-col :span="18">
            <div>只支持从此系统下载的模板导入，请按右侧按钮下载模板!</div>
          </el-col>
          <el-col :span="3">
            <!-- <el-button link type="primary" @click="rmFileList()"
              >清除文件列表</el-button
            > -->
            <el-button link type="primary" @click="downloadTemplate()"
              >点击下载模板</el-button
            >
          </el-col>
        </el-row>
      </template>
      <template #file="{ file, index }">
        <div class="flexJstart gap-1">
          <span>{{ file.name }} </span>
          <!-- <span>{{ JSON.stringify(file) }}</span> -->
          <div
            v-if="uploadResStatusList[file.uid] == true"
            class="flexJstart gap-1"
          >
            <el-icon
              v-if="uploadRes[file.uid]?.status !== 'completed'"
              class="is-loading"
              ><Loading
            /></el-icon>
            <el-icon v-else-if="uploadRes[file.uid]?.failed >>> 0"
              ><Warning color="var(--el-color-warning)"
            /></el-icon>
            <el-icon v-else="uploadRes[file.uid]?.failed == 0"
              ><CircleCheck color="var(--el-color-success)"
            /></el-icon>
            <div v-if="uploadRes[file.uid]" class="flexJstart gap-1">
              <span>{{ `进度: ${uploadRes[file.uid]?.progress}%` }}</span>
              <span>{{
                `结果: 总条数: ${uploadRes[file.uid]?.total},创建: ${
                  uploadRes[file.uid]?.created
                },更新: ${uploadRes[file.uid]?.updated},跳过: ${
                  uploadRes[file.uid]?.skipped
                },失败: ${uploadRes[file.uid]?.failed}.`
              }}</span>
              <el-link
                type="danger"
                v-if="uploadRes[file.uid]?.failed >>> 0"
                @click="
                  downloadImportErrorRecord(uploadRes[file.uid]?.error_file_key)
                "
                >查看导入失败数据</el-link
              >
            </div>
          </div>
          <el-icon v-else-if="uploadResStatusList[file.uid] == false"
            ><CircleClose color="var(--el-color-error)"
          /></el-icon>
        </div>
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
const props = defineProps(["ciModelId", "currentNodeId"]);
const emit = defineEmits(["getCiData"]);
import axios from "axios";
import { ElMessage } from "element-plus";
import { CircleClose, Warning } from "@element-plus/icons-vue";
// 导入导出
const uploadDia = defineModel("isShowUpload");
// 导入
const fileList = ref([]);
const refUpload = ref(null);
const fileType = ["xlsx"];
const maxFiles = ref(10);
const uploadRes = ref({});
// const refUpload = ref(null)
const uploadMission = ref({});
const headers = reactive({
  "Content-Type": "multipart/form-data",
});
const uploadResStatusList = ref({});
// 定义定时获取导入结果的函数
const getUploadRes = async () => {
  if (Object.keys(uploadMission.value).length > 0) {
    Object.entries(uploadMission.value).forEach(async ([k, v]) => {
      // 发起请求
      let res = await proxy.$api.importCiDataStatus(v);
      // console.log(res)
      uploadRes.value[k] = res.data;
      if (res.data.status === "completed") {
        delete uploadMission.value[k];
      }
    });
  } else {
    clearInterval(timer);
    timer = null;
    // 更新表格
    emit("getCiData", {
      model: props.ciModelId,
      model_instance_group: props.currentNodeId,
    });
  }
};
let timer = null;
const uploadFile = async (item) => {
  let formDatas = new FormData();
  formDatas.append("file", item.file);
  formDatas.append("model", props.ciModelId);
  //上传文件
  let res = await proxy.$api.importCiData(formDatas, headers, 2 * 60 * 1000);
  if (res.status == 200) {
    uploadMission.value[item.file.uid] = res.data;
    uploadResStatusList.value[item.file.uid] = true;
    if (timer === null) {
      timer = setInterval(getUploadRes, 2000);
    }
  } else {
    uploadResStatusList.value[item.file.uid] = false;
    ElMessage({
      message: `导入异常: ${JSON.stringify(res.data)}`,
      type: "error",
      showClose: true,
    });
  }
};
const handleChange = () => {};
// 超出限制时执行的方法
// const handleExceed = (files) => {
//   // console.log(files);
//   refUpload.value!.clearFiles();
//   // const file = files[0] as UploadRawFile;
//   // file.uid = genFileId();
//   refUpload.value!.handleStart(files);
// };

const beforeUpload = (file) => {
  let fileName = file.name;
  if (file.type != "" || file.type != null || file.type != undefined) {
    //截取文件的后缀，判断文件类型
    const fileExt = file.name.replace(/.+\./, "").toLowerCase();
    //计算文件的大小
    const isLt5M = file.size / 1024 / 1024 < 5; //这里做文件大小限制
    //如果大于50M
    if (!isLt5M) {
      ElMessage.error("上传文件大小不能超过 5MB!");
      return false;
    }
    //如果文件类型不在允许上传的范围内
    if (fileType.includes(fileExt)) {
      let found = fileList.value.find(
        (item) =>
          item.name == fileName && item.lastModified == file.lastModified
      );
      if (found) {
        ElMessage({
          type: "error",
          message: "该文件已上传！",
          showClose: true,
        });
        return false;
      }
      // console.log(fileList.value.length);

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

// 导出导入失败的数据
const downloadImportErrorRecord = async (params) => {
  let res = await proxy.$api.downloadErrorRecords({ error_file_key: params });
};
// 导出
const downloadTemplate = async () => {
  let res = await proxy.$api.downloadImportTemplate({ model: props.ciModelId });
  // let res = await proxy.$commFunc.downloadFile({ model: props.ciModelId });
};
</script>