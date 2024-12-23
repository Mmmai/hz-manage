<template>
  <ciDataFilter
    :ciModelId="props.ciModelId"
    :currentNodeId="props.currentNodeId"
    :allModelFieldByNameObj="allModelFieldByNameObj"
    :enumOptionObj="enumOptionObj"
    :validationRulesObj="validationRulesObj"
    :allModelField="allModelField"
    :modelRefOptions="modelRefOptions"
    v-model:showFilter="showFilter"
    @updateFilterParam="updateFilterParam"
    @getCiData="getCiData"
    ref="ciDataFilterRef"
  />

  <!-- <el-button @click="getHasConfigField">1111</el-button> -->
  <div class="card table-main" v-if="reloadTable" style="width: 100%; flex: 1">
    <div class="table-header">
      <div class="header-button-lf">
        <el-button type="primary" @click="addCiData">添加</el-button>
        <!-- <el-button @click="isShowUpload = true">导入</el-button> -->
        <el-button
          :disabled="!(multipleSelect.length >>> 0)"
          @click="ciDataToTree = true"
          >转移</el-button
        >

        <el-button :disabled="!(multipleSelect.length >>> 0)">导出</el-button>
        <el-button
          :disabled="!(multipleSelect.length >>> 0)"
          @click="multipleUpdate"
          >批量更新</el-button
        >
      </div>
      <div class="header-button-ri">
        <el-tooltip
          class="box-item"
          effect="dark"
          content="刷新表格"
          placement="top"
        >
          <el-button :icon="Refresh" circle @click="reloadWind" />
        </el-tooltip>

        <el-tooltip
          class="box-item"
          effect="dark"
          content="配置表格显示列"
          placement="top"
        >
          <el-button :icon="Operation" circle @click="editCol" />
        </el-tooltip>

        <el-tooltip
          class="box-item"
          effect="dark"
          content="实例导入"
          placement="top"
        >
          <el-button :icon="UploadFilled" circle @click="isShowUpload = true" />
        </el-tooltip>

        <el-tooltip
          class="box-item"
          effect="dark"
          content="打开过滤器"
          placement="top"
        >
          <el-button :icon="Search" circle @click="openFilter" />
        </el-tooltip>
      </div>
    </div>
    <div class="flexJstart gap-1" style="overflow: auto">
      <el-text v-show="filterTags.length >>> 0" tag="b">过滤器</el-text>
      <el-tag
        v-for="(tag, index) in filterTags"
        :key="tag.name"
        closable
        type="primary"
        @close="tagClose(tag.field, index)"
      >
        {{ tag.name }}
      </el-tag>
    </div>
    <el-table
      ref="ciDataTableRef"
      :data="ciDataList"
      @selection-change="handleSelectionChange"
      table-layout="fixed"
      highlight-current-row
      v-loading="tableLoading"
      style="flex: 1"
      :row-key="get_row_key"
    >
      <el-table-column
        type="selection"
        :selectable="selectable"
        width="55"
        :reserve-selection="true"
      />
      <el-table-column prop="name" label="名称" fixed="left" width="180" />

      <!-- <el-table-column label="Date" width="120" @row-click="editCiData">
                  <template #default="scope">{{ scope.row.date }}</template>
