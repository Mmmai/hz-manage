import{n as qe}from"./nearLogCom-DsviBRhk.js";import{u as Ie}from"./tabs-B5ZD239g.js";import{d as Oe,r as u,b as $e,a as De,M as X,aN as Ee,e as s,b3 as Ve,o as m,f as j,h as v,g as t,w as l,j as n,aG as R,t as _,bO as Ae,O as g,F as Y,b1 as Ue,P as Me,k as Be,_ as We}from"./index-DbTZdHLp.js";const ze={class:"card"},Ke={class:"cell-item"},je={class:"cell-item"},Ge={class:"cell-item"},Pe={class:"cell-item"},He={class:"cell-item"},Je={class:"cell-item"},Qe={class:"cell-item"},Xe={style:{display:"inline-flex","align-items":"center"}},Ye={style:{display:"inline-flex","align-items":"center"}},Ze=["innerHTML"],el={class:"operation_show"},ll=Oe({__name:"logFlowInfoView",setup(tl){const{proxy:f}=Be(),Z=Ie(),L=u(!0);u([1,2,3,4,5]);const y=$e(),ee=De(),C=u(!0),le=u("default"),te=()=>{ee.push({name:"logFlowMission"}),console.log(y.fullPath),Z.removeTabs(y.fullPath,!1)},E=u(!1),q=u(""),G=u(""),ae=async a=>{E.value=!0;let e=await f.$api.dataSourceGet(M.value);q.value=e.data.url,G.value.showNearLog(q.value,a)},V=u(""),c=u({}),I=u([]),x=u([]),N=u(""),A=u(""),U=u(""),M=u(""),B=u(""),p=u({level:"info",status:"运行中"}),oe=async a=>{let e=f.$commonFunc.timestampToDate(a.dateValue[0]),r=f.$commonFunc.timestampToDate(a.dateValue[1]);x.value.push(e),x.value.push(r),N.value=a.matchKey,V.value=a.username,A.value=a.dataSourceName,M.value=a.dataSourceId,U.value=a.flowName,B.value=a.missionId;let d=await f.$api.getFlowLokiLog(a);if(console.log(d),d)if(d.status==200)p.value.level="success",p.value.status="成功",L.value=!1;else return L.value=!1,p.value.level="danger",p.value.status="异常",!1;else return p.value.level="danger",p.value.status="异常",L.value=!1,!1;c.value=d.data.info,I.value=d.data.sort,f.$nextTick(()=>{})},b=X(()=>{const a={large:"8px",default:"6px",small:"4px"};return{marginRight:a[le.value]||a.default}}),S=u({}),se=X(()=>{let a=[];return I.value.forEach(e=>{if(console.log(e),c.value[e].status&&c.value[e].queryResult.length>>>0)var r=!1;else var r=!0;a.push({label:S.value[e].module_name,value:e,disabled:r})}),a}),ne=async()=>{let a=await f.$api.getLogModule();a==null||a.data.results.forEach(e=>{S.value[e.id]=e}),console.log(S.value)},ue=(a,e)=>{let r=S.value[a].module_name,d=[];e.queryResult.forEach(i=>{d.push(`${i.logTime},${i.level},${i.logLine}
`)});let T=f.$commonFunc.getCurrentTimeString("-","-","_",":",":");f.$commonFunc.downloadArray(`${r}-export-log-${T}`,d)},re=(a,e)=>{W.value=!0,$.value=a},O=u([]),ie=a=>{console.log(a.stream),O.value=[],Object.keys(a.stream).forEach(e=>{let r={};r.label=e,r.value=a.stream[e],O.value.push(r)}),console.log(O.value)},de=async()=>{let a=y.path.split("/").filter(i=>i!="");a[a.length-1],console.log(y.query.mission_id);let e=await f.$api.getLogFlowMission(y.query.mission_id);console.log(e);let r=e.data.mission_query;e.data.status=="Success"?(p.value.level="success",p.value.status="成功"):e.data.status=="Failed"?(p.value.level="danger",p.value.status="失败"):(p.value.level="info",p.value.status="未知");let d=f.$commonFunc.timestampToDate(r.dateValue[0]),T=f.$commonFunc.timestampToDate(r.dateValue[1]);x.value.push(d),x.value.push(T),N.value=e.data.task_id,V.value=e.data.username,B.value=e.data.mission_id,A.value=e.data.dataSource_name,U.value=e.data.flow_name,M.value=e.data.dataSource_id,c.value=e.data.results.info,I.value=e.data.results.sort,console.log(c.value),L.value=!1};Ee(async()=>{ne(),y.query.missionId?await oe(y.query):de()});const ce=a=>a.status?a.queryInfo.errorCount==0&&a.queryResult.length>>0?"日志正常":a.queryInfo.errorCount>>0&&a.queryResult.length>>0?"存在报错":"无请求信息":"请求错误",pe=a=>a.status?a.queryInfo.errorCount==0&&a.queryResult.length>>0?"success":a.queryInfo.errorCount>>0&&a.queryResult.length>>0?"warning":"danger":"danger",W=u(!1),$=u(""),ve=(a,e)=>{if(e){const r=new RegExp(e,"gi");return a.replace(r,'<span style="background-color: #FFFF00;">$&</span>')}else return a},fe=[{text:"DEBUG",value:"DEBUG"},{text:"INFO",value:"INFO"},{text:"WARN",value:"WARN"},{text:"ERROR",value:"ERROR"},{text:"FATAL",value:"FATAL"},{text:"UNKNOWN",value:"UNKNOWN"}],me=(a,e)=>e.level===a;return(a,e)=>{const r=s("el-button"),d=s("el-tooltip"),T=s("Back"),i=s("el-icon"),_e=s("user"),w=s("el-descriptions-item"),ge=s("iphone"),ye=s("location"),z=s("tickets"),k=s("el-tag"),be=s("office-building"),we=s("el-descriptions"),ke=s("el-divider"),he=s("el-result"),P=s("Warning"),H=s("el-statistic"),D=s("el-space"),K=s("el-link"),Re=s("el-card"),xe=s("Right"),Ne=s("el-scrollbar"),Fe=s("el-segmented"),h=s("el-table-column"),J=s("el-table"),Le=s("el-drawer"),Se=s("Top"),Te=s("el-backtop"),Ce=Ve("loading");return m(),j(Y,null,[v("div",ze,[t(Ne,null,{default:l(()=>[t(we,{class:"margin-top",title:"查询条件",column:4,border:""},{extra:l(()=>[t(d,{content:"切换流程是否换行显示",placement:"top"},{default:l(()=>[t(r,{type:"primary",onClick:e[0]||(e[0]=o=>C.value?C.value=!1:C.value=!0)},{default:l(()=>e[6]||(e[6]=[n("切换")])),_:1})]),_:1}),t(d,{content:"返回任务列表",placement:"top"},{default:l(()=>[t(r,{type:"primary",onClick:te},{default:l(()=>[t(i,null,{default:l(()=>[t(T)]),_:1})]),_:1})]),_:1})]),default:l(()=>[t(w,null,{label:l(()=>[v("div",Ke,[t(i,{style:R(b.value)},{default:l(()=>[t(_e)]),_:1},8,["style"]),e[7]||(e[7]=n(" 查询用户 "))])]),default:l(()=>[n(" "+_(V.value),1)]),_:1}),t(w,null,{label:l(()=>[v("div",je,[t(i,{style:R(b.value)},{default:l(()=>[t(ge)]),_:1},8,["style"]),e[8]||(e[8]=n(" 请求ID "))])]),default:l(()=>[n(" "+_(B.value),1)]),_:1}),t(w,null,{label:l(()=>[v("div",Ge,[t(i,{style:R(b.value)},{default:l(()=>[t(ye)]),_:1},8,["style"]),e[9]||(e[9]=n(" 时间范围 "))])]),default:l(()=>[n(" "+_(x.value[0])+" - "+_(x.value[1]),1)]),_:1}),t(w,null,{label:l(()=>[v("div",Pe,[t(i,{style:R(b.value)},{default:l(()=>[t(z)]),_:1},8,["style"]),e[10]||(e[10]=n(" 任务状态 "))])]),default:l(()=>[t(k,{type:p.value.level},{default:l(()=>[n(_(p.value.status),1)]),_:1},8,["type"])]),_:1}),t(w,null,{label:l(()=>[v("div",He,[t(i,{style:R(b.value)},{default:l(()=>[t(z)]),_:1},8,["style"]),e[11]||(e[11]=n(" 数据源 "))])]),default:l(()=>[n(" "+_(A.value),1)]),_:1}),t(w,null,{label:l(()=>[v("div",Je,[t(i,{style:R(b.value)},{default:l(()=>[t(z)]),_:1},8,["style"]),e[12]||(e[12]=n(" 业务流 "))])]),default:l(()=>[n(" "+_(U.value),1)]),_:1}),t(w,null,{label:l(()=>[v("div",Qe,[t(i,{style:R(b.value)},{default:l(()=>[t(be)]),_:1},8,["style"]),e[13]||(e[13]=n(" 分析ID "))])]),default:l(()=>[n(" "+_(N.value),1)]),_:1})]),_:1}),t(ke,null,{default:l(()=>e[14]||(e[14]=[n(" 分析结果 ")])),_:1}),Ae((m(),g(D,{wrap:C.value,size:10},{default:l(()=>[(m(!0),j(Y,null,Ue(I.value,(o,F)=>(m(),j("div",{key:F,style:{width:"100%",heigth:"320px",display:"flex","align-items":"center"}},[t(Re,{class:"result-card"},{header:l(()=>[v("span",null,"环节"+_(F+1)+": "+_(S.value[o].module_name),1)]),footer:l(()=>[t(D,{style:{width:"100%",justifyContent:"flex-end"}},{default:l(()=>[t(K,{type:"primary",onClick:Q=>ue(o,c.value[o]),disabled:c.value[o].queryResult.length===0},{default:l(()=>e[17]||(e[17]=[n("下载日志")])),_:2},1032,["onClick","disabled"]),t(K,{type:"primary",onClick:Q=>re(o,c.value[o]),disabled:c.value[o].queryResult.length===0},{default:l(()=>e[18]||(e[18]=[n("查看日志")])),_:2},1032,["onClick","disabled"])]),_:2},1024)]),default:l(()=>[t(D,{wrap:"",size:50},{default:l(()=>[t(he,{icon:pe(c.value[o]),title:ce(c.value[o])},null,8,["icon","title"]),t(D,{direction:"vertical"},{default:l(()=>[t(H,{value:c.value[o].queryResult.length},{title:l(()=>[v("div",Xe,[e[15]||(e[15]=n(" 匹配数 ")),t(d,{effect:"dark",content:"分析ID返回的日志条数",placement:"top"},{default:l(()=>[t(i,{style:{"margin-left":"4px"},size:12},{default:l(()=>[t(P)]),_:1})]),_:1})])]),_:2},1032,["value"]),t(H,{value:c.value[o].queryInfo.errorCount},{title:l(()=>[v("div",Ye,[e[16]||(e[16]=n(" 错误数 ")),t(d,{effect:"dark",content:"匹配到的日志中,日志等级为ERROR及以上的数量",placement:"top"},{default:l(()=>[t(i,{style:{"margin-left":"4px"},size:12},{default:l(()=>[t(P)]),_:1})]),_:1})])]),_:2},1032,["value"])]),_:2},1024)]),_:2},1024)]),_:2},1024),Object.keys(c.value).length!==F+1?(m(),g(i,{key:0},{default:l(()=>[t(xe)]),_:1})):Me("",!0)]))),128))]),_:1},8,["wrap"])),[[Ce,L.value]])]),_:1})]),t(Le,{modelValue:W.value,"onUpdate:modelValue":e[2]||(e[2]=o=>W.value=o),size:"80%",class:"drawer"},{header:l(()=>[t(Fe,{modelValue:$.value,"onUpdate:modelValue":e[1]||(e[1]=o=>$.value=o),options:se.value},null,8,["modelValue","options"])]),default:l(()=>[t(J,{data:c.value[$.value].queryResult,style:{width:"98%"},onExpandChange:ie,"default-sort":{prop:"logTime",order:"descending"}},{default:l(()=>[t(h,{type:"expand"},{default:l(o=>[t(J,{data:O.value,border:"","show-header":!1},{default:l(()=>[t(h,{fixed:"left",label:"Operations",width:"45"},{default:l(F=>[t(r,{icon:a.Filter,link:"",type:"primary",size:"small",onClick:Q=>a.addLabelToFilter(F.row)},null,8,["icon","onClick"])]),_:1}),t(h,{label:"label",prop:"label",width:"120px"}),t(h,{label:"value",prop:"value"})]),_:1},8,["data"])]),_:1}),t(h,{label:"日志时间",prop:"logTime",sortable:"",width:"200px"}),t(h,{label:"日志等级",prop:"level",width:"100px",filters:fe,"filter-method":me,"filter-placement":"bottom-end"},{default:l(o=>[o.row.level=="DEBUG"?(m(),g(k,{key:0,type:"primary",effect:"light"},{default:l(()=>e[19]||(e[19]=[n("DEBUG")])),_:1})):o.row.level=="INFO"?(m(),g(k,{key:1,type:"success",effect:"light"},{default:l(()=>e[20]||(e[20]=[n("INFO")])),_:1})):o.row.level=="WARN"?(m(),g(k,{key:2,type:"warning",effect:"light"},{default:l(()=>e[21]||(e[21]=[n("WARN")])),_:1})):o.row.level=="ERROR"?(m(),g(k,{key:3,type:"danger",effect:"light"},{default:l(()=>e[22]||(e[22]=[n("ERROR")])),_:1})):o.row.level=="FATAL"?(m(),g(k,{key:4,type:"danger",effect:"light"},{default:l(()=>e[23]||(e[23]=[n("FATAL")])),_:1})):(m(),g(k,{key:5,type:"info",effect:"light"},{default:l(()=>e[24]||(e[24]=[n("UNKNOWN")])),_:1}))]),_:1}),t(h,{label:"日志内容",prop:"logLine"},{default:l(({row:o})=>[v("span",{innerHTML:ve(o.logLine,N.value)},null,8,Ze),v("div",el,[t(K,{type:"primary",onClick:F=>ae(o)},{default:l(()=>e[25]||(e[25]=[n("查看上下文 ")])),_:2},1032,["onClick"])])]),_:1})]),_:1},8,["data"])]),footer:l(()=>e[26]||(e[26]=[v("div",{style:{flex:"auto"}},null,-1)])),_:1},8,["modelValue"]),t(Te,{bottom:50},{default:l(()=>[t(i,null,{default:l(()=>[t(Se)]),_:1})]),_:1}),t(qe,{isShow:E.value,"onUpdate:isShow":e[3]||(e[3]=o=>E.value=o),highlightKey:N.value,"onUpdate:highlightKey":e[4]||(e[4]=o=>N.value=o),url:q.value,"onUpdate:url":e[5]||(e[5]=o=>q.value=o),ref_key:"childRef",ref:G},null,8,["isShow","highlightKey","url"])],64)}}}),nl=We(ll,[["__scopeId","data-v-bd0dc79d"]]);export{nl as default};
