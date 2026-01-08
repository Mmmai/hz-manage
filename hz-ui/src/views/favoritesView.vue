<template>
  <div class="card favorites-container">
    <div class="favorites-header">
      <div class="header-left">
        <span class="header-title">门户清单</span>
      </div>
      <div class="header-right">
        <el-input
          v-model="filterPortal"
          style="width: 240px"
          placeholder="搜索门户或分组..."
          clearable
          :prefix-icon="Search"
        />
        <el-dropdown @command="handleAddCommand" style="margin-left: 15px">
          <el-button type="primary">
            添加
            <el-icon class="el-icon--right">
              <arrow-down />
            </el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="portal">添加门户</el-dropdown-item>
              <el-dropdown-item command="group">添加门户组</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <el-divider />

    <!-- 分组卡片视图 -->
    <div class="groups-container">
      <el-space wrap :size="80">
        <div class="group-col">
          <el-card
            class="group-card"
            shadow="hover"
            @click="openFavoritesDia(favoritesData)"
          >
            <div class="group-card-header">
              <div class="group-info">
                <el-avatar size="small" :icon="StarFilled"> </el-avatar>
                <div class="group-text-info">
                  <span class="group-name">收藏夹</span>
                </div>
              </div>
              <div class="group-stats">
                <span class="portal-count"
                  >{{ favoritesData.length }} 个链接</span
                >
              </div>
            </div>
            <div class="portals-grid-preview">
              <div
                v-for="(fPortal, index) in favoritesData.slice(0, 9)"
                :key="fPortal.id"
                class="portal-preview-item"
              >
                <div class="portal-preview-wrapper">
                  <el-tooltip :content="fPortal.url" placement="top">
                    <div
                      class="portal-preview-icon"
                      :style="{
                        backgroundColor: getRandomColor(
                          fPortal.id + fPortal.name
                        ),
                      }"
                      
                    >
                      {{ fPortal.name.charAt(0).toUpperCase() }}
                    </div>
                  </el-tooltip>

                  <el-tag
                    :type="
                      fPortal.sharing_type === 'public' ? 'success' : 'warning'
                    "
                    size="small"
                    class="portal-sharing-tag"
                  >
                    {{ fPortal.sharing_type === "public" ? "公" : "私" }}
                  </el-tag>
                  <el-tooltip
                    :content="fPortal.is_favorite ? '取消收藏' : '收藏'"
                    placement="top"
                  >
                    <el-icon
                      v-if="fPortal.is_favorite"
                      class="portal-favorite-tag"
                      :class="{ favorited: fPortal.is_favorite }"
                      @click.stop="toggleFavorite(fPortal)"
                      color="#e6a23c"
                    >
                      <StarFilled />
                    </el-icon>
                    <el-icon
                      v-else
                      class="portal-favorite-tag"
                      :class="{ favorited: fPortal.is_favorite }"
                      @click.stop="toggleFavorite(fPortal)"
                    >
                      <Star />
                    </el-icon>
                  </el-tooltip>
                </div>
                <el-text>{{ fPortal.name }}</el-text>
              </div>
            </div>
            <div
              v-if="favoritesData.length > 9"
              class="portal-preview-more portal-preview-item"
            >
              +{{ favoritesData.length - 9 }}
            </div>
          </el-card>
        </div>

        <div v-for="group in filteredGroups" :key="group.id" class="group-col">
          <el-card
            class="group-card"
            shadow="hover"
            @click="openGroupDialog(group)"
          >
            <div class="group-card-header">
              <div class="group-info">
                <el-avatar
                  :style="{ backgroundColor: getRandomColor(group.group) }"
                  size="small"
                >
                  {{ group.group.charAt(0).toUpperCase() }}
                </el-avatar>
                <div class="group-text-info">
                  <span class="group-name">{{ group.group }}</span>
                  <el-tag
                    :type="
                      group.sharing_type === 'public' ? 'success' : 'warning'
                    "
                    size="small"
                    class="sharing-type-tag"
                  >
                    {{ group.sharing_type === "public" ? "公共" : "私人" }}
                  </el-tag>
                </div>
              </div>
              <div class="group-stats">
                <span class="portal-count"
                  >{{ group.portals.length }} 个链接</span
                >
              </div>
            </div>

            <!-- 显示该组前9个门户（九宫格） -->
            <div class="portals-grid-preview">
              <div
                v-for="(portal, index) in group.portals.slice(0, 9)"
                :key="portal.id + group.id"
                class="portal-preview-item"
              >
                <div class="portal-preview-wrapper">
                  <el-tooltip :content="portal.url" placement="top">
                    <div
                      class="portal-preview-icon"
                      :style="{
                        backgroundColor: getRandomColor(
                          portal.id + portal.name
                        ),
                      }"
                    >
                      {{ portal.name.charAt(0).toUpperCase() }}
                    </div>
                  </el-tooltip>
                  <el-tag
                    :type="
                      portal.sharing_type === 'public' ? 'success' : 'warning'
                    "
                    size="small"
                    class="portal-sharing-tag"
                  >
                    {{ portal.sharing_type === "public" ? "公" : "私" }}
                  </el-tag>
                  <el-tooltip
                    :content="portal.is_favorite ? '取消收藏' : '收藏'"
                    placement="top"
                  >
                    <el-icon
                      v-if="portal.is_favorite"
                      class="portal-favorite-tag"
                      :class="{ favorited: portal.is_favorite }"
                      @click.stop="toggleFavorite(portal)"
                      color="#e6a23c"
                    >
                      <StarFilled />
                    </el-icon>
                    <el-icon
                      v-else
                      class="portal-favorite-tag"
                      :class="{ favorited: portal.is_favorite }"
                      @click.stop="toggleFavorite(portal)"
                    >
                      <Star />
                    </el-icon>
                  </el-tooltip>
                </div>
                <el-text>{{ portal.name }}</el-text>
              </div>
            </div>
            <!-- 显示更多数量 -->
            <div
              v-if="group.portals.length > 9"
              class="portal-preview-more portal-preview-item"
            >
              +{{ group.portals.length - 9 }}
            </div>
          </el-card>
        </div>
      </el-space>
    </div>
  </div>

  <!-- 分组详情对话框 -->
  <el-dialog
    v-model="groupDialogVisible"
    :title="currentGroup?.group"
    width="800px"
    class="group-detail-dialog"
    :before-close="closeGroupDialog"
  >
    <template #header>
      <div class="dialog-header-edit">
        <div v-if="!groupEditing" class="group-name-display">
          <span class="group-title">{{ currentGroup?.group }}</span>
          <!-- <el-icon class="edit-icon" @click="startGroupEdit">
            <Edit />
          </el-icon> -->
          <el-button
            type="primary"
            link
            :icon="Edit"
            @click="startGroupEdit"
            :disabled="currentUser !== currentGroup?.owner_name"
          ></el-button>
        </div>
        <div v-else class="group-name-edit">
          <el-input
            v-model="groupNameInput"
            style="width: 150px"
            @keyup.enter="saveGroupName"
          />
          <div class="edit-buttons">
            <el-button @click="cancelGroupEdit">取消</el-button>
            <el-button type="primary" @click="saveGroupName"> 保存 </el-button>
          </div>
        </div>
      </div>
    </template>

    <div class="group-detail-header">
      <el-tag
        :type="currentGroup?.sharing_type === 'public' ? 'success' : 'warning'"
        size="small"
      >
        {{ currentGroup?.sharing_type === "public" ? "公共" : "私人" }}
      </el-tag>
      <span class="group-owner" v-if="currentGroup?.owner_name">
        创建者: {{ currentGroup.owner_name }}
      </span>
    </div>

    <div class="dialog-content">
      <!-- 分组内门户列表 -->
      <div
        class="portals-grid"
        v-draggable="[
          currentGroupPortals,
          { animation: 150, onUpdate: handlePortalSort },
        ]"
      >
        <el-card
          v-for="portal in currentGroupPortals"
          :key="portal.id"
          class="portal-card"
          shadow="hover"
          @click="editPortal(portal)"
        >
          <el-tooltip content="点击编辑门户" placement="top" :enterable="false">
            <div class="portal-card-content">
              <div class="portal-icon-wrapper">
                <div
                  class="portal-icon"
                  :style="{
                    backgroundColor: getRandomColor(portal.id + portal.name),
                  }"
                >
                  {{ portal.name.charAt(0).toUpperCase() }}
                </div>
                <el-tag
                  :type="
                    portal.sharing_type === 'public' ? 'success' : 'warning'
                  "
                  size="small"
                  class="portal-sharing-tag-detail"
                >
                  {{ portal.sharing_type === "public" ? "公" : "私" }}
                </el-tag>

                <!-- <el-icon
                class="drag-handle"
                :size="16"
                @click="editPortal(portal)"
              >
                <MoreFilled />
              </el-icon> -->
              </div>

              <div class="portal-info">
                <div class="portal-name">{{ portal.name }}</div>
                <div class="portal-url" :title="portal.url">
                  {{ portal.url }}
                </div>
                <div class="portal-description" v-if="portal.describe">
                  {{ portal.describe }}
                </div>
              </div>

              <div class="portal-actions">
                <el-tooltip
                  :content="portal.is_favorite ? '取消收藏' : '收藏'"
                  placement="top"
                >
                  <el-icon
                    v-if="portal.is_favorite"
                    :class="{ favorited: portal.is_favorite }"
                    @click.stop="toggleFavorite(portal)"
                    color="#e6a23c"
                    size="large"
                  >
                    <StarFilled />
                  </el-icon>
                  <el-icon
                    v-else
                    size="large"
                    :class="{ favorited: portal.is_favorite }"
                    @click.stop="toggleFavorite(portal)"
                  >
                    <Star />
                  </el-icon>
                </el-tooltip>
                <el-button type="primary" link @click="openPortal(portal)">
                  打开
                </el-button>
              </div>
            </div>
          </el-tooltip>
        </el-card>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="closeGroupDialog">关闭</el-button>
        <el-button type="primary" @click="addPortalFormPgroup()">
          添加门户
        </el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 添加/编辑门户对话框 -->
  <el-dialog
    v-model="portalDialogVisible"
    :title="portalAction === 'add' ? '添加门户' : '编辑门户'"
    width="600px"
    :before-close="closePortalDia"
  >
    <el-form
      :model="portalForm"
      :rules="portalRules"
      ref="portalFormRef"
      label-width="100px"
    >
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="名称" prop="name">
            <el-input v-model="portalForm.name" placeholder="请输入门户名称" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="链接地址" prop="url">
            <el-input v-model="portalForm.url" placeholder="请输入链接地址" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="分组" prop="groups">
            <el-select
              v-model="portalForm.groups"
              placeholder="请选择分组"
              style="width: 100%"
              filterable
              multiple
              :disabled="currentGroup !== null && portalAction === 'add'"
            >
              <el-option
                v-for="group in pgroupOptions"
                :key="group.id"
                :label="group.name"
                :value="group.id"
                :disabled="group.disabled"
              >
                <div class="flexJbetween">
                  <span style="float: left">{{ group.name }}</span>
                  <el-tag v-if="group.sharing_type === 'public'" type="success"
                    >公共</el-tag
                  >

                  <el-tag v-else type="danger">私有</el-tag>
                </div>
              </el-option>
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="共享类型" prop="sharing_type">
            <el-select
              v-model="portalForm.sharing_type"
              placeholder="请选择共享类型"
              style="width: 100%"
              :disabled="
                (currentGroup !== null && portalAction === 'add') ||
                portalAction === 'edit'
              "
            >
              <el-option label="公共" value="public" />
              <el-option label="私人" value="private" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="portalForm.username"
              placeholder="请输入用户名"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="密码" prop="password">
            <el-input
              v-model="portalForm.password"
              placeholder="请输入密码"
              show-password
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="排序" prop="sort">
            <el-input-number
              v-model="portalForm.sort"
              controls-position="right"
              :min="0"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="跳转方式" prop="target">
            <el-switch
              v-model="portalForm.target"
              inline-prompt
              style="
                --el-switch-on-color: #13ce66;
                --el-switch-off-color: #ff4949;
              "
              active-text="新窗口"
              inactive-text="当前窗口"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="24">
          <el-form-item label="描述" prop="describe">
            <el-input
              v-model="portalForm.describe"
              placeholder="请输入描述"
              type="textarea"
              :rows="3"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="状态" prop="status">
            <el-switch
              v-model="portalForm.status"
              inline-prompt
              style="
                --el-switch-on-color: #13ce66;
                --el-switch-off-color: #ff4949;
              "
              active-text="启用"
              inactive-text="禁用"
            />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="closePortalDia">取消</el-button>
        <el-button
          type="danger"
          @click="deletePortal(portalForm)"
          v-if="portalAction === 'edit'"
          >删除</el-button
        >
        <el-button
          type="primary"
          @click="submitPortalForm"
          :loading="portalSubmitting"
        >
          确定
        </el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 添加/编辑门户组对话框 -->
  <el-dialog
    v-model="groupDialogFormVisible"
    :title="groupAction === 'add' ? '添加门户组' : '编辑门户组'"
    width="500px"
  >
    <el-form
      :model="groupForm"
      :rules="groupRules"
      ref="groupFormRef"
      label-width="100px"
    >
      <el-form-item label="分组名称" prop="group">
        <el-input v-model="groupForm.group" placeholder="请输入分组名称" />
      </el-form-item>

      <el-form-item label="共享类型" prop="sharing_type">
        <el-select
          v-model="groupForm.sharing_type"
          placeholder="请选择共享类型"
          style="width: 100%"
        >
          <el-option label="公共" value="public" />
          <el-option label="私人" value="private" />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="groupDialogFormVisible = false">取消</el-button>
        <el-button
          type="primary"
          @click="submitGroupForm"
          :loading="groupSubmitting"
        >
          确定
        </el-button>
      </div>
    </template>
  </el-dialog>
  <!-- 收藏夹专用dialog -->
  <!-- 分组详情对话框 -->
  <el-dialog
    v-model="favoritesDialogVisible"
    title="收藏夹"
    width="800px"
    class="group-detail-dialog"
    :before-close="closeFavoritesDia"
  >
    <div class="dialog-content">
      <!-- 分组内门户列表 -->
      <div class="portals-grid">
        <el-card
          v-for="portal in favoritesData"
          :key="portal.id"
          class="portal-card"
          shadow="hover"
        >
          <div class="portal-card-content">
            <div class="portal-icon-wrapper">
              <div
                class="portal-icon"
                :style="{
                  backgroundColor: getRandomColor(portal.id + portal.name),
                }"
              >
                {{ portal.name.charAt(0).toUpperCase() }}
              </div>
              <el-tag
                :type="portal.sharing_type === 'public' ? 'success' : 'warning'"
                size="small"
                class="portal-sharing-tag-detail"
              >
                {{ portal.sharing_type === "public" ? "公" : "私" }}
              </el-tag>

              <!-- <el-icon
                class="drag-handle"
                :size="16"
                @click="editPortal(portal)"
              >
                <MoreFilled />
              </el-icon> -->
            </div>

            <div class="portal-info">
              <div class="portal-name">{{ portal.name }}</div>
              <div class="portal-url" :title="portal.url">
                {{ portal.url }}
              </div>
              <div class="portal-description" v-if="portal.describe">
                {{ portal.describe }}
              </div>
            </div>

            <div class="portal-actions">
              <el-tooltip
                :content="portal.is_favorite ? '取消收藏' : '收藏'"
                placement="top"
              >
                <el-icon
                  v-if="portal.is_favorite"
                  :class="{ favorited: portal.is_favorite }"
                  @click.stop="toggleFavorite(portal)"
                  color="#e6a23c"
                  size="large"
                >
                  <StarFilled />
                </el-icon>
                <el-icon
                  v-else
                  size="large"
                  :class="{ favorited: portal.is_favorite }"
                  @click.stop="toggleFavorite(portal)"
                >
                  <Star />
                </el-icon>
              </el-tooltip>
              <el-button type="primary" link @click="openPortal(portal)">
                打开
              </el-button>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, getCurrentInstance, onMounted, computed, reactive } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { vDraggable } from "vue-draggable-plus";
