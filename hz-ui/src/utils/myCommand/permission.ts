import { Directive, DirectiveBinding, inject } from 'vue'
// import { useRoutesStore } from '@/store/modules/routes'
// import { BUTTON_PERMISSION_MAP } from '@/constants/button-permission'
// import { useStore } from "vuex";
import store from "@/store/index"
const permission: Directive = {
  mounted(el: HTMLElement, binding: DirectiveBinding): void {
    // console.log(el)
    // console.log(binding)
    const { value } = binding
    if (!value)
      return
    if (typeof value === "string") {
      if (store.state.permission.includes(value)) {

        el.style.display = 'auto'
      }
      else {
        el.style.display = 'none'
      }
    } else if (typeof value === "object") {

      if (!store.state.permission.includes(value.id)) {
        el.classList.add("is-disabled")
      }
    }
    // 可根据自己的业务修改此处实现逻辑

  },
}

export default permission