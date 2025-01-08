/<template>
  <el-dialog v-model="showAllPassDia" title="查看密码" width="400">
    <el-form
      ref="allPassFormRef"
      :inline="true"
      :model="passwordForm"
      require-asterisk-position="right"
      label-position="left"
    >
      <el-form-item
        label="密钥"
        prop="secret"
        :rules="[
          {
            required: true,
            message: '输入密钥',
            trigger: 'blur',
          },
        ]"
      >
        <el-input
          type="password"
          v-model="passwordForm.secret"
          show-password
          placeholder="输入密钥查看密码"
          clearable
          style="width: 250px"
        />
      </el-form-item>
      <el-form-item label="有效时间" prop="time">
        <el-input-number
          v-model="passwordForm.time"
          :min="1"
          :step="1"
          :max="30"
        >
          <template #suffix>
            <span>分钟</span>
          </template>
        </el-input-number>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="getPassword(allPassFormRef)">
          查看
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import { watch, ref, onMounted, reactive, computed } from "vue";
import { encrypt_sm4, decrypt_sm4 } from "@/utils/gmCrypto.ts";
import { ElNotification } from "element-plus";
import useConfigStore from "@/store/config";
const configStore = useConfigStore();
const showAllPassDia = defineModel("showAllPassDia");
const gmConfig = computed(() => configStore.gmCry);

const clearPass = () => {
  isShowPass.value = false;
  resetForm(allPassFormRef.value[0]);
  fieldPassword.value = "";
};
const allPassFormRef = ref();

const passwordForm = reactive({
  secret: null,
  time: 3,
});
const fieldPassword = ref("");
const isShowPass = ref(false);
const getPassword = async (formEl: FormItemInstance | undefined) => {
  formEl!.validate(async (valid) => {
    if (valid) {
      if (passwordForm.secret === gmConfig.value.key) {
        // 解密
        ElNotification({
          title: "操作成功",
          message: "解密成功," + passwordForm.time + "分钟后过期！",
          type: "success",
          duration: 2000,
        });
        configStore.updateShowAllPass(true);

        showAllPassDia.value = false;
        // 设置计时器,到时间就清除密码显示
        configStore.setShowAllPassTime(passwordForm.time * 60 * 1000);
        resetForm(allPassFormRef.value!);
      } else {
        ElNotification({
          title: "操作失败",
          message: "密钥错误",
          type: "warning",
          duration: 2000,
        });
      }
    }
  });
};
const resetForm = (formEl: FormInstance | undefined) => {
  if (!formEl) return;
  formEl.resetFields();
};
const handleClose = () => {
  showAllPassDia.value = false;
  resetForm(allPassFormRef.value!);
};
</script>



<style scoped lang="ts">
</style>