import {
  Search,
  MoreFilled,
  ArrowDown,
  StarFilled,
  Edit,
} from "@element-plus/icons-vue";
import { useRouter } from "vue-router";
import useConfigStore from "@/store/config";
const configStore = useConfigStore();
defineOptions({ name: "favorites" });
const currentUser = computed(() => configStore.userInfo.username);
const { proxy } = getCurrentInstance();
const router = useRouter();

// 数据状态
const pgroupData = ref([]);
const portalList = ref([]);
const filterPortal = ref("");
const groupDialogVisible = ref(false);
const portalDialogVisible = ref(false);
const groupDialogFormVisible = ref(false);

const currentGroup = ref(null);
const currentGroupPortals = ref([]);
// const currentGroupPortals = computed(() => {
//   return (
//     pgroupData.value.find((item) => item.id == currentGroup.value?.id)
//       ?.portals || []
//   );
// });

const savingOrder = ref(false);
const portalSubmitting = ref(false);
const groupSubmitting = ref(false);

// 表单数据
const portalAction = ref("add");
const groupAction = ref("add");

const portalForm = reactive({
  name: "",
  url: "",
  groups: [],
  sharing_type: "public",
  username: "",
  password: "",
  sort: 9999,
  target: true,
  describe: "",
  status: true,
});
const pgroupOptions = computed(() => {
  return pgroupData.value.map((item) => {
    return {
      name: item.group,
      id: item.id,
      sharing_type: item.sharing_type,
      disabled:
        portalForm.sharing_type === "public" && item.sharing_type === "private"
          ? true
          : false,
    };
  });
});
const favoritesDialogVisible = ref(false);
const openFavoritesDia = () => {
  favoritesDialogVisible.value = true;
};
const closeFavoritesDia = () => {
  favoritesDialogVisible.value = false;
};
const groupForm = reactive({
  group: "",
  sharing_type: "public",
});

