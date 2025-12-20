<template>
  <div class="ansible-cli-container">
    <!-- 左侧主机树 -->
    <div class="host-tree-panel">
      <!-- 添加过滤输入框 -->
      <div class="tree-filter">
        <el-input
          v-model="filterText"
          placeholder="输入关键字过滤节点"
          clearable
          size="default"
          :prefix-icon="Search"
        />
        <el-tooltip content="刷新资产树" placement="top">
          <el-button
            type="primary"
            :icon="Refresh"
            size="large"
            link
            @click="reloadTree()"
          ></el-button>
        </el-tooltip>
      </div>

      <el-tree-v2
        ref="treeRef"
        :data="treeData"
        show-checkbox
        default-expand-all
        node-key="id"
        highlight-current
        :props="defaultProps"
        :filter-method="filterNode"
        @check-change="handleCheckChange"
        :default-expanded-keys="branchNodeIds"
        :height="900"
      >
        <template #default="{ node, data }">
          <el-tooltip
            v-if="data.disabled"
            :content="data.disabledTooltip || '无法移除'"
            placement="top"
          >
            <span class="custom-tree-node">
              <el-icon
                class="node-icon"
                v-if="node.childNodes && node.childNodes.length > 0"
              >
                <Folder />
              </el-icon>
              <span :class="{ 'node-disabled': data.disabled }">{{
                node.label
              }}</span>
            </span>
          </el-tooltip>
          <span v-else class="custom-tree-node">
            <el-icon
              class="node-icon"
              v-if="node.childNodes && node.childNodes.length > 0"
            >
              <Folder />
            </el-icon>
            <span>{{ node.label }}</span>
          </span>
        </template>
      </el-tree-v2>
    </div>

    <!-- 右侧命令和结果区域 -->
    <div class="command-result-panel">
      <!-- 结果展示区域 -->
      <div class="result-display-area">
        <div class="result-header">
          <span>执行结果</span>
          <el-button
            type="danger"
            size="small"
            @click="clearResult"
            :disabled="executing"
          >
            清空
          </el-button>
        </div>
        <div class="result-content" ref="resultContentRef">
          <div v-if="!resultOutput.length" class="no-result">
            执行结果将在此处显示
          </div>
          <div
            v-for="(line, index) in resultOutput"
            :key="index"
            v-html="line"
            class="result-line"
          ></div>
        </div>
      </div>

      <!-- 模块选择和命令输入区域 -->
      <div class="command-input-area">
        <div class="command-header">
          <span>Ansible 命令执行</span>
          <el-button
            type="primary"
            size="small"
            @click="executeCommand"
            :loading="executing"
            :disabled="
              !selectedHosts.length ||
              !selectedModule ||
              executing ||
              (selectedModule !== 'ping' && !commandInput.length)
            "
          >
            执行
          </el-button>
          <!-- <el-button
            type="danger"
            size="small"
            @click="terminateCommand"
            :disabled="!executing"
          >
            终止
          </el-button> -->
        </div>

        <!-- 模块选择 -->
        <div class="module-selection">
          <el-select
            v-model="selectedModule"
            placeholder="请选择 Ansible 模块"
            filterable
            :disabled="executing"
            @change="onModuleChange"
            style="width: 200px"
          >
            <el-option-group
              v-for="group in ansibleModules"
              :key="group.label"
              :label="group.label"
            >
              <el-option
                v-for="item in group.options"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-option-group>
          </el-select>

          <el-button type="primary" link @click="showModuleDocs">
            查看文档
          </el-button>
        </div>

        <!-- 模块文档对话框 -->
        <el-dialog
          v-model="moduleDocsVisible"
          :title="`${docsModule} 模块文档`"
          width="70%"
          class="module-docs-dialog"
        >
          <div class="module-docs-header">
            <el-select
              v-model="docsModule"
              placeholder="请选择模块"
              filterable
              clearable
              style="width: 250px; margin-bottom: 20px"
            >
              <el-option-group
                v-for="group in ansibleModules"
                :key="group.label"
                :label="group.label"
              >
                <el-option
                  v-for="item in group.options"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-option-group>
            </el-select>
          </div>

          <div class="module-docs-content" v-if="currentDocsModuleData">
            <div class="module-description">
              <h3>描述</h3>
              <p>{{ currentDocsModuleData.description }}</p>
            </div>

            <div
              class="module-parameters"
              v-if="
                currentDocsModuleData.parameters &&
                Object.keys(currentDocsModuleData.parameters).length > 0
              "
            >
              <h3>参数</h3>
              <el-table :data="docsModuleParameters" border>
                <el-table-column prop="name" label="参数名" width="200" />
                <el-table-column prop="required" label="必需" width="80">
                  <template #default="scope">
                    <el-tag v-if="scope.row.required" type="danger">是</el-tag>
                    <el-tag v-else type="info">否</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="default" label="默认值" width="120">
                  <template #default="scope">
                    <span
                      v-if="
                        scope.row.default !== null &&
                        scope.row.default !== undefined
                      "
                      >{{ scope.row.default }}</span
                    >
                    <span v-else>-</span>
                  </template>
                </el-table-column>
                <el-table-column prop="choices" label="可选值" width="200">
                  <template #default="scope">
                    <el-tag
                      v-for="choice in scope.row.choices"
                      :key="choice"
                      size="small"
                      style="margin: 2px"
                    >
                      {{ choice }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="description" label="描述" />
              </el-table>
            </div>

            <div
              class="module-examples"
              v-if="
                currentDocsModuleData.examples &&
                currentDocsModuleData.examples.length > 0
              "
            >
              <h3>示例</h3>
              <div
                v-for="(example, index) in currentDocsModuleData.examples"
                :key="index"
                class="example-item"
              >
                <pre><code>{{ example }}</code></pre>
              </div>
            </div>
          </div>

          <div v-else class="no-docs">
            <p>请选择一个模块查看文档</p>
          </div>
        </el-dialog>

        <!-- 命令参数输入 -->
        <div class="command-input" v-if="selectedModule">
          <el-autocomplete
            v-model="commandInput"
            :fetch-suggestions="queryHistory"
            :placeholder="getCommandPlaceholder()"
            :disabled="executing || selectedModule === 'ping'"
            @keyup.enter="executeCommand"
            @keyup.up="navigateHistoryUp"
            @keyup.down="navigateHistoryDown"
            @select="handleSelectHistory"
            clearable
          />
        </div>
      </div>
    </div>
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
import { ElMessage } from "element-plus";
import AnsiToHtml from "ansi-to-html";
// import "@/assets/ansi-colors.css"; // 引入 ANSI CSS 类
const ansiConverter = new AnsiToHtml({ escapeXML: false });

import type {
  FilterNodeMethodFunction,
  TreeV2Instance,
  TreeNodeData,
} from "element-plus";
const { proxy } = getCurrentInstance();
const treeRef = ref<TreeV2Instance>();
const resultContentRef = ref();

import useModelStore from "@/store/cmdb/model";
import { Refresh, Search } from "@element-plus/icons-vue";
const modelConfigStore = useModelStore();
const hostsModelId = computed(
  () => modelConfigStore.modelObjectByName?.["hosts"]?.id
);
const hostModelCiDataObj = computed(
  () => modelConfigStore.allModelCiDataObj[hostsModelId.value]
);
defineOptions({ name: "ansibleCli" });
const filterText = ref("");
watch(filterText, (val) => {
  treeRef.value!.filter(val);
});

const filterNode = (query: string, node: TreeNodeData) =>
  node.label!.includes(query);

const currentChange = (data, obj) => {
  // console.log(data, obj);
};

// 添加历史记录相关数据
const commandHistory = ref([]);
const historyIndex = ref(-1);
const maxHistoryItems = ref(50); // 最大历史记录数
const saveHistory = () => {
  localStorage.setItem(
    "ansibleCommandHistory",
    JSON.stringify(commandHistory.value)
  );
};

// 添加命令到历史记录
const addToHistory = (command) => {
  if (!command) return;

  // 移除重复的命令
  const index = commandHistory.value.indexOf(command);
  if (index !== -1) {
    commandHistory.value.splice(index, 1);
  }

  // 添加到开头
  commandHistory.value.unshift(command);

  // 限制历史记录数量
  if (commandHistory.value.length > maxHistoryItems.value) {
    commandHistory.value = commandHistory.value.slice(0, maxHistoryItems.value);
  }

  // 保存到localStorage
  saveHistory();
};

// 查询历史记录（用于autocomplete）
const queryHistory = (queryString, callback) => {
  // 当输入为空时，不显示任何建议
  if (!queryString) {
    callback([]);
    return;
  }
  const results = queryString
    ? commandHistory.value.filter((item) => item.includes(queryString))
    : commandHistory.value.map((item) => ({ value: item }));

  callback(
    results.map((item) => (typeof item === "string" ? { value: item } : item))
  );
};

// 向上导航历史记录
const navigateHistoryUp = () => {
  if (commandHistory.value.length === 0) return;

  if (historyIndex.value < commandHistory.value.length - 1) {
    historyIndex.value++;
    commandInput.value = commandHistory.value[historyIndex.value];
  }
};

// 向下导航历史记录
const navigateHistoryDown = () => {
  if (historyIndex.value >= 0) {
    historyIndex.value--;
    commandInput.value =
      historyIndex.value >= 0 ? commandHistory.value[historyIndex.value] : "";
  }
};

// 处理从历史记录中选择
const handleSelectHistory = (item) => {
  commandInput.value = item.value;
};

// 选中的主机
const selectedHosts = ref([]);

// 选中的模块
const selectedModule = ref("shell");

// 命令输入
const commandInput = ref("");

// 执行状态
const executing = ref(false);

// 结果输出
const resultOutput = ref([]);

// WebSocket 连接
const socket = ref(null);

// 模块文档可见性
const moduleDocsVisible = ref(false);

// 文档对话框中选中的模块
const docsModule = ref("");

// AnsiUp 实例用于处理 ANSI 颜色代码
// const ansiUp = new AnsiUp();
// ansiUp.use_classes = true;
// 树属性配置
const defaultProps = {
  children: "children",
  label: "label",
};

// Ansible 模块列表
const ansibleModules = ref([
  {
    label: "常用模块",
    options: [
      { value: "shell", label: "shell - 执行 shell 命令" },
      { value: "command", label: "command - 执行命令" },
      { value: "ping", label: "ping - 测试主机连通性" },
      { value: "copy", label: "copy - 复制文件" },
      { value: "file", label: "file - 管理文件属性" },
      { value: "yum", label: "yum - 包管理" },
      { value: "service", label: "service - 管理服务" },
    ],
  },
  {
    label: "系统模块",
    options: [
      { value: "user", label: "user - 管理用户" },
      { value: "group", label: "group - 管理用户组" },
      { value: "cron", label: "cron - 管理定时任务" },
      { value: "hostname", label: "hostname - 管理主机名" },
      { value: "iptables", label: "iptables - 管理防火墙规则" },
    ],
  },
  {
    label: "文件模块",
    options: [
      { value: "template", label: "template - 模板文件" },
      { value: "lineinfile", label: "lineinfile - 管理文件行" },
      { value: "replace", label: "replace - 替换文件内容" },
      { value: "stat", label: "stat - 获取文件状态" },
      { value: "fetch", label: "fetch - 从远程节点获取文件" },
      { value: "synchronize", label: "synchronize - 同步文件" },
    ],
  },
  {
    label: "网络模块",
    options: [
      { value: "uri", label: "uri - 发起 HTTP 请求" },
      { value: "get_url", label: "get_url - 下载文件" },
    ],
  },
  {
    label: "软件包管理模块",
    options: [
      { value: "pip", label: "pip - Python 包管理" },
      { value: "npm", label: "npm - Node.js 包管理" },
    ],
  },
]);

// 模块文档数据（包含参数默认值和可选值）
const moduleDocs = ref({
  shell: {
    description:
      "在目标主机上执行 shell 命令，支持 shell 特性如管道、重定向等。",
    parameters: {
      _raw_params: {
        required: false,
        description: "要执行的命令（作为字符串传递）",
        default: null,
        choices: null,
      },
      chdir: {
        required: false,
        description: "执行命令前切换到的目录",
        default: null,
        choices: null,
      },
      creates: {
        required: false,
        description: "如果指定文件存在，则不执行命令",
        default: null,
        choices: null,
      },
      removes: {
        required: false,
        description: "如果指定文件不存在，则不执行命令",
        default: null,
        choices: null,
      },
      executable: {
        required: false,
        description: "用于执行命令的可执行文件",
        default: null,
        choices: null,
      },
      stdin: {
        required: false,
        description: "传递给命令的标准输入",
        default: null,
        choices: null,
      },
      warn: {
        required: false,
        description: "是否显示警告信息",
        default: true,
        choices: [true, false],
      },
    },
    examples: [
      "# 执行简单的命令\nansible webservers -m shell -a 'ls -l /tmp'",
      "# 切换目录后执行命令\nansible webservers -m shell -a 'chdir=/tmp ls -l'",
      "# 使用管道\nansible webservers -m shell -a 'ps aux | grep nginx'",
      "# 只有当文件不存在时才执行\nansible webservers -m shell -a 'creates=/tmp/app.pid /usr/local/bin/app &'",
    ],
  },
  command: {
    description: "在目标主机上执行命令，不支持 shell 特性如管道、重定向等。",
    parameters: {
      _raw_params: {
        required: false,
        description: "要执行的命令（作为字符串传递）",
        default: null,
        choices: null,
      },
      chdir: {
        required: false,
        description: "执行命令前切换到的目录",
        default: null,
        choices: null,
      },
      creates: {
        required: false,
        description: "如果指定文件存在，则不执行命令",
        default: null,
        choices: null,
      },
      removes: {
        required: false,
        description: "如果指定文件不存在，则不执行命令",
        default: null,
        choices: null,
      },
      stdin: {
        required: false,
        description: "传递给命令的标准输入",
        default: null,
        choices: null,
      },
      warn: {
        required: false,
        description: "是否显示警告信息",
        default: true,
        choices: [true, false],
      },
    },
    examples: [
      "# 执行简单的命令\nansible webservers -m command -a 'uptime'",
      "# 切换目录后执行命令\nansible webservers -m command -a 'chdir=/tmp pwd'",
      "# 只有当文件存在时才执行\nansible webservers -m command -a 'removes=/tmp/app.pid cat /tmp/app.pid'",
    ],
  },
  ping: {
    description: "测试目标主机的连通性，如果主机可达则返回 pong。",
    parameters: {
      data: {
        required: false,
        description: "返回给调用者的数据",
        default: "pong",
        choices: null,
      },
    },
    examples: [
      "# 测试所有主机连通性\nansible all -m ping",
      "# 测试并返回自定义数据\nansible all -m ping -a 'data=hello'",
    ],
  },
  copy: {
    description: "将文件从控制节点复制到目标主机。",
    parameters: {
      src: {
        required: false,
        description: "源文件路径（在控制节点上）",
        default: null,
        choices: null,
      },
      content: {
        required: false,
        description: "直接指定文件内容",
        default: null,
        choices: null,
      },
      dest: {
        required: true,
        description: "目标文件路径（在远程主机上）",
        default: null,
        choices: null,
      },
      backup: {
        required: false,
        description: "在覆盖前创建备份",
        default: false,
        choices: [true, false],
      },
      force: {
        required: false,
        description: "即使文件内容相同也强制复制",
        default: true,
        choices: [true, false],
      },
      mode: {
        required: false,
        description: "目标文件权限",
        default: null,
        choices: null,
      },
      owner: {
        required: false,
        description: "目标文件所有者",
        default: null,
        choices: null,
      },
      group: {
        required: false,
        description: "目标文件所属组",
        default: null,
        choices: null,
      },
      directory_mode: {
        required: false,
        description: "递归设置目录权限时使用的模式",
        default: null,
        choices: null,
      },
    },
    examples: [
      "# 复制文件\nansible webservers -m copy -a 'src=/etc/hosts dest=/tmp/hosts'",
      "# 直接指定文件内容\nansible webservers -m copy -a \"content='Hello World' dest=/tmp/test.txt\"",
      "# 复制文件并设置权限\nansible webservers -m copy -a 'src=/etc/hosts dest=/tmp/hosts mode=0644 owner=root group=root'",
    ],
  },
  file: {
    description: "管理目标主机上的文件属性，如创建目录、修改权限等。",
    parameters: {
      path: {
        required: true,
        description: "文件或目录路径",
        default: null,
        choices: null,
      },
      state: {
        required: false,
        description: "文件状态",
        default: "file",
        choices: ["file", "directory", "link", "hard", "touch", "absent"],
      },
      mode: {
        required: false,
        description: "文件权限",
        default: null,
        choices: null,
      },
      owner: {
        required: false,
        description: "文件所有者",
        default: null,
        choices: null,
      },
      group: {
        required: false,
        description: "文件所属组",
        default: null,
        choices: null,
      },
      recurse: {
        required: false,
        description: "递归设置目录属性",
        default: false,
        choices: [true, false],
      },
      src: {
        required: false,
        description: "符号链接指向的路径",
        default: null,
        choices: null,
      },
    },
    examples: [
      "# 创建目录\nansible webservers -m file -a 'path=/tmp/myapp state=directory mode=0755'",
      "# 修改文件权限\nansible webservers -m file -a 'path=/etc/foo.conf owner=foo group=foo mode=0644'",
      "# 创建符号链接\nansible webservers -m file -a 'src=/tmp/foo dest=/tmp/bar state=link'",
      "# 删除文件\nansible webservers -m file -a 'path=/tmp/foo state=absent'",
    ],
  },
  yum: {
    description: "使用 yum 包管理器管理软件包。",
    parameters: {
      name: {
        required: true,
        description: "软件包名称（可以是列表）",
        default: null,
        choices: null,
      },
      state: {
        required: false,
        description: "软件包状态",
        default: "present",
        choices: ["present", "installed", "latest", "absent", "removed"],
      },
      enablerepo: {
        required: false,
        description: "启用额外的仓库",
        default: null,
        choices: null,
      },
      disablerepo: {
        required: false,
        description: "禁用指定的仓库",
        default: null,
        choices: null,
      },
      conf_file: {
        required: false,
        description: "yum 配置文件路径",
        default: null,
        choices: null,
      },
      disable_gpg_check: {
        required: false,
        description: "禁用 GPG 检查",
        default: false,
        choices: [true, false],
      },
    },
    examples: [
      "# 安装软件包\nansible webservers -m yum -a 'name=nginx state=present'",
      "# 更新软件包到最新版本\nansible webservers -m yum -a 'name=nginx state=latest'",
      "# 删除软件包\nansible webservers -m yum -a 'name=nginx state=absent'",
      '# 安装多个软件包\nansible webservers -m yum -a \'name=["nginx", "mysql-server"] state=present\'',
    ],
  },
  service: {
    description: "管理服务（启动、停止、重启等）。",
    parameters: {
      name: {
        required: true,
        description: "服务名称",
        default: null,
        choices: null,
      },
      state: {
        required: false,
        description: "服务状态",
        default: null,
        choices: ["started", "stopped", "restarted", "reloaded"],
      },
      enabled: {
        required: false,
        description: "是否开机自启",
        default: null,
        choices: [true, false],
      },
      pattern: {
        required: false,
        description: "用于查找进程的模式",
        default: null,
        choices: null,
      },
      sleep: {
        required: false,
        description: "执行操作前等待的秒数",
        default: null,
        choices: null,
      },
    },
    examples: [
      "# 启动服务\nansible webservers -m service -a 'name=nginx state=started'",
      "# 停止服务\nansible webservers -m service -a 'name=nginx state=stopped'",
      "# 重启服务\nansible webservers -m service -a 'name=nginx state=restarted'",
      "# 设置服务开机自启\nansible webservers -m service -a 'name=nginx enabled=yes'",
      "# 重载服务配置\nansible webservers -m service -a 'name=nginx state=reloaded'",
    ],
  },
  user: {
    description: "管理用户账户。",
    parameters: {
      name: {
        required: true,
        description: "用户名",
        default: null,
        choices: null,
      },
      state: {
        required: false,
        description: "用户状态",
        default: "present",
        choices: ["present", "absent"],
      },
      uid: {
        required: false,
        description: "用户ID",
        default: null,
        choices: null,
      },
      group: {
        required: false,
        description: "用户主组",
        default: null,
        choices: null,
      },
      groups: {
        required: false,
        description: "用户附加组",
        default: null,
        choices: null,
      },
      home: {
        required: false,
        description: "用户家目录",
        default: null,
        choices: null,
      },
      shell: {
        required: false,
        description: "用户登录shell",
        default: null,
        choices: null,
      },
      password: {
        required: false,
        description: "用户密码（加密后的）",
        default: null,
        choices: null,
      },
      system: {
        required: false,
        description: "是否创建系统用户",
        default: false,
        choices: [true, false],
      },
    },
    examples: [
      "# 创建用户\nansible webservers -m user -a 'name=john'",
      "# 创建系统用户\nansible webservers -m user -a 'name=app system=yes'",
      "# 创建用户并设置家目录和shell\nansible webservers -m user -a 'name=john home=/home/john shell=/bin/bash'",
      "# 删除用户\nansible webservers -m user -a 'name=john state=absent'",
      "# 创建用户并设置密码\nansible webservers -m user -a 'name=john password=$6$....'",
    ],
  },
  group: {
    description: "管理用户组。",
    parameters: {
      name: {
        required: true,
        description: "组名",
        default: null,
        choices: null,
      },
      state: {
        required: false,
        description: "组状态",
        default: "present",
        choices: ["present", "absent"],
      },
      gid: {
        required: false,
        description: "组ID",
        default: null,
        choices: null,
      },
      system: {
        required: false,
        description: "是否创建系统组",
        default: false,
        choices: [true, false],
      },
    },
    examples: [
      "# 创建用户组\nansible webservers -m group -a 'name=developers'",
      "# 创建系统组\nansible webservers -m group -a 'name=app system=yes'",
      "# 删除用户组\nansible webservers -m group -a 'name=developers state=absent'",
    ],
  },
  cron: {
    description: "管理定时任务（crontab条目）。",
    parameters: {
      name: {
        required: true,
        description: "定时任务描述",
        default: null,
        choices: null,
      },
      state: {
        required: false,
        description: "定时任务状态",
        default: "present",
        choices: ["present", "absent"],
      },
      minute: {
        required: false,
        description: "分钟（0-59）",
        default: "*",
        choices: null,
      },
      hour: {
        required: false,
        description: "小时（0-23）",
        default: "*",
        choices: null,
      },
      day: {
        required: false,
        description: "日期（1-31）",
        default: "*",
        choices: null,
      },
      month: {
        required: false,
        description: "月份（1-12）",
        default: "*",
        choices: null,
      },
      weekday: {
        required: false,
        description: "星期（0-7，0和7都表示星期日）",
        default: "*",
        choices: null,
      },
      job: {
        required: false,
        description: "要执行的命令",
        default: null,
        choices: null,
      },
      user: {
        required: false,
        description: "拥有定时任务的用户",
        default: "root",
        choices: null,
      },
    },
    examples: [
      '# 创建定时任务\nansible webservers -m cron -a \'name="check dirs" minute=0 hour=5 job="ls -alh > /dev/null"\'',
      "# 删除定时任务\nansible webservers -m cron -a 'name=\"check dirs\" state=absent'",
      '# 创建每天执行的定时任务\nansible webservers -m cron -a \'name="daily backup" minute=30 hour=2 job="/usr/local/bin/backup.sh"\'',
    ],
  },
  hostname: {
    description: "管理系统主机名。",
    parameters: {
      name: {
        required: true,
        description: "主机名",
        default: null,
        choices: null,
      },
    },
    examples: [
      "# 设置主机名\nansible webservers -m hostname -a 'name=webserver01'",
      "# 设置主机名为特定值\nansible webservers -m hostname -a 'name=database01'",
    ],
  },
});

/**
 * 将 getCiModelTreeNode 返回的数据转换为树形选择器格式
 * @param {Array} treeData - getCiModelTreeNode 返回的数据
 * @returns {Array} 转换后的树形数据
 */
const convertToTreeFormat1 = (treeData) => {
  /**
   * 递归转换节点
   * @param {Object} node - 原始节点
   * @returns {Object} 转换后的节点
   */
  function convertNode(node) {
    const newNode = {
      id: node.id,
      label: node.label,
    };

    // 处理子节点
    if (node.children && node.children.length > 0) {
      newNode.children = node.children.map(convertNode);
    }

    // 处理实例作为叶子节点
    if (node.instances && node.instances.length > 0) {
      // 如果已经有children，需要合并
      if (!newNode.children) {
        newNode.children = [];
      }

      // 将instances转换为叶子节点并添加到children中
      const instanceNodes = node.instances.map((instance) => ({
        id: instance.id,
        label: instance.instance_name,
      }));

      newNode.children = [...newNode.children, ...instanceNodes];
    }

    return newNode;
  }

  // 处理根节点数组
  return treeData.map(convertNode);
};
// 在树数据声明附近添加分支节点ID的响应式变量
const treeData = ref([]);
const branchNodeIds = ref([]); // 存储所有分支节点的ID

// 修改convertToTreeFormat函数以使用响应式变量
const convertToTreeFormat = (data) => {
  // 重置分支节点ID数组
  branchNodeIds.value = [];

  /**
   * 递归转换节点
   * @param {Object} node - 原始节点
   * @returns {Object|null} 转换后的节点，如果应该被剔除则返回null
   */
  const convertNode = (node) => {
    const newNode = {
      id: node?.id,
      label: node.label,
    };

    // 处理子节点
    let validChildren = [];
    if (node.children && node.children.length > 0) {
      validChildren = node.children
        .map(convertNode)
        .filter((child) => child !== null);
    }

    // 处理实例
    let instanceNodes = [];
    if (node.instances && node.instances.length > 0) {
      // 将instances转换为叶子节点
      instanceNodes = node.instances.map((instance) => ({
        id: instance.id,
        label: instance.instance_name,
      }));
    }

    // 合并子节点和实例节点
    const allChildren = [...validChildren, ...instanceNodes];

    if (allChildren.length > 0) {
      newNode.children = allChildren;

      // 只有当节点有真正的子节点（而不是只有实例）时，才将其标记为分支节点
      // 这样可以确保只有包含子树的节点才会被记录为需要展开的节点
      if (validChildren.length > 0) {
        branchNodeIds.value.push(newNode.id);
      }
    } else if (
      (!node.instances || node.instances.length === 0) &&
      (!node.children || node.children.length === 0)
    ) {
      // 如果既没有子节点也没有实例，则剔除此节点
      return null;
    }

    return newNode;
  };

  // 处理根节点数组并过滤掉null节点
  const result = data.map(convertNode).filter((node) => node !== null);

  return result;
};

// 添加一个函数来展开所有分支节点
const expandAllBranchNodes = () => {
  // 这个函数可以在树组件中使用，用来展开所有分支节点
  // 具体实现取决于您使用的树组件
  console.log("Branch node IDs to expand:", branchNodeIds.value);
  return branchNodeIds.value;
};

// 处理选中变化
const handleCheckChange = (data, checked, indeterminate) => {
  // 获取所有选中的叶子节点
  const checkedKeys = treeRef.value.getCheckedKeys();
  // 过滤出选中的叶子节点
  selectedHosts.value = allNodes.value
    .filter((node) => checkedKeys.includes(node.id))
    .map((item) => item.id);
  // console.log(selectedHosts.value);
};

const allNodes = computed(() => getAllLeafNodes(treeData.value));

// 获取所有叶子节点
const getAllLeafNodes = (nodes) => {
  let leafNodes = [];

  nodes.forEach((node) => {
    // 如果节点有子节点，递归查找
    if (node.children && node.children.length > 0) {
      leafNodes = leafNodes.concat(getAllLeafNodes(node.children));
    } else {
      // 如果没有子节点，则为叶子节点
      leafNodes.push(node);
    }
  });

  return leafNodes;
};

// 当模块改变时
const onModuleChange = () => {
  commandInput.value = "";
};

// 获取文档对话框中选中的模块数据
const currentDocsModuleData = computed(() => {
  return moduleDocs.value[docsModule.value] || null;
});

// 获取文档对话框中选中的模块参数列表
const docsModuleParameters = computed(() => {
  if (!currentDocsModuleData.value || !currentDocsModuleData.value.parameters)
    return [];

  return Object.keys(currentDocsModuleData.value.parameters).map((key) => ({
    name: key,
    ...currentDocsModuleData.value.parameters[key],
  }));
});

// 显示模块文档
const showModuleDocs = () => {
  // 如果当前已选中模块，则默认显示该模块的文档
  if (selectedModule.value) {
    docsModule.value = selectedModule.value;
  }
  moduleDocsVisible.value = true;
};

// 获取命令输入框的占位符
const getCommandPlaceholder = () => {
  if (!selectedModule.value) return "请先选择 Ansible 模块";
  if (selectedModule.value === "ping") return "无需输入参数";
  const moduleDoc = moduleDocs.value[selectedModule.value];
  if (moduleDoc && moduleDoc.examples && moduleDoc.examples.length > 0) {
    return `请输入 ${selectedModule.value} 模块的参数，例如: ${
      moduleDoc.examples[0].split("-a ")[1] || "参数"
    }`;
  }
  return `请输入 ${selectedModule.value} 模块的参数`;
};

// 执行命令
const executeCommand = async () => {
  if (!selectedHosts.value.length) {
    ElMessage.warning("请至少选择一个主机");
    return;
  }

  if (!selectedModule.value) {
    ElMessage.warning("请选择要执行的 Ansible 模块");
    return;
  }
  // 判断选择的节点数，如果超过200，则拒绝执行，提示
  if (selectedHosts.value.length > 200) {
    ElMessage.warning("选择的节点数超过200，请选择少一点");
    return;
  }
  const commandToExecute = commandInput.value;

  // 添加到历史记录（除非是ping模块，因为它不需要参数）
  if (selectedModule.value !== "ping") {
    addToHistory(commandToExecute);
  }

  // 重置历史索引
  historyIndex.value = -1;

  // 设置执行状态
  executing.value = true;
  resultOutput.value = [];

  try {
    // 建立 WebSocket 连接
    socket.value = new WebSocket(
      `${window.location.protocol === "https:" ? "wss" : "ws"}://${
        window.location.host
      }/jobflow/ws/ansible/`
    );

    socket.value.onopen = () => {
      // 发送命令到后端，包含模块信息
      socket.value.send(
        JSON.stringify({
          module: selectedModule.value,
          module_args: commandInput.value,
          hosts: selectedHosts.value,
        })
      );
    };

    socket.value.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "output") {
        addResultLine(data.message);
      } else if (data.type === "complete") {
        executing.value = false;
        addResultLine(
          `\n命令执行完成，返回码: ${data.returncode}，执行时长: ${data.execution_time}s`
        );
        socket.value.close();
      } else if (data.type === "error") {
        executing.value = false;
        addResultLine(`错误: ${data.message}`, "error");
      }
    };

    socket.value.onerror = (error) => {
      executing.value = false;
      addResultLine(`WebSocket 错误: ${error.message}`, "error");
    };

    socket.value.onclose = () => {
      console.log("命令执行已结束", "warning");
      executing.value = false;
    };
  } catch (error) {
    console.error("执行命令时出错:", error);
    executing.value = false;
    addResultLine(`错误: ${error.message}`, "error");
  } finally {
    executing.value = false;
  }
};

