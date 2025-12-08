<template>
  <div class="login-container">
    <div class="login-wrapper">
      <div class="login-box">
        <div class="login-left">
          <div class="welcome-text">
            <h1>欢迎登录</h1>
            <p>高效、便捷的自动化运维系统</p>
          </div>
          <div class="decoration-elements">
            <div class="circle circle-1"></div>
            <div class="circle circle-2"></div>
            <div class="circle circle-3"></div>
          </div>
        </div>
        <div class="login-right">
          <el-card class="login-card" shadow="never">
            <div class="card-header">
              <h2>用户登录</h2>
              <p>请输入您的账户信息</p>
            </div>
            <el-form
              :model="formLogin"
              class="login-form"
              ref="ruleFormRef"
              :rules="rules"
              label-position="top"
              @keyup.enter.native="handleCommit"
            >
              <el-form-item prop="username">
                <el-input
                  v-model="formLogin.username"
                  placeholder="请输入用户名"
                  size="large"
                  clearable
                >
                  <template #prefix>
                    <el-icon class="el-input__icon"><User /></el-icon>
                  </template>
                </el-input>
              </el-form-item>

              <el-form-item prop="password">
                <el-input
                  v-model="formLogin.password"
                  type="password"
                  placeholder="请输入密码"
                  size="large"
                  show-password
                >
                  <template #prefix>
                    <el-icon class="el-input__icon"><Lock /></el-icon>
                  </template>
                </el-input>
              </el-form-item>

              <el-form-item>
                <el-button
                  type="primary"
                  @click="handleCommit"
                  :loading="isLoggingIn"
                  size="large"
                  class="login-button"
                  style="width: 100%"
                >
                  {{ isLoggingIn ? "登录中..." : "登录" }}
                </el-button>
              </el-form-item>
            </el-form>

            <div class="login-footer" v-if="loginFailMess">
              <el-alert
                :title="loginFailMess"
                type="error"
                show-icon
                :closable="false"
              />
            </div>
          </el-card>
        </div>
      </div>
    </div>

    <div class="particles-container">
      <div class="particle" v-for="i in 20" :key="i"></div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { reactive, ref, getCurrentInstance } from "vue";
import type { FormInstance, FormRules } from "element-plus";
import { useRouter } from "vue-router";
import { ElNotification } from "element-plus";
import { User, Lock } from "@element-plus/icons-vue";
const { proxy } = getCurrentInstance();

import useConfigStore from "@/store/config";
const configStore = useConfigStore();
const router = useRouter();

// 表单校验
const ruleFormRef = ref<FormInstance>();
const rules = reactive<FormRules>({
  password: [{ required: true, message: "请输入密码", trigger: "blur" }],
  username: [{ required: true, message: "请输入账号", trigger: "blur" }],
});

const loginFailMess = ref("");
const isLoggingIn = ref(false);

const formLogin = reactive({
  username: "",
  password: "",
});

const handleCommit = () => {
  loginFailMess.value = "";
  ruleFormRef.value?.validate(async (valid) => {
    if (valid) {
      isLoggingIn.value = true;
      try {
        let res = await proxy.$api.login(formLogin);
        if (res.data.code != 200) {
          loginFailMess.value = res.data.error;
          // 添加震动效果
          document.querySelector(".login-card")?.classList.add("shake");
          setTimeout(() => {
            document.querySelector(".login-card")?.classList.remove("shake");
          }, 500);
        } else {
          await configStore.setUserConfig(res.data);

          // 获取动态菜单路由
          await configStore.getMenuInfo();

          // 获取国密密钥
          let gmRes = await proxy.$api.getSysConfig({ params: "gm" });
          configStore.setGmCry(gmRes.data);

          // 登录成功通知
          ElNotification({
            title: "登录成功",
            message: "欢迎回来，" + formLogin.username,
            type: "success",
            duration: 2000,
          });

          // 跳转到首页
          router.push({ name: "main" });
        }
      } catch (error) {
        console.error("登录失败:", error);
        loginFailMess.value = "登录失败，请检查网络连接";
        // 添加震动效果
        document.querySelector(".login-card")?.classList.add("shake");
        setTimeout(() => {
          document.querySelector(".login-card")?.classList.remove("shake");
        }, 500);
      } finally {
        isLoggingIn.value = false;
      }
    }
  });
};
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(
    135deg,
    var(--el-color-primary-light-3) 0%,
    var(--el-color-primary) 100%
  );
  position: relative;
  overflow: hidden;
}

.login-wrapper {
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  z-index: 2;
}

.login-box {
  display: flex;
  background: var(--el-bg-color);
  border-radius: var(--el-border-radius-base);
  overflow: hidden;
  box-shadow: var(--el-box-shadow);
  backdrop-filter: blur(10px);
  animation: fadeInUp 0.8s ease-out;
}

