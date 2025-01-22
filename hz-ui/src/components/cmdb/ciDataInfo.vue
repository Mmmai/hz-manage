<template>
  <div class="card">
    <el-drawer
      v-model="ciDrawer"
      class="edit-drawer"
      direction="rtl"
      size="40%"
      :before-close="ciDataHandleClose"
    >
      <template #header>
        <el-text tag="b">实例信息</el-text>
      </template>
      <template #default>
        <el-tabs
          v-model="activeName"
          type="card"
          class="demo-tabs"
          @tab-click="handleClick"
        >
          <el-tab-pane label="模型字段" name="modelField">
            <el-form
              ref="ciDataFormRef"
              style="max-width: 100%"
              :model="ciDataForm"
              label-width="auto"
              status-icon
              label-position="top"
              :disabled="false"
              require-asterisk-position="right"
            >
              <!-- <div v-for="(item, index) in modelInfo.field_groups"> -->
              <el-form-item
                prop="instance_name"
                required
                style="margin-left: 30px"
              >
                <template #label>
                  <el-space :size="2">
                    <el-text tag="b">唯一标识</el-text>
                    <el-tooltip
                      content="唯一命名标识"
                      placement="right"
                      effect="dark"
                    >
                      <el-icon>
                        <Warning />
                      </el-icon>
                    </el-tooltip>
                  </el-space>
                </template>

                <el-input
                  v-model="ciDataForm.instance_name"
                  style="width: 240px"
                  v-if="isEdit"
                >
                </el-input>
                <span v-else class="requiredClass">{{
                  ciDataForm.instance_name
                }}</span>
              </el-form-item>
              <el-collapse v-model="activeArr">
                <el-collapse-item
                  :name="index"
                  v-for="(item, index) in modelInfo.field_groups"
                  :key="index"
                >
                  <template #title>
                    <el-text tag="b" size="large">{{
                      item.verbose_name
                    }}</el-text>
                  </template>
                  <!-- <h4>{{ item.verbose_name }}</h4> -->
                  <!-- <el-row justify="space-evenly"> -->
                  <el-row style="margin-left: 30px">
                    <el-col v-for="(fitem, findex) in item.fields" :span="12">
                      <!-- <span>{{ fitem.name  }}</span> -->

                      <el-form-item
                        :label="fitem.verbose_name"
                        :prop="fitem.name"
                        v-if="fitem.type === 'string'"
                        :required="fitem.required"
                        :rules="setFormItemRule(fitem.validation_rule)"
                      >
                        <template #label>
                          <el-space :size="2">
                            <el-text tag="b">{{ fitem.verbose_name }}</el-text>
                            <el-tooltip
                              :content="fitem.description"
                              placement="right"
                              effect="dark"
                              v-if="
                                fitem.description.length != 0 ? true : false
                              "
                            >
                              <el-icon>
                                <Warning />
                              </el-icon>
                            </el-tooltip>
                          </el-space>
                        </template>
                        <div v-if="!isEdit">
                          <div v-if="ciDataForm[fitem.name] != null">
                            <el-link
                              v-if="fitem.name === 'mgmt_ip'"
                              :href="`https://${ciDataForm[fitem.name]}`"
                              type="primary"
                              target="_blank"
                            >
                              {{ ciDataForm[fitem.name] }}
                            </el-link>
                            <span
                              v-else
                              class="text_class"
                              :class="{ requiredClass: fitem.required }"
                              >{{ ciDataForm[fitem.name] }}</span
                            >
                          </div>

                          <span v-else>--</span>
                        </div>
                        <!-- <el-input v-model="ciDataForm[fitem.name]" style="width: 240px" v-else-if=""></el-input> -->
                        <el-input
                          v-model="ciDataForm[fitem.name]"
                          style="width: 240px"
                          v-else
                        ></el-input>
                      </el-form-item>
                      <el-form-item
                        :label="fitem.verbose_name"
                        :prop="fitem.name"
                        v-if="fitem.type === 'json'"
                        :required="fitem.required"
                      >
                        <template #label>
                          <el-space :size="2">
                            <el-text tag="b">{{ fitem.verbose_name }}</el-text>
                            <el-tooltip placement="right" effect="dark">
                              <template #content>
                                json类型字段<br />请输入json格式数据!
                              </template>

                              <el-icon><InfoFilled /></el-icon>
                            </el-tooltip>
                            <el-tooltip
                              :content="fitem.description"
                              placement="right"
                              effect="dark"
                              v-if="
                                fitem.description.length != 0 ? true : false
                              "
                            >
                              <el-icon>
                                <Warning />
                              </el-icon>
                            </el-tooltip>
                          </el-space>
                        </template>
                        <div v-if="!isEdit">
                          <span
                            class="text_class"
                            v-if="ciDataForm[fitem.name] != null"
                            :class="{ requiredClass: fitem.required }"
                            >{{ ciDataForm[fitem.name] }}</span
                          >
                          <span v-else>--</span>
                        </div>
                        <el-input
                          v-model="ciDataForm[fitem.name]"
                          style="width: 240px"
                          autosize
                          type="textarea"
                          v-else
                        ></el-input>
                      </el-form-item>
                      <el-form-item
                        :label="fitem.verbose_name"
                        :prop="fitem.name"
                        v-if="
                          ['text'].indexOf(fitem.type) >>> -1 ? false : true
                        "
                        :required="fitem.required"
                      >
                        <template #label>
                          <el-space :size="2">
                            <el-text tag="b">{{ fitem.verbose_name }}</el-text>
                            <el-tooltip
                              :content="fitem.description"
                              placement="right"
                              effect="dark"
                              v-if="
                                fitem.description.length != 0 ? true : false
                              "
                            >
                              <el-icon>
                                <Warning />
                              </el-icon>
                            </el-tooltip>
                          </el-space>
                        </template>
                        <div v-if="!isEdit">
                          <span
                            class="text_class"
                            v-if="ciDataForm[fitem.name] != null"
                            :class="{ requiredClass: fitem.required }"
                            >{{ ciDataForm[fitem.name] }}</span
                          >
                          <span v-else>--</span>
                        </div>
                        <el-input
                          v-model="ciDataForm[fitem.name]"
                          style="width: 240px"
                          autosize
                          type="textarea"
                          v-else
                        ></el-input>
                      </el-form-item>
                      <el-form-item
                        :label="fitem.verbose_name"
                        :prop="fitem.name"
                        v-if="fitem.type === 'boolean'"
                        :required="fitem.required"
                      >
                        <template #label>
                          <el-space :size="2">
                            <el-text tag="b">{{ fitem.verbose_name }}</el-text>
                            <el-tooltip
                              :content="fitem.description"
                              placement="right"
                              effect="dark"
                              v-if="
                                fitem.description.length != 0 ? true : false
                              "
                            >
                              <el-icon>
                                <Warning />
                              </el-icon>
                            </el-tooltip>
                          </el-space>
                        </template>
                        <!-- <span>{{ fitem.verbose_name }}</span> -->
                        <el-switch
                          v-model="ciDataForm[fitem.name]"
                          style="
                            --el-switch-on-color: #13ce66;
                            --el-switch-off-color: #ff4949;
                          "
                          :disabled="!isEdit"
                        />
                      </el-form-item>
                      <el-form-item
                        :label="fitem.verbose_name"
                        :prop="fitem.name"
                        v-if="
                          ['float'].indexOf(fitem.type) >>> -1 ? false : true
                        "
                        :required="fitem.required"
                      >
                        <template #label>
                          <el-space :size="2">
                            <el-text
                              tag="b"
                              v-if="fitem.unit !== null ? true : false"
                              >{{
                                fitem.verbose_name + "(" + fitem.unit + ")"
                              }}</el-text
                            >
                            <el-text tag="b" v-else>{{
                              fitem.verbose_name
                            }}</el-text>
                            <el-tooltip
                              :content="fitem.description"
                              placement="right"
                              effect="dark"
                              v-if="
                                fitem.description.length != 0 ? true : false
                              "
                            >
                              <el-icon>
                                <Warning />
                              </el-icon>
                            </el-tooltip>
                          </el-space>
                        </template>
                        <div v-if="!isEdit">
                          <span
                            class="text_class"
                            v-if="ciDataForm[fitem.name] != null"
                            :class="{ requiredClass: fitem.required }"
                            >{{ ciDataForm[fitem.name] }}</span
                          >
                          <span v-else>--</span>
                        </div>
                        <el-input-number
                          v-model="ciDataForm[fitem.name]"
                          :precision="2"
                          :step="1"
                          v-else
                        />
                      </el-form-item>
                      <!-- 密码类型 -->
                      <el-form-item
                        :label="fitem.verbose_name"
                        :prop="fitem.name"
                        v-if="
                          ['password'].indexOf(fitem.type) >>> -1 ? false : true
                        "
                        :required="fitem.required"
                      >
                        <template #label>
                          <el-space :size="2">
                            <el-text tag="b">{{ fitem.verbose_name }}</el-text>
                            <el-tooltip
                              :content="fitem.description"
                              placement="right"
                              effect="dark"
                              v-if="
                                fitem.description.length != 0 ? true : false
                              "
                            >
                              <el-icon>
                                <Warning />
                              </el-icon>
                            </el-tooltip>
                          </el-space>
                        </template>
                        <div v-if="!isEdit">
                          <div v-if="ciDataForm[fitem.name]?.length >> 0">
                            <span v-if="showAllPass">
                              {{
                                decrypt_sm4(
                                  gmConfig.key,
                                  gmConfig.mode,
                                  ciDataForm[fitem.name]
                                )
                              }}</span
                            >
                            <span
                              v-else
                              :class="{ requiredClass: fitem.required }"
                              @mouseenter="showPassButton = true"
                              @mouseleave="showPassButton = false"
                              >********
                              <el-popover
                                v-permission="
                                  `${route.name?.replace(
                                    '_info',
                                    ''
                                  )}:showPassword`
                                "
                                :width="380"
                                trigger="click"
                                @after-leave="clearPass"
                              >
                                <template #reference
                                  ><el-icon
                                    ><View
                                      v-show="showPassButton && !showAllPass"
                                  /></el-icon>
                                </template>
                                <el-form
                                  ref="passFormRef"
                                  :inline="true"
                                  :model="passwordForm"
                                  require-asterisk-position="right"
                                >
                                  <el-row align="middle">
                                    <el-col :span="20">
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
                                          auto-complete="new-password"
                                          placeholder="输入密钥查看密码"
                                          clearable
                                          style="width: 250px"
                                        />
                                      </el-form-item>
                                    </el-col>
                                    <el-col :span="2">
                                      <el-form-item>
                                        <el-button
                                          type="primary"
                                          size="small"
                                          @click="
                                            getPassword(
                                              passFormRef,
                                              ciDataForm[fitem.name]
                                            )
                                          "
                                          >查看</el-button
                                        >
                                      </el-form-item>
                                    </el-col>
                                  </el-row>
                                </el-form>
                                <el-text tag="b" v-if="isShowPass"
                                  >密码: {{ fieldPassword }}
                                  <el-tooltip
                                    class="box-item"
                                    effect="dark"
                                    content="点击复制密码"
                                    placement="top"
                                  >
                                    <el-icon
                                      ><CopyDocument v-copy="fieldPassword"
                                    /></el-icon>
                                  </el-tooltip>
                                </el-text>
                              </el-popover>
                            </span>
                          </div>

                          <span v-else>--</span>
                        </div>
                        <el-input
                          v-model="ciDataForm[fitem.name]"
                          style="width: 240px"
                          type="password"
                          auto-complete="new-password"
                          show-password
                          clearable
                          v-else
                        ></el-input>
                      </el-form-item>
                      <el-form-item
                        :label="fitem.verbose_name"
                        :prop="fitem.name"
                        v-if="
                          ['integer'].indexOf(fitem.type) >>> -1 ? false : true
                        "
                        :required="fitem.required"
                      >
                        <template #label>
                          <el-space :size="2">
                            <el-text
                              tag="b"
                              v-if="fitem.unit !== null ? true : false"
                              >{{
                                fitem.verbose_name + "(" + fitem.unit + ")"
                              }}</el-text
                            >
                            <el-text tag="b" v-else>{{
                              fitem.verbose_name
                            }}</el-text>
                            <el-tooltip
                              :content="fitem.description"
                              placement="right"
                              effect="dark"
                              v-if="
                                fitem.description.length != 0 ? true : false
                              "
                            >
                              <el-icon>
                                <Warning />
                              </el-icon>
                            </el-tooltip>
                          </el-space>
                        </template>
                        <div v-if="!isEdit">
                          <span
                            class="text_class"
                            v-if="ciDataForm[fitem.name] != null"
                            :class="{ requiredClass: fitem.required }"
                            >{{ ciDataForm[fitem.name] }}</span
                          >
                          <span v-else>--</span>
                        </div>
                        <el-input-number
                          v-model="ciDataForm[fitem.name]"
                          :step="1"
                          v-else
                        />
                      </el-form-item>
                      <el-form-item
                        :label="fitem.verbose_name"
                        :prop="fitem.name"
                        v-if="
                          ['date'].indexOf(fitem.type) >>> -1 ? false : true
                        "
                        :required="fitem.required"
                      >
                        <template #label>
                          <el-space :size="2">
                            <el-text tag="b">{{ fitem.verbose_name }}</el-text>
                            <el-tooltip
                              :content="fitem.description"
                              placement="right"
                              effect="dark"
                              v-if="
                                fitem.description.length != 0 ? true : false
                              "
                            >
                              <el-icon>
                                <Warning />
                              </el-icon>
                            </el-tooltip>
                          </el-space>
                        </template>
                        <div v-if="!isEdit">
                          <span
                            v-if="ciDataForm[fitem.name] != null"
                            :class="{ requiredClass: fitem.required }"
                            >{{ ciDataForm[fitem.name] }}</span
                          >
                          <span v-else>--</span>
                        </div>
                        <el-date-picker
                          v-else
                          v-model="ciDataForm[fitem.name]"
                          type="date"
                          placeholder="Pick a Date"
                          format="YYYY-MM-DD"
                          value-format="YYYY-MM-DD"
                        />
                      </el-form-item>
                      <el-form-item
                        :label="fitem.verbose_name"
                        :prop="fitem.name"
                        v-if="
                          ['datetime'].indexOf(fitem.type) >>> -1 ? false : true
                        "
                        :required="fitem.required"
                      >
                        <template #label>
                          <el-space :size="2">
                            <el-text tag="b">{{ fitem.verbose_name }}</el-text>
                            <el-tooltip
                              :content="fitem.description"
                              placement="right"
                              effect="dark"
                              v-if="
                                fitem.description.length != 0 ? true : false
                              "
                            >
                              <el-icon>
                                <Warning />
                              </el-icon>
                            </el-tooltip>
                          </el-space>
                        </template>
                        <div v-if="!isEdit">
                          <span
                            v-if="ciDataForm[fitem.name] != null"
                            :class="{ requiredClass: fitem.required }"
                            >{{ ciDataForm[fitem.name] }}</span
                          >
                          <span v-else>--</span>
                        </div>
                        <el-date-picker
                          v-else
                          v-model="ciDataForm[fitem.name]"
                          type="datetime"
                          placeholder="Pick a Date"
                          format="YYYY/MM/DD hh:mm:ss"
                          value-format="YYYY-MM-DD hh:mm:ss"
                        />
                      </el-form-item>
                      <el-form-item
                        :label="fitem.verbose_name"
                        :prop="fitem.name"
                        v-if="
                          ['enum'].indexOf(fitem.type) >>> -1 ? false : true
                        "
                        :required="fitem.required"
                      >
                        <template #label>
                          <el-space :size="2">
                            <el-text tag="b">{{ fitem.verbose_name }}</el-text>
                            <el-tooltip
                              :content="fitem.description"
                              placement="right"
                              effect="dark"
                              v-if="
                                fitem.description.length != 0 ? true : false
                              "
                            >
                              <el-icon>
                                <Warning />
                              </el-icon>
                            </el-tooltip>
                          </el-space>
                        </template>
                        <div v-if="!isEdit">
                          <span
                            v-if="ciDataForm[fitem.name] != null"
                            :class="{ requiredClass: fitem.required }"
                            >{{ currentRow[fitem.name]?.label }}</span
                          >
                          <span v-else>--</span>
                        </div>
                        <el-select
                          v-else
                          v-model="ciDataForm[fitem.name]"
                          placeholder="请选择"
                          style="width: 240px"
                        >
                          <el-option
                            v-for="item in enumOptionObj[fitem.validation_rule]"
                            :key="item.value"
                            :label="item.label"
                            :value="item.value"
                          />
                        </el-select>
                      </el-form-item>
                      <el-form-item
                        :label="fitem.verbose_name"
                        :prop="fitem.name"
                        v-if="
                          ['model_ref'].indexOf(fitem.type) >>> -1
                            ? false
                            : true
                        "
                        :required="fitem.required"
                      >
                        <template #label>
                          <el-space :size="2">
                            <el-text tag="b">{{ fitem.verbose_name }}</el-text>
                            <el-tooltip
                              :content="fitem.description"
                              placement="right"
                              effect="dark"
                              v-if="
                                fitem.description.length != 0 ? true : false
                              "
                            >
                              <el-icon>
                                <Warning />
                              </el-icon>
                            </el-tooltip>
                          </el-space>
                        </template>
                        <div v-if="!isEdit">
                          <span
                            class="text_class"
                            v-if="ciDataForm[fitem.name] != null"
                            :class="{ requiredClass: fitem.required }"
                            >{{ currentRow[fitem.name].name }}</span
                          >
                          <span v-else>--</span>
                        </div>

                        <el-select
                          v-else
                          v-model="ciDataForm[fitem.name]"
                          clearable
                          placeholder="请选择"
                          style="width: 240px"
                          filterable
                        >
                          <el-option
                            v-for="(citem, cIndex) in modelRefOptions[
                              fitem.name
                            ]"
                            :key="cIndex"
                            :label="citem.label"
                            :value="citem.value"
                          />
                        </el-select>
                      </el-form-item>
                    </el-col>
                  </el-row>
                </el-collapse-item>
              </el-collapse>
            </el-form>
          </el-tab-pane>
          <el-tab-pane label="Config" name="second">Config</el-tab-pane>
          <el-tab-pane label="Role" name="third">Role</el-tab-pane>
          <el-tab-pane label="Task" name="fourth">Task</el-tab-pane>
        </el-tabs>
      </template>
      <template #footer>
        <div style="flex: auto" class="footerButtonClass">
          <el-button @click="ciDataCancel(ciDataFormRef)">取消</el-button>
          <div v-if="commitActionAdd">
            <el-button type="primary" @click="ciDataCommit(ciDataFormRef)"
              >添加</el-button
            >
          </div>
          <div v-else>
            <div v-if="isEdit">
              <el-button
                v-permission="`${route.name?.replace('_info', '')}:delete`"
                type="danger"
                @click="ciDataDelete"
                v-if="currentRow.instance_group?.indexOf(treeIdleId) !== -1"
                >删除</el-button
              >
              <el-tooltip
                v-permission="`${route.name?.replace('_info', '')}:delete`"
                content="无法删除非空闲池的主机"
                placement="top"
                effect="dark"
                v-else
              >
                <el-button type="danger" @click="ciDataDelete" disabled
                  >删除</el-button
                >
              </el-tooltip>
              <el-button
                type="primary"
                @click="ciDataCommit(ciDataFormRef)"
                v-throttle
                >保存</el-button
              >
            </div>
            <div v-else>
              <el-button
                v-permission="`${route.name?.replace('_info', '')}:edit`"
                type="primary"
                @click="isEdit = true"
                >编辑</el-button
              >
            </div>
          </div>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script lang="ts" setup>
import {
  ref,
  computed,
  watch,
  getCurrentInstance,
  onMounted,
  reactive,
  nextTick,
} from "vue";
const { proxy } = getCurrentInstance();
import { useStore } from "vuex";
const store = useStore();
</script>
<style scoped lang="scss">
</style>