// 表单引用
const portalFormRef = ref(null);
const groupFormRef = ref(null);

// 表单验证规则
const portalRules = {
  name: [{ required: true, message: "请输入门户名称", trigger: "blur" }],
  url: [{ required: true, message: "请输入链接地址", trigger: "blur" }],
  groups: [{ required: true, message: "请选择分组", trigger: "change" }],
  sharing_type: [
    { required: true, message: "请选择共享类型", trigger: "change" },
  ],
};

const groupRules = {
  group: [{ required: true, message: "请输入分组名称", trigger: "blur" }],
  sharing_type: [
    { required: true, message: "请选择共享类型", trigger: "change" },
  ],
};
const favoritesData = ref([]);
const syncCurrentGroupPortals = () => {
  if (!currentGroup.value) return;

  // 从 pgroupData 中找到当前组的最新数据
  const latestGroup = pgroupData.value.find(
    (group) => group.id === currentGroup.value.id
  );
  if (latestGroup) {
    // 更新 currentGroupPortals 为最新数据的副本
    currentGroupPortals.value = [...(latestGroup.portals || [])];
  }
};
// 获取分组数据
const getPgroup = async () => {
  try {
    const res = await proxy.$api.pgroupGet({ page: 1, page_size: 1000 });
    pgroupData.value = res.data.results;
    favoritesData.value = [];
    res.data.results.forEach((group) => {
      group.portals.forEach((portal) => {
        // portal.group = group.group;
        if (portal.is_favorite) {
          // 如果已存在则跳过
          if (
            favoritesData.value.findIndex((item) => item.id === portal.id) !==
            -1
          )
            return;
          favoritesData.value.push(portal);
        }
      });
    });
    // 同步当前组的数据
    syncCurrentGroupPortals();
  } catch (error) {
    ElMessage.error("获取分组数据失败");
    console.error(error);
  }
};