</el-table-column> -->
      <el-table-column
        v-for="(data, index) in hasConfigField"
        :property="data.name"
        :label="data.verbose_name"
        show-overflow-tooltip
        sortable
        min-width="120"
      >
        <!-- 列表显示布尔值按钮，以及模型关联、枚举类的label值 -->
        <template
          #default="scope"
          v-if="modelFieldType.boolean.indexOf(data.name) != -1"
        >
          <el-switch
            v-model="scope.row[data.name]"
            class="ml-2"
            style="
              --el-switch-on-color: #13ce66;
              --el-switch-off-color: #ff4949;
            "
            @change="
              updateCiData({
                id: scope.row.id,
                fields: { [data.name]: scope.row[data.name] },
              })
            "
          />
        </template>
        <template
          #default="scope"
          v-if="modelFieldType.enum.indexOf(data.name) != -1"
        >
          <span>{{ scope.row[data.name].label }}</span>
        </template>
        <template
          #default="scope"
          v-if="modelFieldType.model_ref.indexOf(data.name) != -1"
        >
          <span>{{ scope.row[data.name]?.name }}</span>
        </template>
      </el-table-column>
      <el-table-column fixed="right" width="150" label="操作">
        <!-- <template #header>
        <el-button @click="editCol" :icon="Setting" circle />
      </template> -->
        <template #default="scope">
          <el-tooltip
            class="box-item"
            effect="dark"
            content="查看详情"
            placement="top"
          >
            <el-button
              link
              type="primary"
              :icon="View"
              @click="editCiData(scope.row)"
            ></el-button>
          </el-tooltip>
          <el-tooltip
            class="box-item"
            effect="dark"
            content="编辑"
            placement="top"
          >
            <el-button
              link
              type="primary"
              :icon="Edit"
              @click="editCiData(scope.row, true)"
            ></el-button>
          </el-tooltip>
          <el-tooltip
            class="box-item"
            effect="dark"
            content="克隆"
            placement="top"
          >
            <el-button
              link
              type="primary"
              :icon="CopyDocument"
              @click="cpCiData(scope.row)"
            ></el-button>
          </el-tooltip>
          <el-tooltip
            class="box-item"
            effect="dark"
            content="点击查看二维码"
            placement="top"
          >
            <span style="margin-left: 12px">
              <el-popover
                placement="bottom"
                title="实例二维码"
                :width="250"
                trigger="click"
              >
                <template #reference>
                  <el-button link type="primary" :icon="Grid"></el-button>
                </template>
                <a-qrcode :value="JSON.stringify(scope.row)" :size="200" />
              </el-popover>
            </span>
          </el-tooltip>

          <!-- <el-tooltip class="box-item" effect="dark" content="扫描二维码" placement="top">
        </el-tooltip> -->
          <!-- <el-button link type="primary" size="small">Edit</el-button> -->
        </template>
      </el-table-column>
    </el-table>
    <!-- 分页 -->
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :page-sizes="[10, 20, 50, 100, 200]"
      :size="size"
      :disabled="disabled"
      layout="slot,total, sizes, prev, pager, next, jumper"
      :total="totalCount"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      style="margin-top: 5px; justify-content: flex-end"
    >
      <el-text>已选择 {{ multipleSelect.length }} 条</el-text>
    </el-pagination>
  </div>

  <!-- 实例编辑的弹出框 -->

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
        <el-form-item prop="name" required style="margin-left: 30px">
          <template #label>
            <el-space :size="2">
              <span>唯一标识</span>
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
            v-model="ciDataForm.name"
            style="width: 240px"
            v-if="isEdit"
          >
          </el-input>
          <span v-else class="requiredClass">{{ ciDataForm.name }}</span>
        </el-form-item>
        <el-collapse v-model="activeArr">
          <el-collapse-item
            :name="index"
            v-for="(item, index) in modelInfo.field_groups"
            :key="index"
          >
            <template #title>
              <el-text tag="b" size="large">{{ item.verbose_name }}</el-text>
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
                      <span>{{ fitem.verbose_name }}</span>
                      <el-tooltip
                        :content="fitem.description"
                        placement="right"
                        effect="dark"
                        v-if="fitem.description.length != 0 ? true : false"
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
                  v-if="
                    ['text', 'json'].indexOf(fitem.type) >>> -1 ? false : true
                  "
                  :required="fitem.required"
                >
                  <template #label>
                    <el-space :size="2">
                      <span>{{ fitem.verbose_name }}</span>
                      <el-tooltip
                        :content="fitem.description"
                        placement="right"
                        effect="dark"
                        v-if="fitem.description.length != 0 ? true : false"
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
                  v-if="['float'].indexOf(fitem.type) >>> -1 ? false : true"
                  :required="fitem.required"
                >
                  <template #label>
                    <el-space :size="2">
                      <span v-if="fitem.unit !== null ? true : false">{{
                        fitem.verbose_name + "(" + fitem.unit + ")"
                      }}</span>
                      <span v-else>{{ fitem.verbose_name }}</span>
                      <el-tooltip
                        :content="fitem.description"
                        placement="right"
                        effect="dark"
                        v-if="fitem.description.length != 0 ? true : false"
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
                  <el-input-number
                    v-model="ciDataForm[fitem.name]"
                    :precision="2"
                    :step="0.1"
                    v-else
                  />
                </el-form-item>
                <!-- 密码类型 -->
                <el-form-item
                  :label="fitem.verbose_name"
                  :prop="fitem.name"
                  v-if="['password'].indexOf(fitem.type) >>> -1 ? false : true"
                  :required="fitem.required"
                >
                  <template #label>
                    <el-space :size="2">
                      <span>{{ fitem.verbose_name }}</span>
                      <el-tooltip
                        :content="fitem.description"
                        placement="right"
                        effect="dark"
                        v-if="fitem.description.length != 0 ? true : false"
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
                      @mouseenter="showPassButton = true"
                      @mouseleave="showPassButton = false"
                      >********
                      <el-popover
                        :width="380"
                        trigger="click"
                        @after-leave="clearPass"
                      >
                        <template #reference
                          ><el-icon><View v-show="showPassButton" /></el-icon>
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
                                  @click="getPassword(passFormRef, fitem.name)"
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

                    <span v-else>--</span>
                  </div>
                  <el-input
                    v-model="ciDataForm[fitem.name]"
                    style="width: 240px"
                    type="password"
                    show-password
                    clearable
                    v-else
                  ></el-input>
                </el-form-item>
                <el-form-item
                  :label="fitem.verbose_name"
                  :prop="fitem.name"
                  v-if="['integer'].indexOf(fitem.type) >>> -1 ? false : true"
                  :required="fitem.required"
                >
                  <template #label>
                    <el-space :size="2">
                      <span v-if="fitem.unit !== null ? true : false">{{
                        fitem.verbose_name + "(" + fitem.unit + ")"
                      }}</span>
                      <span v-else>{{ fitem.verbose_name }}</span>
                      <el-tooltip
                        :content="fitem.description"
                        placement="right"
                        effect="dark"
                        v-if="fitem.description.length != 0 ? true : false"
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
                  <el-input-number
                    v-model="ciDataForm[fitem.name]"
                    :step="1"
                    v-else
                  />
                </el-form-item>
                <el-form-item
                  :label="fitem.verbose_name"
                  :prop="fitem.name"
                  v-if="['date'].indexOf(fitem.type) >>> -1 ? false : true"
                  :required="fitem.required"
                >
                  <template #label>
                    <el-space :size="2">
                      <span>{{ fitem.verbose_name }}</span>
                      <el-tooltip
                        :content="fitem.description"
                        placement="right"
                        effect="dark"
                        v-if="fitem.description.length != 0 ? true : false"
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
                  v-if="['datetime'].indexOf(fitem.type) >>> -1 ? false : true"
                  :required="fitem.required"
                >
                  <template #label>
                    <el-space :size="2">
                      <span>{{ fitem.verbose_name }}</span>
                      <el-tooltip
                        :content="fitem.description"
                        placement="right"
                        effect="dark"
                        v-if="fitem.description.length != 0 ? true : false"
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
                  v-if="['enum'].indexOf(fitem.type) >>> -1 ? false : true"
                  :required="fitem.required"
                >
                  <template #label>
                    <el-space :size="2">
                      <span>{{ fitem.verbose_name }}</span>
                      <el-tooltip
                        :content="fitem.description"
                        placement="right"
                        effect="dark"
                        v-if="fitem.description.length != 0 ? true : false"
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
                      >{{ currentRow[fitem.name].label }}</span
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
                  v-if="['model_ref'].indexOf(fitem.type) >>> -1 ? false : true"
                  :required="fitem.required"
                >
                  <template #label>
                    <el-space :size="2">
                      <span>{{ fitem.verbose_name }}</span>
                      <el-tooltip
                        :content="fitem.description"
                        placement="right"
                        effect="dark"
                        v-if="fitem.description.length != 0 ? true : false"
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
                      v-for="(citem, cIndex) in modelRefOptions[fitem.name]"
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
              type="danger"
              @click="ciDataDelete"
              v-if="currentRow.instance_group.indexOf(treeIdleId) !== -1"
              >删除</el-button
            >
            <el-tooltip
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
            <el-button type="primary" @click="isEdit = true">编辑</el-button>
          </div>
        </div>

        <!-- <el-button type="primary" @click="ciDataCommit(ciDataFormRef)" v-if="saveButtonShow">{{ postButtonLabel }}</el-button> -->
        <!-- <el-button type="primary" @click="isEdit = true" v-if="editButtonShow">编辑</el-button> -->
        <!-- <el-button type="primary" @click="ciDataCommit(ciDataFormRef)" v-else="commitActionAdd">提交</el-button> -->

        <!-- <el-button type="primary" @click="ciDrawer = false" v-else>确认</el-button> -->
      </div>
    </template>
  </el-drawer>

  <!-- 批量更新 -->
  <el-dialog
    v-model="multipleDia"
    title="批量更新"
    width="500"
    :before-close="handleClose"
  >
    <el-form
      ref="multipleFormRef"
      style="max-width: 1000px"
      :model="multipleForm"
      label-width="auto"
    >
      <el-form-item
        v-for="(item, index) in paramNames"
        :key="`param-${item}`"
        :label="'字段' + (index + 1)"
        :prop="`updateParams.${item}`"
        :rules="
          setUpdateFormItemRule(allModelFieldByNameObj[item]?.validation_rule)
        "
        :required="true"
      >
        <!--       :rules="modelFieldFormItemRule"
        :rules="setUpdateFormItemRule(allModelFieldByNameObj[item.name]?.validation_rule)"
   :rules="setFormItemRule(item.name)"  -->
        <el-space>
          <el-select
            :model-value="item.startsWith('__temp') ? undefined : item"
            placeholder="选择字段"
            style="width: 120px"
            filterable
            @change="selectName(index, $event)"
          >
            <el-option
              v-for="oitem in allModelFieldOptions"
              :key="oitem.value"
              :label="oitem.label"
              :value="oitem.value"
              :disabled="oitem.disable"
            />
          </el-select>
          <div v-if="item && !item.startsWith('__temp')">
            <div
              v-if="
                ['text', 'json'].indexOf(allModelFieldByNameObj[item].type) >>>
                -1
                  ? false
                  : true
              "
            >
              <el-input
                v-model="multipleForm.updateParams[item]"
                type="textarea"
                autosize
                style="width: 180px"
              />
            </div>
            <div
              v-else-if="
                ['string'].indexOf(allModelFieldByNameObj[item].type) >>> -1
                  ? false
                  : true
              "
            >
              <el-input
                v-model="multipleForm.updateParams[item]"
                style="width: 180px"
              />
            </div>
            <div
              v-else-if="
                ['enum'].indexOf(allModelFieldByNameObj[item].type) >>> -1
                  ? false
                  : true
              "
            >
              <el-select
                v-model="multipleForm.updateParams[item]"
                placeholder="请选择"
                style="width: 180px"
              >
                <el-option
                  v-for="ritem in enumOptionObj[
                    allModelFieldByNameObj[item].validation_rule
                  ]"
                  :key="ritem.value"
                  :label="ritem.label"
                  :value="ritem.value"
                />
              </el-select>
            </div>
            <div
              v-else-if="
                ['model_ref'].indexOf(allModelFieldByNameObj[item].type) >>> -1
                  ? false
                  : true
              "
            >
              <el-select
                v-model="multipleForm.updateParams[item]"
                placeholder="请选择"
                style="width: 240px"
                filterable
              >
                <!--                 @visible-change="
                  getModelRefCiData($event, {
                    id: allModelFieldByNameObj[item].ref_model,
                    name: item,
                  })
                " -->
                <el-option
                  v-for="(citem, cIndex) in modelRefOptions[item]"
                  :key="cIndex"
                  :label="citem.label"
                  :value="citem.value"
                />
              </el-select>
            </div>
            <div
              v-else-if="
                ['boolean'].indexOf(allModelFieldByNameObj[item].type) >>> -1
                  ? false
                  : true
              "
            >
              <el-switch
                v-model="multipleForm.updateParams[item]"
                style="
                  --el-switch-on-color: #13ce66;
                  --el-switch-off-color: #ff4949;
                "
              />
            </div>
            <div
              v-else-if="
                ['integer'].indexOf(allModelFieldByNameObj[item].type) >>> -1
                  ? false
                  : true
              "
            >
              <el-input-number
                v-model="multipleForm.updateParams[item]"
                :step="1"
                style="width: 180px"
              />
            </div>
            <div
              v-else-if="
                ['float'].indexOf(allModelFieldByNameObj[item].type) >>> -1
                  ? false
                  : true
              "
            >
              <el-input-number
                v-model="multipleForm.updateParams[item]"
                :precision="2"
                :step="0.1"
                style="width: 180px"
              />
            </div>
            <div
              v-else-if="
                ['date'].indexOf(allModelFieldByNameObj[item].type) >>> -1
                  ? false
                  : true
              "
            >
              <el-date-picker
                v-model="multipleForm.updateParams[item]"
                type="date"
                placeholder="Pick a Date"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 180px"
              />
            </div>
            <div
              v-else-if="
                ['datetime'].indexOf(allModelFieldByNameObj[item].type) >>> -1
                  ? false
                  : true
              "
            >
              <el-date-picker
                v-model="multipleForm.updateParams[item]"
                type="datetime"
                placeholder="Pick a Date"
                format="YYYY/MM/DD hh:mm:ss"
                value-format="YYYY-MM-DD hh:mm:ss"
                style="width: 180px"
              />
            </div>

            <div v-else>
              <el-input v-model="multipleForm.updateParams[item]" />
            </div>
          </div>
          <el-button
            class="mt-2"
            :icon="Delete"
            circle
            @click.prevent="removeUpdateParams(index, item)"
          >
          </el-button>
        </el-space>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="multipleDia = false">取消</el-button>
        <el-button @click.prevent="addUpdateParams()">新增字段</el-button>
        <el-button
          v-throttle
          type="primary"
          @click="saveCommit"
          :disabled="paramNames.length > 0 ? false : true"
          >保存</el-button
        >
      </div>
    </template>
  </el-dialog>

  <!-- 实例组更新 -->
  <el-dialog v-model="ciDataToTree" title="实例组编辑" width="500">
    <el-cascader
      :options="props.treeData"
      :props="cascaderProps"
      clearable
      v-model="selectTreeNode"
      style="width: 400px"
    />
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="ciDataToTree = false">取消</el-button>
        <el-button type="primary" @click="treeDataCommit"> 提交更新 </el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 实例导入 -->
  <ciDataUpload
    v-model:isShowUpload="isShowUpload"
    :ciModelId="props.ciModelId"
  />
  <ciDataTableCol
    :ciModelId="props.ciModelId"
    :allModelField="allModelField"
    :allModelFieldInfo="allModelFieldInfo"
    v-model:isShowTableCol="ciModelColDrawer"
    v-model:hasConfigField="hasConfigField"
    @reloadTable="reloadWind"
    ref="ciDataTableColRef"
  />
