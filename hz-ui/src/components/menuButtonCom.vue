<template>
  <el-drawer
    v-model="showDrawer"
    title="菜单按钮编辑"
    direction="rtl"
    :before-close="handleClose"
    size="30%"
  >
    <el-row justify="space-between">
      <el-col :span="5">
        <el-text size="large" tag="b">菜单：{{ props.nowMenu.label }}</el-text>
      </el-col>
      <el-col :span="2">
        <el-button
          v-permission="`${route.name?.replace('_info', '')}:add`"
          type="primary"
          @click="handleAdd"
          >添加</el-button
        >
      </el-col>
    </el-row>

    <el-divider />
    <el-table border :data="menuButtonList" style="width: 100%">
      <el-table-column prop="name" label="按钮名称" />
      <el-table-column prop="action" label="按钮标识" />
      <el-table-column fixed="right" label="操作">
        <template #default="scope">
          <el-tooltip
            class="box-item"
            effect="dark"
            content="编辑菜单"
            placement="top"
          >
            <el-button
              v-permission="`${route.name?.replace('_info', '')}:edit`"
              link
              type="primary"
              :icon="Edit"
              @click="handleEdit(scope.row)"
            ></el-button>
          </el-tooltip>
          <el-tooltip
            class="box-item"
            effect="dark"
            content="删除"
            placement="top"
          >
            <el-button
              v-permission="`${route.name?.replace('_info', '')}:delete`"
              link
              type="danger"
              :icon="Delete"
              @click="handleDelete(scope.row)"
            ></el-button>
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>
  </el-drawer>
  <el-dialog
    v-model="dialogVisible"
    title="按钮配置"
    width="400"
    :before-close="diaHandleClose"
  >
    <el-form
      :inline="true"
      :model="formInline"
      ref="formRef"
      class="demo-form-inline"
    >
      <el-form-item label="按钮名称" required prop="name">
        <el-input v-model="formInline.name" placeholder="中文名" clearable />
      </el-form-item>
      <el-form-item
        label="按钮标识"
        placeholder="英文标识"
        required
        prop="action"
      >
        <el-input v-model="formInline.action" clearable />
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCommit"> 提交 </el-button>
      </div>
    </template>
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
const props = defineProps(["nowMenu"]);
const emit = defineEmits(["getMenuData"]);
const showDrawer = defineModel("showDrawer");
import { useRoute } from "vue-router";
const route = useRoute();
import axios from "axios";
import { ElMessage, ElMessageBox,FormInstance} from "element-plus";
import { CircleClose, Delete, Edit, Warning } from "@element-plus/icons-vue";
const formRef = ref<FormInstance>();
const menuButtonList = ref([]);
const updateMenuButtonList = (params) => {
  menuButtonList.value = params;
};
defineExpose({
  updateMenuButtonList,
});
const handleClose = () => {
  showDrawer.value = false;
};
const dialogVisible = ref(false);
const diaHandleClose = () => {
  dialogVisible.value = false;
};
const formInline = reactive({
  name: "",
  action: "",
  menu: "",
});
const hanldeAction = ref(true);
const handleAdd = () => {
  dialogVisible.value = true;
  hanldeAction.value = true;
  formInline.menu = props.nowMenu.id;
};
const handleEdit = (params) => {
  dialogVisible.value = true;
  hanldeAction.value = false;

  nextTick(() => {
    Object.keys(formInline).forEach((item) => {
      formInline[item] = params[item];
    });
    formInline.id = params.id;
    formInline.menu = params.menu;
  });
};

const getMenuButtonList = async () => {
  let res = await proxy.$api.getButton({ menu: props.nowMenu.id });
  menuButtonList.value = res.data.results;
};

const handleDelete = (row) => {
  ElMessageBox.confirm("是否确认删除?", "Warning", {
    confirmButtonText: "确认删除",
    cancelButtonText: "取消",
    type: "warning",
    draggable: true,
  })
    .then(async () => {
      // 发起删除请求
      let res = await proxy.$api.deleteButton(row.id);
      if (res.status == 204) {
        ElMessage({
          type: "success",
          message: "删除成功",
        });
        await getMenuButtonList();
        emit("getMenuData");
      } else {
        ElMessage({
          type: "error",
          message: "删除失败",
        });
      }
    })
    .catch(() => {
      ElMessage({
        type: "info",
        message: "取消删除",
      });
    });
};
const handleCommit = () => {
  formRef.value!.validate(async (valid) => {
    if (valid) {
      // 新增接口
      if (hanldeAction.value) {
        let res = await proxy.$api.addButton(formInline);
        //
        if (res.status == 201) {
          dialogVisible.value = false;

          // 重置表单
          formRef.value!.resetFields();

          getMenuButtonList();
          emit("getMenuData");
        } else {
          ElMessage({
            showClose: true,
            message: "添加失败:" + JSON.stringify(res.data),
            type: "error",
          });
        }
      }
      // 编辑接口
      else {
        let res = await proxy.$api.updateButton(formInline);
        if (res.status == 200) {
          dialogVisible.value = false;
          // 重置表单
          formRef.value!.resetFields();
          getMenuButtonList();
          emit("getMenuData");
        } else {
          ElMessage({
            showClose: true,
            message: "更新失败:" + JSON.stringify(res.data),
            type: "error",
          });
        }
      }
    } else {
      ElMessage({
        showClose: true,
        message: "请输入正确内容.",
        type: "error",
      });
    }
  });
};
</script>
  <style scoped>
.el-divider--horizontal {
  margin: 8px 0;
}
</style>