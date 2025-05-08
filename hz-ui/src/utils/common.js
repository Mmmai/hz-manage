// import {callback} from 'vue'

const pageFunc = (dataArr,pageConfig) =>{ 
  let sindex = 0+pageConfig.size*(pageConfig.page - 1 )
  let eindex = pageConfig.size + sindex
  let res = dataArr.slice(sindex,eindex)
  return res

}
// 导出
const downloadFunc = (res) => {
  let lines = res.split('\n');
  console.log(1111)
  console.log(lines)
  if (navigator.userAgent.indexOf('Windows') !== -1) {
    // 如果是Windows系统，使用`\r\n`作为换行符
    lines = lines.map(line => line + '\r\n');
  }
  const content = lines.join('');
  var blob = content.data;
  //  FileReader主要用于将文件内容读入内存
  var reader = new FileReader();
  reader.readAsDataURL(blob);
  // onload当读取操作成功完成时调用
  reader.onload = function(e) {
    var a = document.createElement('a');
    // 获取文件名fileName
    let contentDisposition = res.headers['content-disposition'];
    // fileName必用这种方式进行解析，否则乱码
    let fileName = window.decodeURI(contentDisposition.substring(contentDisposition.indexOf('=')+1));
    // var fileName = res.headers["content-disposition"].split("=");
    // fileName = fileName[fileName.length - 1];
    // fileName = fileName.replace(/"/g, "");
    console.log(fileName)
    a.download = fileName;
    a.href = e.target.result;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }
}
const testr = () =>{
  let contentDisposition = response.headers['content-disposition'];
  // fileName必用这种方式进行解析，否则乱码
  let fileName = window.decodeURI(contentDisposition.substring(contentDisposition.indexOf('=')+1));
  console.log('fileName=' + fileName);
  let url = window.URL.createObjectURL(new Blob([data]));
  let a = document.createElement('a');
  a.style.display = 'none';
  a.href = url;
  a.setAttribute('download',fileName);
  document.body.appendChild(a);
  //点击下载
  a.click();
  // 下载完成移除元素
  document.body.removeChild(a);
  // 释放掉blob对象
  window.URL.revokeObjectURL(url);
  console.log("下载完成");
 
}
// 防抖函数
const debounceFunc = (fn,wait=500) => {
  let timer
  return function() {
    let context = this
    let args = arguments
    if (timer) clearTimeout(timer)
    timer = setTimeout(()=>{
      fn.apply(context,args)
    },wait)
  }
}
// 节流
const throttle = (func, wait=1000) =>{
  let timer; // 定义一个计时器变量，用于限制函数调用频率
  return function (...args) { // 返回一个包装后的函数
      const context = this; // 保存函数执行上下文对象
      if (!timer) { // 如果计时器不存在
          func.apply(context, args); // 执行函数
          timer = setTimeout(() => {
            timer = null; // 清空计时器变量
          }, wait); // 创建计时器，在指定时间后重置计时器变量
      }
  };
}
// 将数组导出
//res.value.code 数据源
//type：格式设置
//form.name是下载文件的自定义名字
const downloadArray = (fileName,exportArray)=>{

  let result = exportArray
  const blob = new Blob(result, { type: 'text/txt' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${fileName}.txt`;
  link.click();
  URL.revokeObjectURL(url);
}
// 当前时间字符串
const getCurrentTimeString = (ym='-',md='-',dh=' ',hm=':',ms=':') => {
  var now = new Date();
  var year = now.getFullYear();
  var month = now.getMonth() + 1; // 月份是从0开始的
  var day = now.getDate();
  var hours = now.getHours();
  var minutes = now.getMinutes();
  var seconds = now.getSeconds();

  // 格式化月份、日期、小时、分钟、秒
  month = (month < 10 ? "0" : "") + month;
  day = (day < 10 ? "0" : "") + day;
  hours = (hours < 10 ? "0" : "") + hours;
  minutes = (minutes < 10 ? "0" : "") + minutes;
  seconds = (seconds < 10 ? "0" : "") + seconds;

  // 组合为YYYY-MM-DD HH:MM:SS格式的字符串
  return year + ym + month + md + day + dh + hours + hm + minutes + ms + seconds;
}
// 时间戳转字符串
const timestampToDate = (timeValue)=>{
  const timestamp = Number(timeValue);
  const date = new Date(timestamp);
  const formattedDate = date.toLocaleString();
  return formattedDate
}
// UUID
const getUuid = ()=> {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
      var r = Math.random() * 16 | 0,
          v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
  });
}

const validateRegexp = (regexp,rule, value, callback) => {
  const pattern = new RegExp(regexp)
  if (value === '' || value === undefined || value == null) {
    callback()
  } else {
    if ((!pattern.test(value)) && value !== '') {
      callback(new Error('正则不匹配!'))
    } else {
      callback()
    }
  }
}
const hasDuplicates = (array) => {
  return new Set(array).size !== array.length;
}
// 模板下载
import axios from '../utils/request'

const downloadFile = async(fileUrl,params)=>{
    try {
      const response = await axios({
        url: fileUrl, // 替换为你的文件 URL
        method: 'POST',
        data:params,
        responseType: 'blob' // 确保响应是 Blob 类型
      });
      console.log(response)
      // 创建一个 URL 对象
      const url = window.URL.createObjectURL(new Blob([response.data],{type: response.data.type}));
      
      // 创建一个 <a> 元素并下载
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', response.headers['content-disposition'].split('"')[1]); // 替换为你希望的文件名
      document.body.appendChild(link);
      link.click();
      link.remove(); // 下载后移除链接元素
    } catch (error) {
      console.error('下载文件失败', error); // 捕获并输出错误信息
    }
  }



export default {
  pageFunc,
  downloadFunc,
  debounceFunc,
  throttle,
  downloadArray,
  getCurrentTimeString,
  getUuid,
  timestampToDate,
  validateRegexp,
  hasDuplicates,
  downloadFile
}