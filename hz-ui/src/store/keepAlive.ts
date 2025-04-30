import { ref, computed } from 'vue'

import { defineStore } from "pinia";
// import { KeepAliveState } from "@/stores/interface";

export const useKeepAliveStore = defineStore(
  "keepalive",

  () => {
    const keepAliveName = ref([])
    // Add KeepAliveName
    const addKeepAliveName = async (name: string) => {
      !keepAliveName.value.includes(name) && keepAliveName.value.push(name);
    }
    // Remove KeepAliveName
    const removeKeepAliveName = async (name: string) => {
      keepAliveName.value = keepAliveName.value.filter(item => item !== name);
    }
    // Set KeepAliveName
    const setKeepAliveName = async (keepaliveName: []) => {
      keepAliveName.value = keepaliveName;
    }
    return { keepAliveName, addKeepAliveName, removeKeepAliveName, setKeepAliveName }
  }, {
  persist: true

}
);
export default useKeepAliveStore