// 获取门户列表
const getPortal = async () => {
  try {
    const res = await proxy.$api.portalGet({ page: 1, page_size: 1000 });
    portalList.value = res.data.results;
  } catch (error) {
    ElMessage.error("获取门户数据失败");
    console.error(error);
  }
};

// 过滤后的分组
const filteredGroups = computed(() => {
  if (!filterPortal.value) {
    return pgroupData.value.filter((item) => item.portals.length > 0);
  }

  const searchTerm = filterPortal.value.toLowerCase();
  return pgroupData.value
    .map((group) => {
      // 过滤分组内的门户
      const filteredPortals = group.portals.filter(
        (portal) =>
          portal.name.toLowerCase().includes(searchTerm) ||
          portal.describe?.toLowerCase().includes(searchTerm) ||
          portal.url.toLowerCase().includes(searchTerm)
      );

      // 如果分组内还有门户，或者分组名称匹配，则显示该分组
      return {
        ...group,
        portals: filteredPortals,
      };
    })
    .filter(
      (group) =>
        group.portals.length > 0 ||
        group.group.toLowerCase().includes(searchTerm)
    );
});

// 根据字符串生成颜色
const getRandomColor = (str) => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }

  // 获取当前Element UI主题色
  const rootStyle = getComputedStyle(document.documentElement);
  let themeColor = rootStyle.getPropertyValue("--el-color-primary").trim();

  // 如果没有获取到主题色，使用默认值
  if (!themeColor) {
    themeColor = "#409EFF";
  }

  // 根据hash值生成主题色的不同明暗变体
  const lightnessVariation = (hash % 40) - 20; // -20到+20的明暗变化
  const saturationVariation = (hash % 20) - 10; // -10到+10的饱和度变化

  // 如果是十六进制颜色，转换为HSL进行调整
  if (themeColor.startsWith("#")) {
    const hsl = hexToHSL(themeColor);
    const newLightness = Math.min(90, Math.max(20, hsl.l + lightnessVariation));
    const newSaturation = Math.min(
      100,
      Math.max(30, hsl.s + saturationVariation)
    );
    return `hsl(${hsl.h}, ${newSaturation}%, ${newLightness}%)`;
  } else if (themeColor.startsWith("hsl")) {
    // 如果已经是HSL格式，直接调整
    const matches = themeColor.match(/hsl\((\d+),\s*(\d+)%,\s*(\d+)%\)/);
    if (matches) {
      const h = parseInt(matches[1]);
      const s = parseInt(matches[2]);
      const l = parseInt(matches[3]);
      const newLightness = Math.min(90, Math.max(20, l + lightnessVariation));
      const newSaturation = Math.min(
        100,
        Math.max(30, s + saturationVariation)
      );
      return `hsl(${h}, ${newSaturation}%, ${newLightness}%)`;
    }
  }

  // 默认返回主题色
  return themeColor;
};

