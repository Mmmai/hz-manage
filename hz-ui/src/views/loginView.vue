<template>
  <div class="login-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>欢迎登录</span>
          <!-- <el-button class="button" text>Operation button</el-button> -->
        </div>
      </template>
      <el-form
        :model="formLogin"
        style="max-width: 460px"
        ref="ruleFormRef"
        :rules="rules"
        label-position="right"
        label-width="80px"
        @keyup.enter.native="handleCommit"
      >
        <el-form-item label="用户名" prop="username" :error="usernameError">
          <el-input v-model="formLogin.username" />
        </el-form-item>
        <el-form-item label="密码" prop="password" :error="passwordError">
          <el-input type="password" v-model="formLogin.password" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleCommit" style="width: 100%"
            >登录</el-button
          >
        </el-form-item>
      </el-form>
      <span style="color: red">{{ loginFailMess }}</span>
    </el-card>
  </div>
</template>
<script lang="ts" setup>
import { reactive, ref, getCurrentInstance, onMounted } from "vue";
// import { login } from '@/api';
import type { FormInstance, FormRules } from "element-plus";
import { useRouter, useRoute } from "vue-router";
const { proxy } = getCurrentInstance();
import { useStore } from "vuex";
const store = useStore();
import useConfigStore from "@/store/config";

const configStore = useConfigStore();
const router = useRouter();
const route = useRoute();

// 表单校验
const ruleFormRef = ref<FormInstance>();
const usernameError = ref("");
const passwordError = ref("");
const rules = reactive<FormRules>({
  password: [{ required: true, message: "请输入密码", trigger: "blur" }],
  username: [{ required: true, message: "请输入账号", trigger: "blur" }],
});
const loginFailMess = ref("");
const token = ref("");
const formLogin = reactive({
  username: "",
  password: "",
});

const handleCommit = () => {
  proxy.$refs.ruleFormRef.validate(async (valid) => {
    if (valid) {
      let res = await proxy.$api.login(formLogin);
      console.log(res);
      if (res.data.code != 200) {
        loginFailMess.value = res.data.error;
      }
      // 登录成功,将token存储到vuex
      else {
        // setTimeout(() => {
        //   console.log(store.state.routerInfo)

        //   console.log(route)
        // }, 350)
        // 储存username
        store.commit("updateCurrentUsername", formLogin.username);
        // localStorage.setItem('username', formLogin.username);
        // 存储token信息
        // localStorage.setItem('token',res.data.token)
        store.commit("addToken", res.data);
        // 初始化顶部tag和面包屑
        router.push({ name: "main" });
        // 获取国密密钥
        let gmRes = await proxy.$api.getSysConfig({ params: "gm" });

        configStore.setGmCry(gmRes.data);
        configStore.getAppVersion();
        // 获取版本
      }
    }
  });
};
</script>
<style scoped>
.login-container {
  height: 100vh;
  background: url("../assets/background.jpg") center center fixed no-repeat;
  background-size: cover;
}
.card-header {
  display: flex;
  justify-content: center;
  align-items: center;
}

.text {
  font-size: 14px;
}

.item {
  margin-bottom: 18px;
}

.box-card {
  position: fixed;
  top: 20%;
  right: 15%;
  width: 25%;
}

.el-form-item__content {
  justify-content: center;
}
</style>
