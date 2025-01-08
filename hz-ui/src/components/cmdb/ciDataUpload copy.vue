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
      :limit="10"
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

          <el-icon v-if="file.status === 'ready'" class="is-loading"
            ><Loading
          /></el-icon>
          <div v-if="file.status === 'success'">
            <div v-if="!uploadRes[file.uid].timeout">
              <div
                v-if="uploadRes[file.uid].status === 'success'"
                class="flexJstart gap-1"
              >
                <el-icon
                  ><Warning
                    color="var(--el-color-warning)"
                    v-if="uploadRes[file.uid].failed >>> 0"
                  />
                  <CircleCheck v-else color="var(--el-color-success)" />
                </el-icon>
                <span>{{
                  `结果: 总条数: ${uploadRes[file.uid].total},创建: ${
                    uploadRes[file.uid].created
                  },更新: ${uploadRes[file.uid].updated},跳过: ${
                    uploadRes[file.uid].skipped
                  },失败: ${uploadRes[file.uid].failed}.耗时(s): ${
                    uploadRes[file.uid].costTime / 1000
                  }`
                }}</span>
                <el-link
                  type="danger"
                  v-if="uploadRes[file.uid].failed >>> 0"
                  @click="
                    downloadImportErrorRecord(
                      uploadRes[file.uid].error_file_key
                    )
                  "
                  >查看导入失败数据</el-link
                >
              </div>
              <div v-else>
                <el-popover
                  placement="top-start"
                  title="错误信息"
                  :width="400"
                  trigger="hover"
                  :content="JSON.stringify(uploadRes[file.uid])"
                >
                  <template #reference>
                    <el-icon color="var(--el-color-error)"
                      ><CircleClose />
                    </el-icon>
                  </template>
                </el-popover>
                <!-- <el-tooltip
                  class="box-item"
                  effect="dark"
                  :content="JSON.stringify(uploadRes[file.uid])"
                  placement="right"
                >
                  <el-icon color="var(--el-color-error)"
                    ><CircleClose />
                  </el-icon>
                </el-tooltip> -->
                <span> 模板文件错误！</span>
              </div>
            </div>
            <div v-else>
              <el-icon color="var(--el-color-error)"><CircleClose /> </el-icon>
              <span>请求超时！</span>
            </div>
          </div>

          <!-- <span>{{ JSON.stringify(uploadRes[file.uid]) }}</span> -->
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
const uploadRes = ref({});
const headers = reactive({
  "Content-Type": "multipart/form-data",
});

const uploadFile = async (item) => {
  let formDatas = new FormData();
  formDatas.append("file", item.file);
  formDatas.append("model", props.ciModelId);
  //上传文件
  let res = await proxy.$api.importCiData(formDatas, headers, 60 * 60 * 1000);
  // let res = await axios({ method: "post", url: "" });
  if (res.timeout) {
    ElMessage({
      message: `请求超时`,
      type: "error",
      showClose: true,
    });
    uploadRes.value[item.file.uid] = { timeout: true };
  } else {
    if (res.status == 200) {
      uploadRes.value[item.file.uid] = {
        timeout: false,
        status: "success",
        ...res.data,
        costTime: res.costTime,
      };
      // 导入成功，刷新数据
      nextTick(() => {
        emit("getCiData", {
          model: props.ciModelId,
          model_instance_group: props.currentNodeId,
        });
      });
    } else {
      uploadRes.value[item.file.uid] = {
        timeout: false,
        status: "failed",
        ...res.data,
        costTime: res.costTime,
      };
    }
  }
  fileList.value.push(item.file);
};
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
      // if (fileList.value.length > 3) {
      //   fileList.value.splice(fileList.value.length - 1, 1);
      //   console.log(fileList.value);
      // }
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
  console.log(res);
};
// 导出
const downloadTemplate = async () => {
  let res = await proxy.$api.downloadImportTemplate({ model: props.ciModelId });
  // let res = await proxy.$commFunc.downloadFile({ model: props.ciModelId });
  console.log(res);
};
</script>