// 辅助函数：将十六进制颜色转换为HSL对象
const hexToHSL = (hex) => {
  // 移除#符号
  hex = hex.replace("#", "");

  // 解析RGB值
  let r = parseInt(hex.substring(0, 2), 16) / 255;
  let g = parseInt(hex.substring(2, 4), 16) / 255;
  let b = parseInt(hex.substring(4, 6), 16) / 255;

  // 找到最大值和最小值
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);

  let h, s, l;

  l = (max + min) / 2;

  if (max === min) {
    h = s = 0; // 灰色
  } else {
    const delta = max - min;
    s = l > 0.5 ? delta / (2 - max - min) : delta / (max + min);

    switch (max) {
      case r:
        h = (g - b) / delta + (g < b ? 6 : 0);
        break;
      case g:
        h = (b - r) / delta + 2;
        break;
      case b:
        h = (r - g) / delta + 4;
        break;
    }

    h = Math.round(h * 60);
  }

  s = Math.round(s * 100);
  l = Math.round(l * 100);

  return { h, s, l };
};
const addPortalFormPgroup = () => {
  if (currentGroup.value.sharing_type === "public") {
    portalForm.sharing_type = "public";
  } else {
    portalForm.sharing_type = "private";
  }
  portalForm.groups = [currentGroup.value.id];
  portalAction.value = "add";
  portalDialogVisible.value = true;
};
// 处理添加命令
const handleAddCommand = (command) => {
  if (command === "portal") {
    // 添加门户
    portalAction.value = "add";

    portalDialogVisible.value = true;
  } else if (command === "group") {
    // 添加门户组
    groupAction.value = "add";

    groupDialogFormVisible.value = true;
  }
};
const editPortal = (portal) => {
  // 设置为编辑模式
  portalAction.value = "edit";

  // 填充表单数据

  // portalForm.name = portal.name;
  // portalForm.url = portal.url;
  // portalForm.sharing_type = portal.sharing_type;
  // portalForm.username = portal.username;
  // portalForm.password = portal.password;
  // portalForm.status = portal.status;
  // portalForm.target = portal.target;
  // portalForm.sort = portal.sort;
  // portalForm.describe = portal.describe;
  // portalForm.groups = portal.groups;
  Object.assign(portalForm, {
    id: portal.id,
    name: portal.name,
    url: portal.url,
    groups: portal.groups || [],
    sharing_type: portal.sharing_type,
    username: portal.username || "",
    password: "", // 不填充密码字段
    sort: portal.sort_order || 9999,
    target: portal.target !== undefined ? portal.target : true,
    describe: portal.describe || "",
    status: portal.status !== undefined ? portal.status : true,
  });

  // 显示门户编辑对话框
  portalDialogVisible.value = true;
};
// 提交门户表单
const submitPortalForm = () => {
  portalFormRef.value.validate(async (valid) => {
    if (!valid) return;

    portalSubmitting.value = true;
    try {
      let res;
      if (portalAction.value === "add") {
        res = await proxy.$api.portalAdd(portalForm);
        if (res.status === 201) {
          ElMessage.success("门户添加成功");
          closePortalDia();
          await getPgroup();
        } else {
          ElMessage.error("门户添加失败: " + JSON.stringify(res.data));
        }
      } else {
        // 编辑门户
        res = await proxy.$api.portalUpdate(portalForm);
        if (res.status === 200) {
          ElMessage.success("门户更新成功");
          closePortalDia();
          await getPgroup();
        } else {
          ElMessage.error("门户更新失败: " + JSON.stringify(res.data));
        }
      }
    } catch (error) {
      ElMessage.error("操作失败: " + error.message);
    } finally {
      portalSubmitting.value = false;
    }
  });
};
const deletePortal = (portal) => {
  ElMessageBox.confirm(
    `确定要删除门户 "${portal.name}" 吗？此操作不可撤销。`,
    "确认删除",
    {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    }
  )
    .then(async () => {
      try {
        const res = await proxy.$api.portalDelete(portal.id);
        if (res.status === 204) {
          ElMessage.success("门户删除成功");
          portalDialogVisible.value = false;
          await getPgroup();
        } else {
          ElMessage.error("门户删除失败");
        }
      } catch (error) {
        ElMessage.error("门户删除失败: " + error.message);
      }
    })
    .catch(() => {
      // 用户取消删除
    });
};
// 门户dialog关闭
const closePortalDia = () => {
  portalFormRef.value!.resetFields();
  portalDialogVisible.value = false;
};
// 提交门户组表单
const submitGroupForm = () => {
  groupFormRef.value.validate(async (valid) => {
    if (!valid) return;

    groupSubmitting.value = true;
    try {
      let res;
      if (groupAction.value === "add") {
        res = await proxy.$api.pgroupAdd(groupForm);
        if (res.status === 201) {
          ElMessage.success("门户组添加成功");
          groupDialogFormVisible.value = false;
          await getPgroup();
        } else {
          ElMessage.error("门户组添加失败: " + JSON.stringify(res.data));
        }
      } else {
        // 编辑门户组
        res = await proxy.$api.pgroupUpdate(groupForm);
        if (res.status === 200) {
          ElMessage.success("门户组更新成功");
          groupDialogFormVisible.value = false;
          await getPgroup();
        } else {
          ElMessage.error("门户组更新失败: " + JSON.stringify(res.data));
        }
      }
    } catch (error) {
      ElMessage.error("操作失败: " + error.message);
    } finally {
      groupSubmitting.value = false;
    }
  });
};