// 终止命令执行
const terminateCommand = () => {
  if (socket.value && socket.value.readyState === WebSocket.OPEN) {
    // 发送终止指令到后端
    socket.value.send(
      JSON.stringify({
        type: "terminate",
      })
    );
    executing.value = false;
    addResultLine("正在终止命令执行...", "warning");
  } else {
    executing.value = false;
    addResultLine("命令执行已终止", "warning");
  }
};

// 根据 ID 查找节点
const findNodeById = (nodes, id) => {
  for (const node of nodes) {
    if (node.id === id) {
      return node;
    }
    if (node.children) {
      const found = findNodeById(node.children, id);
      if (found) return found;
    }
  }
  return null;
};

// 添加结果行
const addResultLine = (text, type = "") => {
  // 使用 ansiUp 处理 ANSI 颜色代码
  if (text === "" || text === null || text === undefined) return;
  // 忽略WARNING
  if (text.includes("[WARNING]: Platform")) return;
  const htmlText = ansiConverter.toHtml(text);
  resultOutput.value.push(htmlText);

  // 限制显示行数，避免内存占用过大
  // if (resultOutput.value.length > 1000) {
  //   resultOutput.value.shift();
  // }

  // 实时滚动到底部
  scrollToBottom();
};

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (resultContentRef.value) {
      resultContentRef.value.scrollTop = resultContentRef.value.scrollHeight;
    }
  });
};

