// 点击防抖
const debounce = {
  bind: (el, binding) => {
    let throttleTime = binding.value // 防抖时间
    if (!throttleTime) { // 用户若不设置防抖时间，则默认1s
      throttleTime = 1000
    }
    let timer ;
    el.addEventListener('click',(e)=>{
        if(!timer){//首次执行
            timer = setTimeout(()=>{
                timer = null 
            },throttleTime)
        }else {
            e && e.stopPropagation();
        }
    },true)
  }
}



// 将函数作为默认导出
export default debounce