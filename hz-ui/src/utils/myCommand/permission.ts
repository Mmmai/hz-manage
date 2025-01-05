import  { Directive, DirectiveBinding,inject  } from 'vue'
// import { useRoutesStore } from '@/store/modules/routes'
// import { BUTTON_PERMISSION_MAP } from '@/constants/button-permission'
// import { useStore } from "vuex";
import store from "@/store/index"
const permission: Directive = {
  mounted(el: HTMLElement, binding: DirectiveBinding): void {
    const { value } = binding
    console.log(value)
    if (!value)
      return

    // 可根据自己的业务修改此处实现逻辑
    if (store.state.permission.includes(value)){

        el.style.display = 'auto'
    }
    else{
        el.style.display = 'none'


    }
  },
}
 
export default permission