// 打开分组详情对话框
const openGroupDialog = (group) => {
  currentGroup.value = group;
  // 初始化 currentGroupPortals 为 group.portals 的副本
  currentGroupPortals.value = [...(group.portals || [])];
  groupDialogVisible.value = true;
};
// 关闭分组详情对话框
const closeGroupDialog = () => {
  groupDialogVisible.value = false;
  currentGroup.value = null;
};

// 处理门户排序更新
const handlePortalSort = async (event) => {
  // 手动重新排列数组元素
  const newData = [...currentGroupPortals.value];
  const movedItem = newData.splice(event.oldIndex, 1)[0];
  newData.splice(event.newIndex, 0, movedItem);

  // 更新数组
  currentGroupPortals.value = newData;

  console.log(currentGroupPortals.value.map((item) => item.name));
  let res = await proxy.$api.updatePortalOrder({
    group_id: currentGroup.value.id,
    ordering: currentGroupPortals.value.map((portal, index) => ({
      id: portal.id,
      sort_order: index + 1,
    })),
  });
  if (res.status === 200) {
    ElMessage.success("排序保存成功");
    // 更新本地数据
    await getPgroup(); // 重新获取门户数据
  } else {
    ElMessage.error("排序保存失败," + JSON.stringify(res.data));
  }
};

