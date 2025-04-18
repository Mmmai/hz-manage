<template>
  <div class="card">
    <el-tabs v-model="activeName" class="demo-tabs">
      <el-tab-pane label="SSE测试" name="sseTest">
        <el-button @click="openSse">开始</el-button>
        <el-button type="danger" @click="closeSse">终止</el-button>

        {{ result }}
      </el-tab-pane>
      <el-tab-pane label="celery测试" name="celery">
        <el-button @click="startTask">提交任务</el-button>
        <el-button type="primary" @click="checkTask(taskId)"
          >查看任务状态</el-button
        >
        {{ `任务ID是：${taskId}` }}
        <div>{{ taskRes }}</div>
      </el-tab-pane>
      <el-tab-pane label="WebSocket测试" name="weSocketTest">
        <el-input v-model="command" style="width: 240px"></el-input>
        <el-button @click="openWs">执行</el-button>
        <el-button type="danger" @click="closeWs">终止</el-button>
        <div v-for="(item, index) in outputLines" :key="index">
          <!-- <el-text v-for="(item, index) in outputLines" :key="index">{{
            item
          }}</el-text> -->
          <!-- <p style="" v-for="(item, index) in outputLines" :key="index">
            {{ item }}
          </p> -->
          <div v-html="item"></div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script lang="ts" setup>
import {
  ref,
  computed,
  watch,
  getCurrentInstance,
  onMounted,
  onUnmounted,
  reactive,
  nextTick,
} from "vue";
const { proxy } = getCurrentInstance();
import { useStore } from "vuex";
const store = useStore();
const result = ref([]);
const activeName = ref("sseTest");

const eventSource = ref(null);
const openSse = () => {
  eventSource.value = new EventSource(
    "/api/v1/log/logFlowMission/get_lokiAnalysis_status/53467f14-557f-4472-8dd8-150fdd8b4684/"
    // "/api/v1/sse"
  );
  eventSource.value.onmessage = (event) => {
    console.log(typeof event.data);
    console.log(event.data.is_finish);

    result.value.push(event.data);
  };
};
const closeSse = () => {
  eventSource.value.close();
};
// const eventSource = new EventSource("sse");
onMounted(() => {
  // eventSource = new EventSource("/api/v1/sse/");
  // eventSource.onmessage = (event) => {
  //   result.value.push(event.data);
  // };
});
import axios from "../utils/request";

const taskId = ref(null);
const startTask = async () => {
  let res = await axios.request({
    url: "/api/v1/test_celery/",
    method: "post",
  });
  taskId.value = res.data.task_id;
  // console.log(res);
};
const taskRes = ref(null);
const checkTask = async (id) => {
  let res = await axios.request({ url: `/api/v1/check_task/${id}/` });
  // console.log(res);
  taskRes.value = res.data;
};
onUnmounted(() => {
  if (eventSource.value) {
    eventSource.value.close();
  }
  if (socket.value) {
    socket.value.close();
  }
});
import { AnsiUp } from "ansi_up";
const ansiUp = new AnsiUp();

// websocket
const command = ref("");
const socket = ref(null);
const outputLines = ref([]);
const openWs = () => {
  outputLines.value = [];
  socket.value = new WebSocket("/ws/ansible/");

  socket.value.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === "output") {
      console.log(ansiUp.ansi_to_html(data.message + "\r\n"));
      outputLines.value.push(ansiUp.ansi_to_html(data.message + "\r\n"));
    } else if (data.type === "complete") {
      console.log(data);

      outputLines.value.push(`执行完成，返回码: ${data.returncode}`);
      socket.value.close();
    }
  };
  socket.value.onopen = () => {
    socket.value.send(
      JSON.stringify({
        module_args: command.value,
        module_name: "shell",
        inventory: ["192.168.163.160", "192.168.163.162"],
        username: "root",
        password: "thinker",
      })
    );
  };
};
const closeWs = () => {
  socket.value.close();
};
</script>
<style scoped lang="scss">
</style>