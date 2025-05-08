// 创建自定义指令
import useClipboard from 'vue-clipboard3';
import { Directive, DirectiveBinding } from 'vue';
import { ElMessage } from "element-plus";
const clipboard = useClipboard();

const copyDirective: Directive = {
  mounted(el: HTMLElement, binding: DirectiveBinding) {
    el.addEventListener('click', async () => {
      const text = binding.value;
      try {
        await clipboard.toClipboard(text);

        ElMessage({
          message: '已复制到剪贴板',
          type: 'success',
        })
      } catch (e) {
        // console.error('复制失败', e);
        ElMessage.error("复制失败")
      }
    });
  }
};

export default copyDirective;