</template>

<script lang="ts" setup>
import ciDataUpload from "./ciDataUpload.vue";
import ciDataTableCol from "./ciDataTableCol.vue";
import {
  Check,
  Delete,
  Setting,
  Message,
  Search,
  Star,
  View,
  Warning,
  Grid,
  Refresh,
  Operation,
  CopyDocument,
  UploadFilled,
  Edit,
} from "@element-plus/icons-vue";
import { ElMessageBox, ElMessage, ElNotification } from "element-plus";
import { Rank } from "@element-plus/icons-vue";
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
import { da, pa } from "element-plus/es/locale/index.mjs";
const { proxy } = getCurrentInstance();
import type { FormInstance, FormItemInstance, FormRules } from "element-plus";
import ciDataFilter from "./ciDataFilter.vue";
import { useStore } from "vuex";
import { useClipboard } from "vue-clipboard3";
import { debounce } from "lodash";
const store = useStore();
const emit = defineEmits(["getTree"]);
const props = defineProps(["ciModelId", "treeData", "currentNodeId"]);
// const treeData = defineModel("treeData");
// const currentNodeId = defineModel("currentNodeId");
const activeArr = ref([0]);
const showFilter = ref(false);
const openFilter = () => {
  showFilter.value = true;
};
const ciDataFilterRef = ref("");
const closeFilter = () => {
  showFilter.value = false;
};
// 密码相关
const showPassButton = ref(false);
const clearPass = () => {
  isShowPass.value = false;
  resetForm(passFormRef.value[0]);
  fieldPassword.value = "";
};
const passFormRef = ref();