.login-left {
  flex: 1;
  background: linear-gradient(
    135deg,
    var(--el-color-primary-light-3) 0%,
    var(--el-color-primary) 100%
  );
  color: var(--el-text-color-primary);
  padding: 60px 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.welcome-text h1 {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 15px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  color: white;
}

.welcome-text p {
  font-size: 1.1rem;
  opacity: 0.9;
  margin-bottom: 30px;
  color: white;
}

.decoration-elements {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
}

.circle-1 {
  width: 150px;
  height: 150px;
  top: 20%;
  right: 10%;
  animation: float 6s ease-in-out infinite;
}

.circle-2 {
  width: 100px;
  height: 100px;
  bottom: 30%;
  right: 20%;
  animation: float 8s ease-in-out infinite;
  animation-delay: 1s;
}

.circle-3 {
  width: 80px;
  height: 80px;
  top: 40%;
  left: 10%;
  animation: float 7s ease-in-out infinite;
  animation-delay: 2s;
}

.login-right {
  flex: 1;
  padding: 40px;
  display: flex;
  align-items: center;
}

.login-card {
  width: 100%;
  border: none;
  background: transparent;
}

.card-header {
  text-align: center;
  margin-bottom: 30px;
}

.card-header h2 {
  font-size: 1.8rem;
  color: var(--el-text-color-primary);
  margin-bottom: 10px;
}

.card-header p {
  color: var(--el-text-color-secondary);
  font-size: 0.95rem;
}

.login-form {
  margin-top: 20px;
}

.login-button {
  background: linear-gradient(
    135deg,
    var(--el-color-primary-light-3) 0%,
    var(--el-color-primary) 100%
  );
  border: none;
  font-weight: 600;
  letter-spacing: 1px;
  transition: all 0.3s ease;
  color: white;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: var(--el-box-shadow-light);
}

.login-footer {
  margin-top: 20px;
}

.shake {
  animation: shake 0.5s;
}

/* 粒子背景 */
.particles-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.particle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  animation: particle-float linear infinite;
}

.particle:nth-child(1) {
  width: 5px;
  height: 5px;
  top: 10%;
  left: 20%;
  animation-duration: 15s;
}
.particle:nth-child(2) {
  width: 8px;
  height: 8px;
  top: 20%;
  left: 80%;
  animation-duration: 20s;
}
.particle:nth-child(3) {
  width: 6px;
  height: 6px;
  top: 70%;
  left: 30%;
  animation-duration: 18s;
}
.particle:nth-child(4) {
  width: 4px;
  height: 4px;
  top: 40%;
  left: 50%;
  animation-duration: 25s;
}
.particle:nth-child(5) {
  width: 7px;
  height: 7px;
  top: 60%;
  left: 90%;
  animation-duration: 22s;
}
.particle:nth-child(6) {
  width: 5px;
  height: 5px;
  top: 30%;
  left: 10%;
  animation-duration: 17s;
}
.particle:nth-child(7) {
  width: 9px;
  height: 9px;
  top: 80%;
  left: 60%;
  animation-duration: 24s;
}
.particle:nth-child(8) {
  width: 6px;
  height: 6px;
  top: 50%;
  left: 40%;
  animation-duration: 19s;
}
.particle:nth-child(9) {
  width: 4px;
  height: 4px;
  top: 15%;
  left: 70%;
  animation-duration: 21s;
}
.particle:nth-child(10) {
  width: 7px;
  height: 7px;
  top: 85%;
  left: 25%;
  animation-duration: 23s;
}
.particle:nth-child(11) {
  width: 5px;
  height: 5px;
  top: 25%;
  left: 45%;
  animation-duration: 16s;
}
.particle:nth-child(12) {
  width: 8px;
  height: 8px;
  top: 75%;
  left: 75%;
  animation-duration: 26s;
}
.particle:nth-child(13) {
  width: 6px;
  height: 6px;
  top: 35%;
  left: 15%;
  animation-duration: 20s;
}
.particle:nth-child(14) {
  width: 4px;
  height: 4px;
  top: 65%;
  left: 85%;
  animation-duration: 18s;
}
.particle:nth-child(15) {
  width: 7px;
  height: 7px;
  top: 55%;
  left: 35%;
  animation-duration: 22s;
}
.particle:nth-child(16) {
  width: 5px;
  height: 5px;
  top: 45%;
  left: 65%;
  animation-duration: 19s;
}
.particle:nth-child(17) {
  width: 9px;
  height: 9px;
  top: 5%;
  left: 95%;
  animation-duration: 25s;
}
.particle:nth-child(18) {
  width: 6px;
  height: 6px;
  top: 90%;
  left: 5%;
  animation-duration: 21s;
}
.particle:nth-child(19) {
  width: 4px;
  height: 4px;
  top: 50%;
  left: 95%;
  animation-duration: 23s;
}
.particle:nth-child(20) {
  width: 7px;
  height: 7px;
  top: 95%;
  left: 50%;
  animation-duration: 27s;
}

/* 动画 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(10deg);
  }
  100% {
    transform: translateY(0) rotate(0deg);
  }
}

@keyframes shake {
  0%,
  100% {
    transform: translateX(0);
  }
  20%,
  60% {
    transform: translateX(-5px);
  }
  40%,
  80% {
    transform: translateX(5px);
  }
}

@keyframes particle-float {
  0% {
    transform: translateY(0) translateX(0) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100vh) translateX(100px) rotate(360deg);
    opacity: 0;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-box {
    flex-direction: column;
  }

  .login-left {
    padding: 30px 20px;
  }

  .login-right {
    padding: 30px 20px;
  }

  .welcome-text h1 {
    font-size: 2rem;
  }

  .card-header h2 {
    font-size: 1.5rem;
  }
}
</style>