// 清空结果
const clearResult = () => {
  resultOutput.value = [];
};

// 获取主机模型
const hostModel = ref(null);
const getCiModel = async () => {
  let res = await proxy.$api.getCiModel({
    name: "hosts",
  });
  hostModel.value = res.data.results[0];
};

// 获取主机树数据
const getHostTreeData = async () => {
  console.log(hostModel.value);
  let res = await proxy.$api.getCiModelTreeNode({
    model: hostModel.value?.id,
  });
  treeData.value = convertToTreeFormat(res.data);
};
const reloadTree = async () => {
  // await modelConfigStore.getModel(true);
  await modelConfigStore.getAllModelTreeInstances(true);
};
watch(hostModelCiDataObj, (val) => {
  treeData.value = convertToTreeFormat([hostModelCiDataObj.value]);
});

onMounted(async () => {
  const savedHistory = localStorage.getItem("ansibleCommandHistory");
  if (savedHistory) {
    commandHistory.value = JSON.parse(savedHistory);
  }
  await modelConfigStore.getModel();
  await modelConfigStore.getAllModelTreeInstances();
  nextTick(() => {
    treeData.value = convertToTreeFormat([hostModelCiDataObj.value]);
    // treeRef.value!.setExpandedKeys(branchNodeIds.value);
  });
});

