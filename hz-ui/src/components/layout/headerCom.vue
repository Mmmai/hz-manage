<template>
  <el-row style="width: 100%" justify="space-between">
    <el-col :span="12" style="display: flex; align-items: center">
      <!-- <div class="l-content"> -->
      <!-- <Menu /> -->
      <el-tooltip
        :content="collapse ? '收起菜单' : '展开菜单'"
        placement="bottom"
        effect="dark"
      >
        <div style="margin-right: 10px; display: flex">
          <el-icon v-if="collapse" @click="changeCollapse">
            <Fold />
          </el-icon>
          <el-icon v-else @click="changeCollapse">
            <Expand />
          </el-icon>
        </div>
      </el-tooltip>

      <!-- 面包屑 -->
      <el-breadcrumb :separator-icon="ArrowRight">
        <!-- 可以跳转 -->
        <!-- <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item 
        :to="currentMenu.path"
        v-if="currentMenu"
      >
        {{ currentMenu.name }}
      </el-breadcrumb-item> -->
        <el-breadcrumb-item v-if="currentMenuLabel === '首页'">
          <el-icon><HomeFilled /></el-icon> <span>首页</span>
        </el-breadcrumb-item>
        <el-breadcrumb-item v-for="(item, index) in currentBreadcrumb">
          <div class="flexJbetween gap-2">
            <el-icon>
              <iconifyOffline :icon="item.icon" />
            </el-icon>
            <span> {{ item.name }}</span>
          </div>
        </el-breadcrumb-item>
      </el-breadcrumb>
      <!-- </div> -->
      <!-- <div>
    1111
  </div> -->
    </el-col>

    <el-col :span="4">
      <div
        style="
          display: flex;
          justify-content: flex-end;
          align-items: center;
          gap: 10px;
        "
      >
        <!-- <el-link type="primary" href="/docs/" target="_blank" >指南</el-link> -->

        <!-- 主题选择器按钮 -->
        <el-tooltip content="自定义主题色" placement="bottom" effect="dark">
          <el-button circle size="small" @click="openThemeDrawer">
            <el-icon :size="16">
              <Brush />
            </el-icon>
          </el-button>
        </el-tooltip>

        <!-- 主题选择抽屉 -->
        <el-drawer
          v-model="themeDrawerVisible"
          title="皮肤选择"
          direction="rtl"
          size="300px"
        >
          <div class="dark-mode-section">
            <div class="dark-mode-toggle">
              <el-text tag="b" size="large">显示模式</el-text>
              <el-switch
                v-model="isDark"
                :active-icon="Moon"
                :inactive-icon="Sunny"
                inline-prompt
                @change="toggleDark"
                style="zoom: 1.2"
              >
                <template #active>暗黑</template>
                <template #inactive>明亮</template>
              </el-switch>
            </div>
          </div>
          <div class="theme-drawer-content">
            <div class="theme-list">
              <el-text tag="b" size="large">主题色</el-text>
              <div
                v-for="(theme, index) in themeColors"
                :key="index"
                class="theme-item-large"
                @click="handleThemeChange(theme.color)"
              >
                <span
                  class="theme-color-block-large"
                  :style="{ backgroundColor: theme.color }"
                ></span>
                <span class="theme-name-large">{{ theme.themeName }}</span>
              </div>
            </div>
            <div class="custom-theme-section">
              <div class="section-title">自定义颜色</div>
              <el-color-picker
                v-model="customThemeColor"
                :predefine="predefineColors"
                show-alpha
                size="default"
                color-format="hex"
              />
              <el-button
                type="primary"
                style="margin-top: 20px; width: 100%"
                @click="confirmCustomTheme"
              >
                应用自定义颜色
              </el-button>
            </div>
          </div>
        </el-drawer>

        <el-dropdown trigger="click">
          <span class="el-dropdown-link">
            <el-icon>
              <UserFilled />
            </el-icon>
            {{ userInfo.username }}
            <el-icon class="el-icon--right">
              <arrow-down />
            </el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="showChangePasswordDialog"
                >修改密码</el-dropdown-item
              >
              <el-dropdown-item @click="handleLogout">退出</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-col>
  </el-row>
  <!-- 修改密码对话框 -->
  <el-dialog
    v-model="changePasswordDialogVisible"
    title="修改密码"
    width="500px"
    @close="resetPasswordForm"
  >
    <el-form
      ref="passwordFormRef"
      :model="passwordForm"
      :rules="passwordRules"
      label-width="100px"
    >
      <el-form-item label="原密码" prop="oldPassword">
        <el-input
          v-model="passwordForm.oldPassword"
          type="password"
          show-password
          placeholder="请输入原密码"
        />
      </el-form-item>
      <el-form-item label="新密码" prop="newPassword">
        <el-input
          v-model="passwordForm.newPassword"
          type="password"
          show-password
          placeholder="请输入新密码"
        />
      </el-form-item>
      <el-form-item label="确认密码" prop="confirmPassword">
        <el-input
          v-model="passwordForm.confirmPassword"
          type="password"
          show-password
          placeholder="请再次输入新密码"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="changePasswordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleChangePassword"
          >确认修改</el-button
        >
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import {
  ref,
  computed,
  watch,
  getCurrentInstance,
  reactive,
  nextTick,
} from "vue";
import { ArrowRight, Brush } from "@element-plus/icons-vue";
import router from "@/router";
import { Sunny, Moon } from "@element-plus/icons-vue";
import useTabsStore from "@/store/tabs";
import useConfigStore from "@/store/config";
import { debounce, throttle } from "lodash";

