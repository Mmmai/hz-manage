import{_ as R,a as A,r as i,M as Q,aN as T,e as s,o as u,f as C,g as t,w as o,h as k,j as _,bO as q,O as w,F as H,b1 as J,aG as K,t as f,P as W,bQ as X,bo as Y,k as Z}from"./index-8aBZIOBx.js";import{s as I}from"./vue-draggable-plus-akWe7VLL.js";const ee={class:"card"},te={style:{"font-size":"20px","font-weight":"bold",width:"200px"}},oe={__name:"favoritesView",setup(ae){const{proxy:x}=Z(),V=A(),L=()=>{V.push({name:"portal"})},m=i(["所有"]),z=i([]),c=i("所有"),U=async()=>{let a=await x.$api.pgroupGet();z.value=a.data.results,m.value=["所有"],a.data.results.forEach(e=>{m.value.push(e.group)})},p=i([]),G=async()=>{let a=await x.$api.portalGet();p.value=a.data.results},N=a=>{let e=0;for(let n=0;n<a.length;n++)e=a.charCodeAt(n)+((e<<5)-e);let d="#";for(let n=0;n<3;n++){let v=e>>n*8&255;d+=("00"+v.toString(16)).slice(-2)}return d},P=a=>{window.open(a.url,"_blank")},r=i(""),B=Q(()=>p.value.filter(a=>{let e=!0;return c.value==="所有"?(e=!0,r.value===""?e=!0:e=a.name.toLowerCase().includes(r.value.toLowerCase())):(e=a.group_name.includes(c.value),e&&(r.value===""?e=!0:e=a.name.toLowerCase().includes(r.value.toLowerCase()))),e})),D=a=>{c.value=a};T(()=>{console.log(99999),G(),U()});const $=()=>{console.log(p.value)};return(a,e)=>{const d=s("el-segmented"),n=s("el-col"),v=s("el-input"),b=s("el-link"),h=s("el-row"),F=s("el-divider"),M=s("el-avatar"),O=s("el-text"),y=s("el-tooltip"),g=s("el-space"),S=s("el-card"),j=s("el-scrollbar");return u(),C("div",ee,[t(j,null,{default:o(()=>[t(h,{justify:"space-between"},{default:o(()=>[t(n,{span:18,class:"group-class"},{default:o(()=>[e[2]||(e[2]=k("span",{style:{display:"flex","align-items":"center","margin-right":"10px"}},"分组",-1)),t(d,{modelValue:c.value,"onUpdate:modelValue":e[0]||(e[0]=l=>c.value=l),options:m.value,size:"large"},null,8,["modelValue","options"])]),_:1}),t(n,{span:4},{default:o(()=>[t(v,{modelValue:r.value,"onUpdate:modelValue":e[1]||(e[1]=l=>r.value=l),style:{width:"200px"},placeholder:"过滤器",clearable:""},null,8,["modelValue"])]),_:1}),t(n,{span:1},{default:o(()=>[t(b,{type:"primary",onClick:L},{default:o(()=>e[3]||(e[3]=[_("添加")])),_:1})]),_:1})]),_:1}),t(F),q((u(),w(g,{wrap:"",size:30},{default:o(()=>[(u(!0),C(H,null,J(B.value,(l,le)=>(u(),w(S,{key:l.id,class:"box-card",style:{width:"300px",height:"120px"},shadow:"hover",onClick:E=>P(l)},{default:o(()=>[t(y,{class:"box-item",effect:"light",content:l.url,placement:"bottom"},{default:o(()=>[t(g,{direction:"vertical",alignment:"end"},{default:o(()=>[t(h,null,{default:o(()=>[t(n,{span:8},{default:o(()=>[t(M,{style:K({"background-color":N(l.id+l.name),"font-size":"28px"}),size:60},{default:o(()=>[_(f(l.name.slice(0,1).toUpperCase()),1)]),_:2},1032,["style"])]),_:2},1024),t(n,{span:12},{default:o(()=>[t(g,{direction:"vertical"},{default:o(()=>[k("span",te,f(l.name),1),l.describe!==""?(u(),w(y,{key:0,class:"box-item",effect:"light",content:l.describe,placement:"bottom"},{default:o(()=>[t(O,{class:"describe-class",type:"info"},{default:o(()=>[_(f(l.describe),1)]),_:2},1024)]),_:2},1032,["content"])):W("",!0)]),_:2},1024)]),_:2},1024)]),_:2},1024),t(b,{type:"info",onClick:X(E=>D(l.group_name),["stop"])},{default:o(()=>[_(f(l.group_name),1)]),_:2},1032,["onClick"])]),_:2},1024)]),_:2},1032,["content"])]),_:2},1032,["onClick"]))),128))]),_:1})),[[Y(I),[p.value,{animation:150,onUpdate:$}]]])]),_:1})])}}},re=R(oe,[["__scopeId","data-v-749234fa"]]);export{re as default};