onUnmounted(() => {
  // 组件销毁时关闭 WebSocket 连接
  if (socket.value) {
    socket.value.close();
  }
});
</script>

<style scoped lang="scss">
.ansible-cli-container {
  flex: 1;
  display: flex;
  height: 100%;
  width: 100%;
  // padding: 10px;
  box-sizing: border-box;
}
.tree-filter {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}
.host-tree-panel {
  flex: 0 0 250px;
  background: var(--el-bg-color);
  border-radius: 4px;
  padding: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow-x: auto; /* 启用水平滚动 */
  overflow-y: auto; /* 启用垂直滚动 */
  margin-right: 10px;
  :deep(.el-vl__window) {
    overflow: inherit !important;
  }
}

// .el-tree-v2 {
//   display: inline-block;
// }
/* 确保树节点内容可以超出容器宽度 */
.host-tree-panel :deep(.el-tree) {
  min-width: fit-content; /* 确保树的最小宽度适应内容 */
}

.host-tree-panel :deep(.el-tree-node__content) {
  white-space: nowrap; /* 防止内容换行 */
}

.host-tree-panel :deep(.el-tree-node__label) {
  white-space: nowrap; /* 防止标签文本换行 */
  padding-right: 10px; /* 添加右边距以确保可读性 */
}