import { useElementPlusTheme } from "use-element-plus-theme";
import { ElMessage, ElMessageBox } from "element-plus";
const { proxy } = getCurrentInstance();
const layoutThemeColor = useStorage("layout-theme-color", "#409eff"); // 默认主题色
const { changeTheme } = useElementPlusTheme(layoutThemeColor.value); // 初始化主题色
const tabsStore = useTabsStore();
const configStore = useConfigStore();
const collapse = computed(() => {
  return configStore.collapse;
});
const changeCollapse = () => {
  configStore.changeCollapse();
};
const currentMenuLabel = computed(() => {
  return tabsStore.currentTitle;
});
const currentBreadcrumb = computed(() => {
  return tabsStore.currentBreadcrumb;
});
import { useDark, useToggle, useStorage, computedAsync } from "@vueuse/core";
const isDark = useDark();
const toggleDark = useToggle(isDark);

const themeColors = [
  { color: "#409eff", themeName: "默认" },
  { color: "#749bc7", themeName: "道奇蓝" },
  { color: "#722ed1", themeName: "深紫罗兰色" },
  { color: "#eb2f96", themeName: "深粉色" },
  { color: "#f5222d", themeName: "猩红色" },
  { color: "#fa541c", themeName: "橙红色" },
  { color: "#13c2c2", themeName: "绿宝石" },
  { color: "#52c41a", themeName: "酸橙绿" },
];
const predefineColors = ref([
  "#409eff",
  "#749bc7",
  "#722ed1",
  "#eb2f96",
  "#f5222d",
  "#fa541c",
  "#13c2c2",
  "#52c41a",
  "#000000",
  "#ffffff",
]);

const themeDrawerVisible = ref(false);
const customThemeColor = ref(layoutThemeColor.value);

const openThemeDrawer = () => {
  themeDrawerVisible.value = true;
};

const handleThemeChange = (theme) => {
  layoutThemeColor.value = theme;
  changeTheme(theme);
  themeDrawerVisible.value = false; // 选择主题后关闭抽屉
};

const confirmCustomTheme = () => {
  if (customThemeColor.value) {
    layoutThemeColor.value = customThemeColor.value;
    changeTheme(customThemeColor.value);
  }
};
const handleCustomThemeChange = (color) => {
  if (color) {
    layoutThemeColor.value = color;
    changeTheme(color);
  }
};

const userInfo = computed(() => configStore.userInfo);

// console.log(currentMenu)
const handleLogout = (done) => {
  ElMessageBox.confirm("是否退出?")
    .then(() => {
      // tabsStore.setTabs([]);
      tabsStore.setTabs([]);
      configStore.clearConfig();
      // localStorage.clear();
      // 清楚tab打开的菜单列表
      router.push({ name: "login" });
      // window.location.reload()
    })
    .catch((error) => {
      // catch error
      console.error("发生错误: " + error);
    });
};
// 修改密码功能
const changePasswordDialogVisible = ref(false);
const passwordFormRef = ref();
const passwordForm = reactive({
  oldPassword: "",
  newPassword: "",
  confirmPassword: "",
});

const passwordRules = {
  oldPassword: [{ required: true, message: "请输入原密码", trigger: "blur" }],
  newPassword: [
    { required: true, message: "请输入新密码", trigger: "blur" },
    { min: 5, message: "密码长度不能低于5位", trigger: "blur" },
  ],
  confirmPassword: [
    { required: true, message: "请确认新密码", trigger: "blur" },
    {
      validator: (rule, value, callback) => {
        if (value === "") {
          callback(new Error("请再次输入新密码"));
        } else if (value !== passwordForm.newPassword) {
          callback(new Error("两次输入的密码不一致"));
        } else {
          callback();
        }
      },
      trigger: "blur",
    },
  ],
};

const showChangePasswordDialog = () => {
  changePasswordDialogVisible.value = true;
};

const resetPasswordForm = () => {
  if (passwordFormRef.value) {
    passwordFormRef.value.resetFields();
  }
};

const handleChangePassword = throttle(() => {
  if (!passwordFormRef.value) return;

  passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      console.log(userInfo.value);
      try {
        const res = await proxy.$api.userupdate({
          id: userInfo.value.user_id,
          old_password: passwordForm.oldPassword,
          password: passwordForm.newPassword,
        });

        if (res.status === 200) {
          ElMessage.success("密码修改成功，请重新登录");
          changePasswordDialogVisible.value = false;
          resetPasswordForm();

          // 退出登录
          tabsStore.setTabs([]);
          localStorage.clear();
          nextTick(() => {
            router.push({ name: "login" });
          });
        } else {
          ElMessage.error(JSON.stringify(res.data) || "密码修改失败");
        }
      } catch (error) {
        ElMessage.error(error || "密码修改失败");
      }
    }
  });
}, 3000);
</script>
<style scoped>
.l-content {
  display: flex;
  align-items: center;
}

.collapseClass {
  margin-right: 10px;
}

.el-dropdown {
  align-items: center;
}

.theme-drawer-content {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.theme-list {
  flex: 1;
}

.theme-item-large {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 10px;
  transition: background-color 0.3s;
}

.theme-item-large:hover {
  background-color: #f5f7fa;
}

.theme-color-block-large {
  display: inline-block;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  margin-right: 15px;
  border: 1px solid #eee;
}

.theme-name-large {
  font-size: 16px;
}

.custom-theme-section {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}
.dark-mode-section {
  padding-top: 20px;
  border-bottom: 1px solid #eee;
}

.dark-mode-toggle {
  display: flex;
  justify-content: flex-start;
  margin-top: 15px;
  gap: 10px;
}
.section-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #333;
}
</style>
