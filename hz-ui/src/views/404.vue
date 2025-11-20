<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <div class="error-code">404</div>
      <div class="error-title">页面未找到</div>
      <div class="error-description">抱歉，您访问的页面不存在或已被删除</div>
      <div class="error-actions">
        <el-button type="primary" @click="goHome">返回首页</el-button>
        <el-button @click="goBack">返回上一页</el-button>
      </div>
    </div>
    <div class="not-found-graphic">
      <svg viewBox="0 0 24 24" width="200" height="200">
        <path
          fill="var(--el-color-primary)"
          d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4M12,6A6,6 0 0,0 6,12A6,6 0 0,0 12,18A6,6 0 0,0 18,12A6,6 0 0,0 12,6M12,8A4,4 0 0,1 16,12A4,4 0 0,1 12,16A4,4 0 0,1 8,12A4,4 0 0,1 12,8Z"
        />
      </svg>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { ElButton } from "element-plus";

const router = useRouter();

const goHome = () => {
  router.push("/");
};

const goBack = () => {
  router.go(-1);
};
</script>

<style scoped>
.not-found-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 20px;
  background-color: var(--color-background);
}

.not-found-content {
  text-align: center;
  max-width: 500px;
  margin-right: 40px;
}

.error-code {
  font-size: 96px;
  font-weight: bold;
  color: var(--el-color-primary);
  line-height: 1;
  margin-bottom: 20px;
}

.error-title {
  font-size: 32px;
  font-weight: bold;
  color: var(--color-heading);
  margin-bottom: 15px;
}

.error-description {
  font-size: 18px;
  color: var(--color-text);
  margin-bottom: 30px;
  line-height: 1.5;
}

.error-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
}

.not-found-graphic {
  display: none;
}

@media (min-width: 768px) {
  .not-found-graphic {
    display: block;
  }
}

@media (min-width: 1024px) {
  .not-found-container {
    padding: 0;
  }

  .not-found-content {
    margin-right: 60px;
  }
}
</style>