.command-result-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.command-input-area {
  flex: 0 0 auto;
  background: var(--el-bg-color);
  border-radius: 4px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.command-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-weight: bold;
  font-size: 16px;
}

.module-selection {
  display: flex;
  gap: 10px;
  align-items: center;
}

// .module-selection .el-select {
//   flex: 1;
// }

.command-input {
  flex: 1;
}

.result-display-area {
  flex: 1;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  margin-bottom: 10px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--el-bg-color);
  padding: 10px 15px;
  border-bottom: 1px solid #eee;
  font-weight: bold;
  font-size: 16px;
}

.result-content {
  flex: 1;
  height: 0; /* 使 flex 元素正确计算高度 */
  padding: 10px 15px;
  overflow-y: auto;
  font-family: "Courier New", monospace;
  background-color: #000;
  color: #fff;
  white-space: pre-wrap;
}

.result-line {
  margin-bottom: 2px;
  line-height: 1.4;
  font-size: large;
}

.no-result {
  color: #888;
  text-align: center;
  margin-top: 20px;
}

.module-docs-dialog :deep(.el-dialog__body) {
  max-height: 60vh;
  overflow-y: auto;
}

.module-docs-content h3 {
  margin: 15px 0 10px 0;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 5px;
}

.example-item {
  margin-bottom: 10px;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.example-item pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.choices-preview {
  cursor: pointer;
  color: #409eff;
}

.choices-list {
  max-height: 200px;
  overflow-y: auto;
}

.no-docs {
  text-align: center;
  color: #999;
  padding: 20px;
}
.node-icon {
  margin-right: 5px;
  width: 16px;
  height: 16px;
  color: #909399;
}
</style>