const passwordForm = reactive({
  secret: null,
});
const fieldPassword = ref("");
const isShowPass = ref(false);
const getPassword = async (formEl: FormItemInstance | undefined, fieldName) => {
  console.log(passFormRef.value[0]);
  formEl![0].validate(async (valid) => {
    if (valid) {
      console.log(passwordForm);
      if (passwordForm.secret === "thinker") {
        let res = await proxy.$api.getCiModelInstance({
          decrypt_password: true,
          name: currentRow.value.name,
          model: props.ciModelId,
        });
        fieldPassword.value = res.data.results[0].fields[fieldName];
        isShowPass.value = true;
      } else {
        ElNotification({
          title: "Warning",
          message: "密钥错误",
          type: "warning",
          duration: 2000,
        });
        isShowPass.value = false;
        fieldPassword.value = "";
      }
    }
  });
};
// 分页
const currentPage = ref(1);
const pageSize = ref(10);
const size = ref("default");
const disabled = ref(false);
const handleSizeChange = () => {
  getCiData({
    model: props.ciModelId,
    model_instance_group: props.currentNodeId,
  });
};
const handleCurrentChange = () => {
  getCiData({
    model: props.ciModelId,
    model_instance_group: props.currentNodeId,
  });
};
// 导入导出
const isShowUpload = ref(false);
// 实例组关联更新
const cascaderProps = { multiple: true, value: "id" };
const ciDataToTree = ref(false);
const selectTreeNode = ref([]);
const treeIdleId = computed(() => {
  return props.treeData[0].children[0].id;
});

const treeDataCommit = async () => {
  let _tmepArr = [];
  selectTreeNode.value?.forEach((item) => {
    _tmepArr.push(item[item.length - 1]);
  });
  // console.log("已选择的组id", _tmepArr);
  // console.log("已选的实例", multipleSelectId.value);

  let res = await proxy.$api.setCiDataToTree({
    instances: multipleSelectId.value,
    groups: _tmepArr,
  });
  if (res.status == "201") {
    ElMessage({ type: "success", message: "更新成功" });
    // 重置表单
    getCiData({
      model: props.ciModelId,
      model_instance_group: props.currentNodeId,
    });
    clearMultipleSelect();
    emit("getTree");
  } else {
    ElMessage({
      showClose: true,
      message: "更新失败:" + JSON.stringify(res.data),
      type: "error",
    });
  }
  selectTreeNode.value = [];
  ciDataToTree.value = false;
  // 触发tree更新,addCode
};
// 批量更新
const multipleFormRef = ref("");
const multipleDia = ref(false);
const multipleUpdate = () => {
  multipleDia.value = true;
  console.log(multipleForm);
};