// 保存门户排序
const savePortalOrder = async () => {
  if (!currentGroup.value) return;

  savingOrder.value = true;

  try {
    // 构造排序数据
    const orderingData = currentGroupPortals.value.map((portal, index) => ({
      id: portal.id,
      sort: index + 1,
    }));

    // 调用API更新排序
    const res = await proxy.$api.portalUpdateSortOrder({
      ordering: orderingData,
      group_id: currentGroup.value.id,
    });

    if (res.status === 200) {
      ElMessage.success("排序保存成功");
      // 更新本地数据
      await getPortal(); // 重新获取门户数据
      closeGroupDialog();
    } else {
      ElMessage.error("排序保存失败");
    }
  } catch (error) {
    ElMessage.error("排序保存失败: " + error.message);
    console.error(error);
  } finally {
    savingOrder.value = false;
  }
};

// 打开门户链接
const openPortal = (portal) => {
  if (portal.target) {
    // 新窗口打开
    window.open(portal.url, "_blank");
  } else {
    // 当前窗口打开
    window.location.href = portal.url;
  }
};

const groupEditing = ref(false);
const groupNameInput = ref("");
// 更新组名

const startGroupEdit = () => {
  groupEditing.value = true;
  groupNameInput.value = currentGroup.value.group;
};

const cancelGroupEdit = () => {
  groupEditing.value = false;
  groupNameInput.value = "";
};

const saveGroupName = async () => {
  if (!groupNameInput.value.trim()) {
    ElMessage.error("组名不能为空");
    return;
  }

  if (groupNameInput.value === currentGroup.value.group) {
    // 名称未改变，直接取消编辑
    cancelGroupEdit();
    return;
  }

  try {
    // 调用API更新组名
    const res = await proxy.$api.pgroupUpdate({
      id: currentGroup.value.id,
      group: groupNameInput.value,
      sharing_type: currentGroup.value.sharing_type,
    });

    if (res.status === 200) {
      ElMessage.success("组名更新成功");
      // 更新本地数据
      await getPgroup();
      // 更新当前组的名称
      currentGroup.value.group = groupNameInput.value;
      // 退出编辑状态
      groupEditing.value = false;
    } else {
      ElMessage.error("组名更新失败");
    }
  } catch (error) {
    ElMessage.error("组名更新失败: " + error.message);
  }
};
// 收藏
const toggleFavorite = async (portal) => {
  if (portal.is_favorite) {
    // 取消收藏
    let res = await proxy.$api.removeFavorite({
      id: portal.id,
    });
    if (res.status === 204) {
      ElMessage.success("取消收藏成功");
      getPgroup();
    } else {
      ElMessage.error("取消收藏失败: " + JSON.stringify(res.data));
    }
  } else {
    // 收藏
    let res = await proxy.$api.addFavorite({
      id: portal.id,
    });
    if (res.status === 201) {
      ElMessage.success("收藏成功");
      getPgroup();
    } else {
      ElMessage.error("收藏失败: " + JSON.stringify(res.data));
    }
  }
};
// 初始化
onMounted(() => {
  Promise.all([getPgroup(), getPortal()]).catch((error) => {
    ElMessage.error("初始化数据失败");
    console.error(error);
  });
});
</script>