const setUpdateFormItemRule = (params) => {
  // let regexp =
  if (params === undefined) return;
  if (validationRulesObj.value[params]?.field_type === "string") {
    if (params == "" || params == null) return;
    // proxy.$commonFunc.validateRegexp(regexp)
    return [
      {
        pattern: new RegExp(validationRulesObj.value[params].rule),
        message: "不符合正则表达式",
        trigger: "blur",
      },
    ];
  }
};
const modelFieldFormItemRule = computed(() => {
  // let regexp =
  let tempList = {};
  modelInfo.value?.field_groups?.forEach((item) => {
    item.fields.forEach((field) => {
      if (
        field.type === "string" &&
        field.validation_rule !== "" &&
        field.validation_rule !== null
      ) {
        tempList["updateParams." + field.name] = [
          {
            pattern: new RegExp(
              validationRulesObj.value[field.validation_rule]?.rule
            ),
            message: "不符合正则表达式",
            trigger: "blur",
          },
        ];
      }
    });
  });
  return tempList;
});

const multipleForm = reactive({
  updateParams: {},
});
// 定义一个map用来知道每一行对应哪个name
const paramNames = ref<string[]>([]);

// 禁用已选择的
// const
const addUpdateParams = () => {
  const index = Object.keys(multipleForm.updateParams).length;
  const tempKey = `__temp_param_${index}`;
  paramNames.value[index] = tempKey;
  multipleForm.updateParams[tempKey] = "";
};
const selectName = (index, name) => {
  // 这里你需要考虑重新选择name，需不需要清空value值
  // 把name替换进去, 把原来那个删掉
  // 删掉原来的key
  console.log(name);
  // 保留原值
  // multipleForm.updateParams[name] = multipleForm.updateParams[paramNameLineMap[index]];
  // or 清空值
  multipleForm.updateParams[name] = undefined;

  // 删除原来的key, 并且更新map
  delete multipleForm.updateParams[paramNames.value[index]];
  paramNames.value[index] = name;
};
const removeUpdateParams = (index, key) => {
  paramNames.value.splice(index, 1);
  delete multipleForm.updateParams[key];
};
const saveCommit = () => {
  console.log(multipleFormRef.value);
  multipleFormRef.value!.validate(async (valid) => {
    console.log(valid);
    if (valid) {
      // 批量更新的方法
      // multipleForm.updateParams = [];
      // paramNames.value = [];
      // multipleDia.value = false;
      // console.log(multipleForm.updateParams);

      // return;
      let res = await proxy.$api.multipleUpdateCiModelInstance({
        update_user: store.state.username,
        instances: multipleSelectId.value,
        fields: multipleForm.updateParams,
      });

      // 发起更新请求
      if (res.status == "200") {
        ElMessage({ type: "success", message: "更新成功" });
        // 重置表单
        getCiData({
          model: props.ciModelId,
          model_instance_group: props.currentNodeId,
        });
        // resetForm(multipleFormRef.value)
        multipleForm.updateParams = {};
        paramNames.value = [];
        console.log(multipleForm.updateParams);
        multipleDia.value = false;
      } else {
        ElMessage({
          showClose: true,
          message: "更新失败:" + JSON.stringify(res.data),
          type: "error",
        });
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
const allModelFieldOptions = computed<any>(() => {
  let tempList = new Array();
  modelInfo.value?.field_groups?.forEach((item) => {
    item.fields.forEach((field) => {
      let isDisabled = false;
      if (field.name in multipleForm.updateParams) {
        isDisabled = true;
      }
      tempList.push({
        value: field.name,
        label: field.verbose_name,
        disable: isDisabled,
      });
    });
  });
  return tempList;
});
const handleClose = () => {
  multipleDia.value = false;
  resetForm(multipleFormRef.value);
};

const tableLoading = ref(true);
const setLoading = (boolean) => {
  tableLoading.value = boolean;
};
const reloadTable = ref(true);
const isEdit = ref(false);
const ciModelColDrawer = ref(false);
const editCol = () => {
  ciModelColDrawer.value = true;
};
// 更新

const updateCiData = async (params) => {
  setLoading(true);
  let res = await proxy.$api.updateCiModelInstance({
    update_user: store.state.username,
    ...params,
  });
  // console.log(123)
  if (res.status == "200") {
    ElMessage({ type: "success", message: "更新成功" });
    // 重置表单
    ciDrawer.value = false;
    resetForm(ciDataFormRef.value);
    await getCiData({
      model: props.ciModelId,
      model_instance_group: props.currentNodeId,
    });
  } else {
    ElMessage({
      showClose: true,
      message: "更新失败:" + JSON.stringify(res.data),
      type: "error",
    });
  }
};
const selectable = () => true;

// 表格勾选
const ciDataTableRef = ref("");
const get_row_key = (row) => {
  return row.id;
};
const multipleSelect = ref([]);
const multipleSelectId = computed(() => {
  let tempArr = [];
  multipleSelect.value?.forEach((item) => {
    tempArr.push(item.id);
  });
  return tempArr;
});
const handleSelectionChange = (val) => {
  multipleSelect.value = val;
};

const clearMultipleSelect = () => {
  multipleSelect.value = [];
  ciDataTableRef.value!.clearSelection();
};
// 穿梭框排序

// 表格显示内容
// 修改显示列的弹出框
// const allModelField = ref([])
const hasConfigField = ref([]);

const modelInfo = ref({});
const allModelFieldInfo = computed<any>(() => {
  let tempList = {};
  modelInfo.value?.field_groups?.forEach((item) => {
    item.fields.forEach((field) => {
      tempList[field.id] = field;
    });
  });
  return tempList;
});
const allModelFieldByNameObj = computed<any>(() => {
  let tempList = {};
  modelInfo.value?.field_groups?.forEach((item) => {
    item.fields.forEach((field) => {
      tempList[field.name] = field;
    });
  });
  return tempList;
});
// 表格显示列
const ciDataTableColRef = ref("");
const getHasConfigField = () => {
  ciDataTableColRef.value!.getHasConfigField();
};

// 列显示

const reloadWind = () => {
  // window.location.reload();
  reloadTable.value = false;
  nextTick(() => {
    reloadTable.value = true;
  });
};
// console.log(allModelFieldInfo.value)
// watch(() => hasConfigField.value, (n,) => {
// }, { deep: true })

// 枚举类的字段下拉框
// 获取所有枚举类的字典
const validationRulesObj = ref({});
const validationRulesByNameObj = ref({});
const getRules = async (params = null) => {
  let res = await proxy.$api.getValidationRules({
    ...params,
    page: 1,
    page_size: 10000,
  });
  // validationRules.value = res.data
  res.data.results.forEach((item) => {
    validationRulesObj.value[item.id] = item;
    // validationRulesByNameObj.value[item.name] = item
  });
};
// 生成以规则ID为key，枚举类的选项为value的对象字典
const enumOptionObj = computed(() => {
  let tempList = {};
  modelInfo.value?.field_groups?.forEach((item) => {
    item.fields.forEach((field) => {
      if (field.type === "enum") {
        // let ruleObj = JSON.parse(validationRulesObj.value[params].rule)
        // JSON.parse(validationRulesObj.value[params].rule)
        let ruleObj = JSON.parse(
          validationRulesObj.value[field.validation_rule].rule
        );
        let tmpList = [];
        Object.keys(ruleObj).forEach((ritem) => {
          tmpList.push({ value: ritem, label: ruleObj[ritem] });
        });
        tempList[field.validation_rule] = tmpList;
      }
    });
  });
  return tempList;
});
const enumOptionNameObj = computed(() => {
  let tempList = {};
  modelInfo.value.field_groups.forEach((item) => {
    item.fields.forEach((field) => {
      if (field.type === "enum") {
        // let ruleObj = JSON.parse(validationRulesObj.value[params].rule)
        // JSON.parse(validationRulesObj.value[params].rule)
        let ruleObj = JSON.parse(
          validationRulesObj.value[field.validation_rule].rule
        );
        let tmpList = {};
        Object.keys(ruleObj).forEach((ritem) => {
          // tmpList.push({ value: ritem, label: ruleObj[ritem] })
          tmpList[ritem] = ruleObj[ritem];
        });
        tempList[field.name] = tmpList;
      }
    });
  });
  return tempList;
});

// 模型引用
const modelRefOptions = ref({});
const getModelRefCiData = async (visible, params) => {
  if (!visible) return;
  let res = await proxy.$api.getModelRefCi({
    model: params.id,
    page: 1,
    page_size: 1000,
  });
  let tmpArr = [];
  res.data.results.forEach((item) => {
    tmpArr.push({ value: item.id, label: item.name });
  });
  modelRefOptions.value[params.name] = [
    { value: null, label: "无" },
    ...tmpArr,
  ];
};
const modelRefDataById = computed(() => {
  let tmpObj = new Object();
  for (let [mKey, mValue] of Object.entries(modelRefOptions.value)) {
    let tmpArr = new Object();
    mValue?.forEach((item) => {
      // if (item.label !== "无") {
      //   tmpArr[item.value] = item;
      // }
      tmpArr[item.value] = item;
    });
    tmpObj[mKey] = tmpArr;
  }
  return tmpObj;
});

// 获取模型关联相关模型的数据
const getModelRefData = async (model) => {
  let res = await proxy.$api.getModelRefCi({
    model: model,
    page: 1,
    page_size: 10000,
  });
  return res.data.results;
};
const setFormItemRule = (rule) => {
  // console.log(rule)
  // let regexp =
  if (rule == "" || rule == null) return;
  // proxy.$commonFunc.validateRegexp(regexp)
  return [
    {
      pattern: new RegExp(validationRulesObj.value[rule].rule),
      message: "不符合正则表达式",
      trigger: "blur",
    },
  ];
};
// 初始化表单数据
const initCiDataForm = () => {
  // let initObj = {}
  modelInfo.value.field_groups.forEach((item) => {
    item.fields.forEach((item2) => {
      // console.log(item2)
      ciDataForm[item2.name] = item2.default;
    });
  });
  // ciDataForm = initObj
  // ciDataForm.name = null
};

// 获取模型实例字段和模型信息

const allModelField = ref([]);
const getModelField = async () => {
  // let res = await proxy.$api.getCiModel({ name: 'hosts' })
  // ciModel.value = res.data.results[0]
  let res2 = await proxy.$api.getCiModel({}, props.ciModelId);
  modelInfo.value = res2.data;
  let tempArr = [];
  modelInfo.value.field_groups?.forEach((item) => {
    item.fields.forEach((field) => {
      tempArr.push(field);
    });
  });
  allModelField.value = tempArr;
  // 赋值初始化过滤条件
  // ciDataFilterRef.value!.initFilterLists([allModelField.value[0]]);
  // console.log()
};

const modelFieldType = computed(() => {
  let tempObj = {
    enum: [],
    boolean: [],
    model_ref: [],
  };
  allModelField.value.forEach((item) => {
    if (item.type === "enum") {
      tempObj.enum.push(item.name);
    } else if (item.type === "boolean") {
      tempObj.boolean.push(item.name);
    } else if (item.type === "model_ref") {
      tempObj.model_ref.push(item.name);
    }
  });
  return tempObj;
});
watch(
  () => modelFieldType.value.model_ref,
  (n) => {
    // console.log();
    modelFieldType.value.model_ref.forEach((item) => {
      getModelRefCiData(true, {
        id: allModelFieldByNameObj.value[item].ref_model,
        name: item,
      });
    });
  },
  { deep: true }
);

// 获取ci数据
const ciDataList = ref([]);
const totalCount = ref(0);
const filterParam = ref({});
const updateFilterParam = (params) => {
  filterParam.value = params;
};
const filterTags = computed(() => {
  let tmpArr = new Array();
  for (let [fName, fValue] of Object.entries(filterParam.value)) {
    // console.log(key + ": " + value);
    if (fName === "name") {
      tmpArr.push({ name: "唯一标识:" + fValue, field: fName });
    } else {
      if (modelFieldType.value.model_ref.indexOf(fName) !== -1) {
        // 判断是否为空
        tmpArr.push({
          name:
            allModelFieldByNameObj.value[fName].verbose_name +
            ":" +
            modelRefDataById.value[fName][fValue].label,
          field: fName,
        });
      } else if (modelFieldType.value.enum.indexOf(fName) !== -1) {
        console.log(enumOptionNameObj.value);
        tmpArr.push({
          name:
            allModelFieldByNameObj.value[fName].verbose_name +
            ":" +
            enumOptionNameObj.value[fName][fValue],
          field: fName,
        });
      } else {
        tmpArr.push({
          name: allModelFieldByNameObj.value[fName].verbose_name + ":" + fValue,
          field: fName,
        });
      }
    }
  }
  return tmpArr;
});
const tagClose = async (name, index) => {
  await ciDataFilterRef.value!.removeFilterParam(name, index);
  nextTick(() => {
    getCiData({
      model: props.ciModelId,
      model_instance_group: props.currentNodeId,
    });
  });
};

const getCiData = async (params) => {
  // console.log("子组件调用的")
  // return
  // filterParam.value = tmpObj;
  setLoading(true);
  let tmpList = new Array();
  let res = await proxy.$api.getCiModelInstance({
    ...params,
    page: currentPage.value,
    page_size: pageSize.value,
    ...filterParam.value,
    // decrypt_password: true,
  });
  totalCount.value = res.data.count;
  res.data.results.forEach((item) => {
    tmpList.push({
      id: item.id,
      instance_group: item.instance_group,
      name: item.name,
      ...item.fields,
    });
  });
  ciDataList.value = tmpList;
  setLoading(false);
};
// const loadingInstance = ElLoading.service(options)

// setTimeout(() => {
//   loadingInstance.close()
//   }, 2000)
onMounted(async () => {
  // const loading = ElLoading.service({
  //   lock: true,
  //   text: 'Loading',
  //   background: 'rgba(0, 0, 0, 0.7)',
  // })
  // await ciDataTableColRef.value!.getHasConfigField();
  await getRules();
  setLoading(false);

  // 依赖模型id
  // await getModelField();
  // await getHasConfigField();
  // await getCiData({model: props.ciModelId,model_instance_group: props.currentNodeId,});
  // // getModelField()
  // await initCiDataForm();
  // setTimeout(() => {
  //   loading.close()
  // }, 2000)
  //   nextTick(() => {
  //   // Loading should be closed asynchronously
  //   loadingInstance.close()
  // })
});

// 实例编辑弹出框
const ciDrawer = ref(false);
const addCiData = () => {
  isEdit.value = true;
  ciDrawer.value = true;
  commitActionAdd.value = true;
  // await initCiDataForm();
};

// 按钮显示

const currentRow = ref({});
const beforeEditCiDataForm = ref({});
const editCiData = (params, edit = false) => {
  ciDrawer.value = true;
  commitActionAdd.value = false;
  isEdit.value = edit;
  currentRow.value = params;
  // getModelRefCiData(true,params.)
  nextTick(() => {
    Object.keys(params).forEach(
      (item) => {
        // if (ciDataForm.hasOwnProperty(item)) ciDataForm[item] = params[item]
        if (item === "id" || item === "instance_group") return;
        // if (item === "")
        // 如果是模型引用，则赋予id
        if (modelFieldType.value.model_ref.indexOf(item) !== -1) {
          // console.log(123, params[item]);
          if (params[item] !== null) {
            ciDataForm[item] = params[item].id;
          } else {
            ciDataForm[item] = params[item];
          }
        } else {
          ciDataForm[item] = params[item];
        }
      } // isDisabled.value = params.built_in
    );
    console.log(ciDataForm);
    // ciDataForm = params
    beforeEditCiDataForm.value = JSON.parse(JSON.stringify(ciDataForm));
  });
};
const cpCiData = (params) => {
  ciDrawer.value = true;
  commitActionAdd.value = true;
  isEdit.value = true;
  currentRow.value = params;
  nextTick(() => {
    Object.keys(params).forEach(
      (item) => {
        // if (ciDataForm.hasOwnProperty(item)) ciDataForm[item] = params[item]
        if (item === "id" || item === "instance_group") return;
        if (modelFieldType.value.model_ref.indexOf(item) !== -1) {
          // console.log(123, params[item]);
          if (params[item] !== null) {
            ciDataForm[item] = params[item].id;
          } else {
            ciDataForm[item] = params[item];
          }
        } else {
          ciDataForm[item] = params[item];
        }
      } // isDisabled.value = params.built_in
    );
    // ciDataForm = params
  });
  ElNotification({
    title: "Warning",
    message: "复制实例，请修改后再提交",
    type: "warning",
    duration: 2000,
  });
};

const ciDataFormRef = ref<FormInstance>();
const ciDataForm = reactive({
  name: null,
});
const rmNameObj = computed(() => {
  let tmpObj = Object.assign({}, ciDataForm);
  delete tmpObj.name;
  return tmpObj;
});
const rmNameObjUpdate = computed(() => {
  let tmpObj = Object.assign({}, updateParams.value);
  delete tmpObj.name;
  return tmpObj;
});

const commitActionAdd = ref(true);
const updateParams = ref({});
const ciDataCommit = async (
  formEl: FormInstance | undefined,
  params = null
) => {
  if (!formEl) return;
  // 增加如果用户进入编辑模式后，没有更新，点击确认的话，就不会调度后端更新
  await formEl.validate(async (valid, fields) => {
    if (valid) {
      if (commitActionAdd.value) {
        // 添加
        // let rmNameObj = Object.assign({}, ciDataForm)
        // delete rmNameObj.name
        let res = await proxy.$api.addCiModelInstance({
          model: props.ciModelId,
          create_user: store.state.username,
          update_user: store.state.username,
          fields: rmNameObj.value,
          name: ciDataForm.name,
          instance_group: currentRow.value.instance_group,
        });
        // console.log(res)
        // console.log(123)
        if (res.status == "201") {
          ElMessage({ type: "success", message: "添加成功" });
          // 重置表单
          ciDrawer.value = false;
          resetForm(formEl);
          // getModelField();
          // 刷新页面
          await getCiData({
            model: props.ciModelId,
            model_instance_group: props.currentNodeId,
          });
          emit("getTree");
        } else {
          ElMessage({
            showClose: true,
            message: "添加失败:" + JSON.stringify(res.data),
            type: "error",
          });
        }
      } else {
        // console.log(111)
        console.log(JSON.stringify(beforeEditCiDataForm.value));
        console.log(JSON.stringify(ciDataForm));

        if (
          JSON.stringify(beforeEditCiDataForm.value) ===
          JSON.stringify(ciDataForm)
        ) {
          isEdit.value = false;
          ciDrawer.value = false;
          resetForm(formEl);
          ElMessage({
            showClose: true,
            message: "无更新,关闭窗口",
            type: "info",
          });
          return;
        } else {
          // 判断此次用户操作的字段
          // 通过entires转为键值对数组
          const arr1 = Object.entries(beforeEditCiDataForm.value);
          const arr2 = Object.entries(ciDataForm);
          //拼接后推入set中，但是需要将数组转为json字符串否则无法对比值的一致性
          const arr = arr1.concat(arr2).map((item) => JSON.stringify(item));
          const result = Array.from(new Set(arr)).map((item) =>
            JSON.parse(item)
          );
          //裁剪掉第一个对象占用掉的部分，剩下就是第二个对象与其不同的属性部分
          result.splice(0, arr1.length);
          //将键值对数组转为正常对象
          const obj = Object.fromEntries(result);
          console.log(obj);
          let tmpObj = {};
          Object.keys(obj).forEach((item) => {
            if (String(obj[item]) != "") {
              tmpObj[item] = obj[item];
            }
          });
          updateParams.value = tmpObj;
          if (Object.keys(updateParams.value).length === 0) {
            isEdit.value = false;
            ciDrawer.value = false;
            resetForm(formEl);
            ElMessage({
              showClose: true,
              message: "无更新,关闭窗口",
              type: "info",
            });
            return;
          }
          // return
        }
        // name的判断有没有更新
        // let updateObj = new Object();
        let updateObj = {
          id: currentRow.value.id,
          model: modelInfo.value.id,
          update_user: store.state.username,
        };
        if (Object.keys(updateParams.value).indexOf("name") === -1) {
          updateObj["fields"] = updateParams.value;
          // fields: updateParams.value,
        } else {
          updateObj["name"] = updateParams.value.name;
          updateObj["fields"] = rmNameObjUpdate.value;
        }

        let res = await proxy.$api.updateCiModelInstance(updateObj);
        // console.log(123)
        if (res.status == "200") {
          ElMessage({ type: "success", message: "更新成功" });
          // 重置表单
          ciDrawer.value = false;
          isEdit.value = false;
          resetForm(formEl);
          await getCiData({
            model: props.ciModelId,
            model_instance_group: props.currentNodeId,
          });
        } else {
          ElMessage({
            showClose: true,
            message: "更新失败:" + JSON.stringify(res.data),
            type: "error",
          });
        }
      }
      // console.log('submit!')
    } else {
      console.log("error submit!", fields);
    }
  });
};
// 取消弹窗
const ciDataHandleClose = (done: () => void) => {
  ElMessageBox.confirm("是否确认关闭?")
    .then(() => {
      done();
      resetForm(ciDataFormRef.value);
      ciDrawer.value = false;
      isEdit.value = false;
    })
    .catch(() => {
      // catch error
    });
};
// 取消按钮
const ciDataCancel = (formEl) => {
  resetForm(formEl);
  ciDrawer.value = false;
  isEdit.value = false;
};
// 实例删除
const ciDataDelete = (params = null) => {
  ElMessageBox.confirm("是否确认删除?", "实例删除", {
    confirmButtonText: "确认删除",
    cancelButtonText: "取消",
    type: "warning",
    draggable: true,
  })
    .then(async () => {
      // 发起删除请求
      let res = await proxy.$api.deleteCiModelInstance(currentRow.value.id);
      //
      // let res = {status:204}
      if (res.status == 204) {
        ElMessage({
          type: "success",
          message: "删除成功",
        });
        // 重新加载页面数据
        await getCiData({
          model: props.ciModelId,
          model_instance_group: props.currentNodeId,
        });
        resetForm(ciDataFormRef.value);
        ciDrawer.value = false;
        isEdit.value = false;
        emit("getTree");
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
// 重置表单
const resetForm = (formEl: FormInstance | undefined) => {
  if (!formEl) return;
  formEl.resetFields();
  currentRow.value = {};
};

const filterMethod = (query, item) => {
  if (!query) {
    return true;
  }
  return item.verbose_name.includes(query);
};

defineExpose({
  getHasConfigField,
  getCiData,
  initCiDataForm,
  getModelField,
  setLoading,
  closeFilter,
  clearMultipleSelect,
});
</script>
<style scoped lang="scss">
:deep(.el-transfer-panel__item).el-checkbox {
  margin-right: 10px;

  .transferLable {
    display: flex;
    justify-content: space-between !important;
  }
}

.el-transfer ::v-deep(.el-transfer-panel):first-child .sort {
  display: none;
}

.el-drawer__header {
  margin-bottom: 0px !important;
}

:deep(.el-transfer-panel) {
  width: 35%;
  height: 500px;
}

// .el-transfer-panel__list.is-filterable{
//     height: 400px;
// }

.moving {
  border-bottom: 1px solid #409eff;
}

.movingTop {
  border-top: 1px solid #409eff;
}

.movingBottom {
  border-bottom: 1px solid #409eff;
}

:deep(.el-drawer__header) {
  margin-bottom: 0;
}

.ci_data_table {
  // width:80%;
  // height: $mainHeight - $headerHeight;
  // flex: 1;
}

.footerButtonClass {
  display: flex;
  justify-content: end;
  gap: 15px;
}

// .common-layout {
//   display: flex;
//   gap: 10px;
//   justify-content: space-between;
// }
</style>