<style scoped lang="less">
.favorites-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.favorites-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .header-title {
    font-size: 24px;
    font-weight: bold;
  }

  .header-right {
    display: flex;
    align-items: center;
  }
}

.groups-container {
  flex: 1;
  overflow-y: auto;

  .group-col {
    margin-bottom: 20px;
  }

  .group-card {
    cursor: pointer;
    transition: all 0.3s ease;
    aspect-ratio: 1 / 1;
    display: flex;
    flex-direction: column;
    height: 450px;
    :deep(.el-card__body) {
      height: 100%;
    }
    .portal-preview-more {
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      background-color: #f5f7fa;
      color: #909399;
      font-weight: bold;
      font-size: 20px;
    }
  }

  .group-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    flex-shrink: 0;

    .group-info {
      display: flex;
      align-items: center;
      gap: 10px;

      .group-text-info {
        display: flex;
        flex-direction: column;
        gap: 5px;

        .group-name {
          font-size: 20px;
          font-weight: bold;
        }

        .sharing-type-tag {
          width: fit-content;
        }
      }
    }

    .group-stats {
      .portal-count {
        color: #909399;
        font-size: 16px;
      }
    }
  }

  .portals-grid-preview {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(3, 1fr);
    justify-items: center;
    gap: 8px;
    flex: 1;
    height: auto;
    /* 确保网格容器占满可用空间 */
    width: 100%;

    .portal-preview-item {
      display: flex;
      flex-direction: column;
      align-items: center;

      .portal-preview-wrapper {
        position: relative;
        width: 80px;
        height: 80px;

        .portal-preview-icon {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-weight: bold;
          font-size: 40px;
        }

        .portal-sharing-tag {
          position: absolute;
          bottom: -6px;
          right: -6px;
          height: 20px;
          line-height: 18px;
          padding: 0 6px;
          font-size: 12px;
        }
        .portal-favorite-tag {
          position: absolute;
          top: -12px;
          right: -15px;
          height: 20px;
          line-height: 18px;
          padding: 0 6px;
          font-size: 20px;
        }
        .portal-favorite-tag.favorited {
          color: #e6a23c;
        }

        .portal-favorite-tag:hover {
          color: #e6a23c;
        }
      }
    }
  }
}

.group-detail-dialog {
  .group-detail-header {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-bottom: 15px;

    .group-owner {
      color: #909399;
      font-size: 14px;
    }
  }

  .dialog-content {
    min-height: 400px;
    max-height: 60vh;
    overflow-y: auto;
  }

  .portals-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 15px;
    padding: 10px;
  }

  .portal-card {
    cursor: move;

    .portal-card-content {
      display: flex;
      align-items: center;
      gap: 15px;

      .portal-icon-wrapper {
        position: relative;

        .portal-icon {
          width: 50px;
          height: 50px;
          border-radius: 10px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-weight: bold;
          font-size: 20px;
        }

        .portal-sharing-tag-detail {
          position: absolute;
          bottom: -8px;
          right: -8px;
        }

        .drag-handle {
          position: absolute;
          bottom: -5px;
          right: -5px;
          background-color: #ecf5ff;
          border-radius: 50%;
          padding: 2px;
          color: #409eff;
          cursor: move;
        }
      }

      .portal-info {
        flex: 1;
        min-width: 0;

        .portal-name {
          font-weight: bold;
          font-size: 16px;
          margin-bottom: 5px;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .portal-url {
          font-size: 12px;
          color: #909399;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          margin-bottom: 5px;
        }

        .portal-description {
          font-size: 12px;
          color: #606266;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
      }

      .portal-actions {
        display: flex;
        align-items: center;
        gap: 5px;
      }
    }
  }

  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
  }
}

@media (max-width: 1200px) {
  .groups-container {
    .group-col {
      span: 12;
    }
  }
}

@media (max-width: 768px) {
  .favorites-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }

  .groups-container {
    .group-col {
      span: 24;
    }
  }

  .group-detail-dialog {
    .portals-grid {
      grid-template-columns: 1fr;
    }
  }
}
.dialog-header-edit {
  display: flex;
  align-items: center;
  gap: 15px;
}

.group-name-display {
  display: flex;
  align-items: center;
  gap: 10px;
}

.group-title {
  font-size: 18px;
  font-weight: bold;
}

.edit-icon {
  cursor: pointer;
  color: #409eff;
  font-size: 16px;
}

.edit-icon:hover {
  color: #66b1ff;
}

.group-name-edit {
  display: flex;
  align-items: center;
  gap: 10px;
}

.edit-buttons {
  display: flex;
  gap: 5px;
}
</style>