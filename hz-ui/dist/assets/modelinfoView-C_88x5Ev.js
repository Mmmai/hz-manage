import{i as ol}from"./iconSelectCom-Bq-vr7TL.js";import{d as Ne,aB as al,u as Se,b as Te,bu as sl,r as i,M as ce,c as fe,e as d,b3 as je,o as g,f as G,h as R,g as e,w as t,F as H,b1 as te,O as j,j as C,t as oe,bO as M,bQ as Ge,bo as x,b$ as Je,c0 as Ae,P as Ee,aE as nl,bF as pe,c3 as b,bV as ve,aD as ke,k as Le,_ as Pe,a as dl,bI as ul,aN as il,aS as rl,aI as ml}from"./index-8aBZIOBx.js";import{I as pl}from"./iconify-CbyDCU2R.js";import{u as cl}from"./tabs-DnJE1Zmi.js";const fl={class:"operation_show"},vl={class:"dialog-footer"},_l={class:"demo-drawer__content"},bl={style:{float:"left"}},gl={style:{float:"right",color:"var(--el-text-color-secondary)","font-size":"13px"}},yl={class:"demo-drawer__footer"},wl=Ne({__name:"ciModelField",props:{ciModelInfo:{},ciModelInfoModifiers:{}},emits:al(["getModelField"],["update:ciModelInfo"]),setup(Ve,{expose:Q,emit:ae}){const{proxy:w}=Le(),L=Se(),k=Te(),B=ae,X=sl(Ve,"ciModelInfo"),Y=i([]),J=i([]),F=i([]),z=ce(()=>{let o=[];return Y.value.forEach(l=>{l.fields.forEach(m=>{m.type==="model_ref"&&o.push(m.ref_model)})}),o}),se=ce(()=>{var l;let o=[];return(l=F.value)==null||l.forEach(m=>{m.id!==X.value.id&&(z.value.indexOf(m.id)===-1?o.push({value:m.id,label:m.verbose_name,disabled:!1}):o.push({value:m.id,label:m.verbose_name,disabled:!0}))}),o}),ne=()=>{s.default="",s.validation_rule="",s.type=="boolean"?s.default=!0:s.type=="enum"?c.value=!0:s.type=="string"&&(c.value=!1)},D=i([]),q=o=>{let l=JSON.parse(A.value[o].rule),m=[];Object.keys(l).forEach(p=>{m.push({value:p,label:l[p]})}),D.value=m},K=o=>{let l=JSON.parse(A.value[o].rule),m=[];Object.keys(l).forEach(p=>{m.push({value:p,label:l[p]})}),D.value=m,s.default!=D.value[0].value&&(s.default=D.value[0].value)},c=i(!1),de=ce(()=>s.type==="fromModel"),_e=i([]),Z=async(o=null)=>{let l=await w.$api.getValidationRules({page:1,page_size:1e4,...o});_e.value=l.data.results,l.data.results.forEach(m=>{A.value[m.id]=m})},A=i({}),v=ce(()=>{let o=[];return _e.value.forEach(l=>{l.field_type==s.type&&o.push({value:l.id,label:l.verbose_name})}),o}),n=async()=>{let o=await w.$api.getCiModel(k.query,k.query.id);X.value=o.data.model,Y.value=o.data.field_groups;let l=[];Y.value.forEach((m,p)=>{var ie;J.value.push(m.verbose_name),(ie=m.fields)==null||ie.forEach(Ue=>{l.push(Ue)})}),B("getModelField",l)},O=i([]),V=i([]);Q({getModelField:n,getCiModelList:async()=>{let o=await w.$api.getCiModel();F.value=o.data.results},getRules:Z,getModelFieldType:async()=>{let o=await w.$api.getCiModelFieldType(),l=o.data.field_types;Object.keys(l).forEach(m=>{O.value.push({value:m,label:l[m]})}),V.value=o.data.limit_fields}});const h=fe({name:"",verbose_name:""}),r=(o,l,m)=>{console.log(l),V.value.includes(l)?m(new Error(`${V.value.join(",")}不能用!`)):m()},u=fe({name:[{required:!0,message:"请输入唯一标识",trigger:"blur"},{pattern:/^[a-z][\w\d]{4,20}$/,trigger:"blur",message:"以英文字符开头,可以使用英文,数字,下划线,长度4-20 "}],verbose_name:[{required:!0,message:"请输入组名称",trigger:"blur"}]}),U=i(),$=i(!1),ge=o=>{$.value=!1,le(o)},ee=i(!1),W=i(""),_=async o=>{o&&await o.validate(async(l,m)=>{if(l)if(ee.value){console.log(h);let p=await w.$api.addCiModelFieldGroup({model:X.value.id,create_user:L.state.username,update_user:L.state.username,...h});console.log(p),p.status=="201"?(b({type:"success",message:"添加成功"}),$.value=!1,le(o),n()):b({showClose:!0,message:"添加失败:"+JSON.stringify(p.data),type:"error"})}else{let p=await w.$api.updateCiModelFieldGroup({id:W.value,update_user:L.state.username,...h});console.log(p),p.status=="200"?(b({type:"success",message:"更新成功"}),$.value=!1,le(o),n()):b({showClose:!0,message:"更新失败:"+JSON.stringify(p.data),type:"error"})}else console.log("error submit!",m)})},N=o=>{ve.confirm("是否确认关闭?").then(()=>{o(),le(U.value)}).catch(()=>{})},E=i("新增"),ye=o=>{E.value="新增",ke(()=>{}),$.value=!0,ee.value=!0},xe=o=>{E.value="修改",$.value=!0,ke(()=>{ee.value=!1,h.name=o.name,h.verbose_name=o.verbose_name,W.value=o.id})},Oe=o=>{ve.confirm("是否确认删除?","删除组",{confirmButtonText:"确认删除",cancelButtonText:"取消",type:"warning",draggable:!0}).then(async()=>{let l=await w.$api.deleteCiModelFieldGroup(o);l.status==204||l.status==200?(b({type:"success",message:"删除成功"}),await n()):b({type:"error",message:"删除失败"})}).catch(()=>{b({type:"info",message:"取消删除"})})},P=i(!1),s=fe({name:"",verbose_name:"",type:"string",required:!1,editable:!0,validation_rule:"",ref_model:"",description:"",default:"",unit:""}),Re=fe({name:[{required:!0,message:"请输入唯一标识",trigger:"blur"},{pattern:/^[a-z][\w\d]{1,20}$/,trigger:"blur",message:"以英文字符开头,可以使用英文,数字,下划线,长度2-20 ",required:!0},{validator:r,trigger:"blur"}],verbose_name:[{required:!0,message:"请输入字段显示名称",trigger:"blur"}],type:[{required:!0,message:"字段类型",trigger:"blur"}],model_name:[{required:de,message:"请选择模型",trigger:"blur"}],validation_rule:[{required:c,message:"选择校验规则",trigger:""}]}),ue=i();i(!1);const f=i(!1),S=i({}),Ce=i(!0),He=o=>{P.value=!0,E.value="修改",f.value=!0,S.value=o,Ce.value=!1,ke(()=>{Object.keys(o).forEach(l=>{s.hasOwnProperty(l)&&(s[l]=o[l])}),s.validation_rule===null?c.value=!1:c.value=!0})},Qe=o=>{le(o),console.log(s),P.value=!1},Ke=o=>{E.value="新增",S.value={},P.value=!0,Ce.value=!0,f.value=!1,c.value=!1,ke(()=>{W.value=o.id})},We=async o=>{o&&await o.validate(async(l,m)=>{if(l)if(Ce.value){let p=await w.$api.addCiModelField({model:X.value.id,model_field_group:W.value,create_user:L.state.username,update_user:L.state.username,...s});console.log(p),p.status=="201"?(b({type:"success",message:"添加成功"}),P.value=!1,le(o),n()):b({showClose:!0,message:"添加失败:"+JSON.stringify(p.data),type:"error"})}else{c.value||(s.validation_rule="");let p=await w.$api.updateCiModelField({id:S.value.id,update_user:L.state.username,...s});console.log(p),p.status=="200"?(b({type:"success",message:"更新成功"}),P.value=!1,le(o),n()):b({showClose:!0,message:"更新失败:"+JSON.stringify(p.data),type:"error"})}else console.log("error submit!",m)})},Xe=o=>{ve.confirm("是否确认关闭?").then(()=>{o(),le(ue.value),P.value=!1}).catch(()=>{})},Ye=o=>{ve.confirm("是否确认删除?","删除组",{confirmButtonText:"确认删除",cancelButtonText:"取消",type:"warning",draggable:!0}).then(async()=>{(await w.$api.deleteCiModelField(S.value.id)).status==204?(b({type:"success",message:"删除成功"}),await n(),le(ue.value),P.value=!1):b({type:"error",message:"删除失败"})}).catch(()=>{b({type:"info",message:"取消删除"})})},le=o=>{o&&o.resetFields()};return(o,l)=>{const m=d("el-text"),p=d("el-button"),ie=d("el-tooltip"),Ue=d("el-space"),qe=d("el-col"),Be=d("el-row"),ze=d("el-card"),Ze=d("el-collapse-item"),el=d("el-collapse"),we=d("el-input"),T=d("el-form-item"),De=d("el-form"),ll=d("el-dialog"),Ie=d("el-switch"),Fe=d("el-option"),Me=d("el-select"),tl=d("el-drawer"),me=je("permission");return g(),G(H,null,[R("div",null,[e(el,{modelValue:J.value,"onUpdate:modelValue":l[0]||(l[0]=y=>J.value=y)},{default:t(()=>[(g(!0),G(H,null,te(Y.value,(y,$e)=>(g(),j(Ze,{name:y.verbose_name,key:$e},{title:t(()=>[e(m,{tag:"b",size:"large"},{default:t(()=>[C(oe(y.verbose_name),1)]),_:2},1024),R("div",fl,[y.built_in?Ee("",!0):(g(),j(Ue,{key:0},{default:t(()=>{var a;return[M((g(),j(ie,{class:"box-item",effect:"dark",content:"编辑",placement:"top"},{default:t(()=>{var I;return[M(e(p,{size:"small",onClick:Ge(he=>xe(y),["stop"]),icon:x(Je),circle:""},null,8,["onClick","icon"]),[[me,`${(I=x(k).name)==null?void 0:I.replace("_info","")}:edit`]])]}),_:2},1024)),[[me,`${(a=x(k).name)==null?void 0:a.replace("_info","")}:edit`]]),e(ie,{class:"box-item",effect:"dark",content:"删除",placement:"top"},{default:t(()=>{var I;return[M(e(p,{size:"small",onClick:Ge(he=>Oe(y.id),["stop"]),icon:x(Ae),circle:""},null,8,["onClick","icon"]),[[me,`${(I=x(k).name)==null?void 0:I.replace("_info","")}:delete`]])]}),_:2},1024)]}),_:2},1024))])]),default:t(()=>[R("div",null,[e(Ue,{wrap:"",size:10,alignment:"flex-start"},{default:t(()=>{var a;return[(g(!0),G(H,null,te(y.fields,(I,he)=>(g(),G("div",{key:he},[e(ie,{effect:"light",content:"点击编辑字段",placement:"top"},{default:t(()=>[e(ze,{shadow:"hover",class:nl(["modelFieldCard",I.built_in?"isBuiltClass":""]),onClick:Ol=>He(I)},{default:t(()=>[e(m,{tag:"b"},{default:t(()=>[C(oe(I.verbose_name),1)]),_:2},1024),e(Be,{justify:"space-between"},{default:t(()=>[e(ie,{class:"box-item",effect:"light",content:I.name,placement:"bottom"},{default:t(()=>[e(qe,{span:13,class:"describe-class"},{default:t(()=>[e(m,null,{default:t(()=>[C(oe(I.name),1)]),_:2},1024)]),_:2},1024)]),_:2},1032,["content"]),e(ie,{class:"box-item",effect:"light",content:I.type,placement:"bottom"},{default:t(()=>[e(qe,{span:10,class:"describe-class"},{default:t(()=>[e(m,null,{default:t(()=>[C(oe(I.type),1)]),_:2},1024)]),_:2},1024)]),_:2},1032,["content"])]),_:2},1024)]),_:2},1032,["class","onClick"])]),_:2},1024)]))),128)),R("div",null,[M((g(),j(ze,{class:"modelFieldCard",style:{"align-items":"center","justify-content":"center"},onClick:I=>Ke(y)},{default:t(()=>[e(m,{type:"primary"},{default:t(()=>l[26]||(l[26]=[C("+ 添加字段")])),_:1})]),_:2},1032,["onClick"])),[[me,`${(a=x(k).name)==null?void 0:a.replace("_info","")}:add`]])])]}),_:2},1024)])]),_:2},1032,["name"]))),128))]),_:1},8,["modelValue"]),e(Be,{style:{"margin-top":"10px"}},{default:t(()=>[e(qe,null,{default:t(()=>{var y;return[M((g(),j(p,{bg:"",text:"",onClick:l[1]||(l[1]=$e=>ye(X.value))},{default:t(()=>l[27]||(l[27]=[C("添加分组")])),_:1})),[[me,`${(y=x(k).name)==null?void 0:y.replace("_info","")}:add`]])]}),_:1})]),_:1})]),e(ll,{modelValue:$.value,"onUpdate:modelValue":l[6]||(l[6]=y=>$.value=y),title:E.value+"字段分组",width:"500","before-close":N},{footer:t(()=>[R("div",vl,[e(p,{onClick:l[4]||(l[4]=y=>ge(U.value))},{default:t(()=>l[28]||(l[28]=[C("取消")])),_:1}),e(p,{type:"primary",onClick:l[5]||(l[5]=y=>_(U.value))},{default:t(()=>l[29]||(l[29]=[C(" 确认 ")])),_:1})])]),default:t(()=>[e(De,{ref_key:"groupFormRef",ref:U,style:{"max-width":"600px"},model:h,rules:u,"label-width":"auto",class:"demo-modelForm","status-icon":""},{default:t(()=>[e(T,{label:"字段组标识",prop:"name"},{default:t(()=>[e(we,{modelValue:h.name,"onUpdate:modelValue":l[2]||(l[2]=y=>h.name=y),disabled:!ee.value},null,8,["modelValue","disabled"])]),_:1}),e(T,{label:"字段分组名称",prop:"verbose_name"},{default:t(()=>[e(we,{modelValue:h.verbose_name,"onUpdate:modelValue":l[3]||(l[3]=y=>h.verbose_name=y)},null,8,["modelValue"])]),_:1})]),_:1},8,["model","rules"])]),_:1},8,["modelValue","title"]),e(tl,{modelValue:P.value,"onUpdate:modelValue":l[25]||(l[25]=y=>P.value=y),title:"模型字段","before-close":Xe,direction:"rtl",class:"demo-drawer"},{default:t(()=>{var y,$e;return[R("div",_l,[e(De,{model:s,ref_key:"modelFieldFormRef",ref:ue,"label-width":"auto","label-position":"right",rules:Re},{default:t(()=>[e(T,{label:"唯一标识",prop:"name"},{default:t(()=>[e(we,{modelValue:s.name,"onUpdate:modelValue":l[7]||(l[7]=a=>s.name=a),autocomplete:"off",disabled:!!(S.value.built_in||f.value)},null,8,["modelValue","disabled"])]),_:1}),e(T,{label:"显示名称",prop:"verbose_name"},{default:t(()=>[e(we,{modelValue:s.verbose_name,"onUpdate:modelValue":l[8]||(l[8]=a=>s.verbose_name=a),autocomplete:"off"},null,8,["modelValue"])]),_:1}),e(T,{label:"可编辑",prop:"editable"},{default:t(()=>[e(Ie,{modelValue:s.editable,"onUpdate:modelValue":l[9]||(l[9]=a=>s.editable=a),style:{"--el-switch-on-color":"#13ce66","--el-switch-off-color":"#ff4949"},disabled:S.value.built_in},null,8,["modelValue","disabled"])]),_:1}),e(T,{label:"必填",prop:"required"},{default:t(()=>[e(Ie,{modelValue:s.required,"onUpdate:modelValue":l[10]||(l[10]=a=>s.required=a),style:{"--el-switch-on-color":"#13ce66","--el-switch-off-color":"#ff4949"}},null,8,["modelValue"])]),_:1}),e(T,{label:"字段类型",prop:"type"},{default:t(()=>[e(Me,{modelValue:s.type,"onUpdate:modelValue":l[11]||(l[11]=a=>s.type=a),placeholder:"Select",style:{width:"240px"},onChange:ne,disabled:!!(S.value.built_in||f.value)},{default:t(()=>[(g(!0),G(H,null,te(O.value,a=>(g(),j(Fe,{key:a.value,label:a.label,value:a.value},{default:t(()=>[R("span",bl,oe(a.label),1),R("span",gl,oe(a.value),1)]),_:2},1032,["label","value"]))),128))]),_:1},8,["modelValue","disabled"])]),_:1}),M(e(T,{label:"校验规则",prop:"validation_rule"},{default:t(()=>[e(Ie,{modelValue:c.value,"onUpdate:modelValue":l[12]||(l[12]=a=>c.value=a),style:{"--el-switch-on-color":"#13ce66","--el-switch-off-color":"#ff4949","margin-right":"10px"}},null,8,["modelValue"]),M(e(Me,{modelValue:s.validation_rule,"onUpdate:modelValue":l[13]||(l[13]=a=>s.validation_rule=a),placeholder:"选择校验规则",style:{width:"240px"}},{default:t(()=>[(g(!0),G(H,null,te(v.value,a=>(g(),j(Fe,{key:a.value,label:a.label,value:a.value},null,8,["label","value"]))),128))]),_:1},8,["modelValue"]),[[pe,c.value]])]),_:1},512),[[pe,s.type==="string"]]),M(e(T,{label:"枚举值",prop:"validation_rule"},{default:t(()=>[e(Me,{modelValue:s.validation_rule,"onUpdate:modelValue":l[14]||(l[14]=a=>s.validation_rule=a),placeholder:"选择校验规则",style:{width:"240px"},onChange:l[15]||(l[15]=a=>K(s.validation_rule))},{default:t(()=>[(g(!0),G(H,null,te(v.value,a=>(g(),j(Fe,{key:a.value,label:a.label,value:a.value},null,8,["label","value"]))),128))]),_:1},8,["modelValue"])]),_:1},512),[[pe,s.type==="enum"]]),M(e(T,{label:"默认值",prop:"default"},{default:t(()=>[e(Me,{modelValue:s.default,"onUpdate:modelValue":l[16]||(l[16]=a=>s.default=a),placeholder:"选择默认值",size:"large",onVisibleChange:l[17]||(l[17]=a=>q(s.validation_rule))},{default:t(()=>[(g(!0),G(H,null,te(D.value,(a,I)=>(g(),j(Fe,{key:I,label:a.label,value:a.value},null,8,["label","value"]))),128))]),_:1},8,["modelValue"])]),_:1},512),[[pe,s.type==="enum"]]),M(e(T,{label:"模型引用",prop:"ref_model"},{default:t(()=>[e(Me,{modelValue:s.ref_model,"onUpdate:modelValue":l[18]||(l[18]=a=>s.ref_model=a),placeholder:"选择CI模型",disabled:!!(S.value.built_in||f.value)},{default:t(()=>[(g(!0),G(H,null,te(se.value,a=>(g(),j(Fe,{key:a.value,label:a.label,disabled:a.disabled,value:a.value},null,8,["label","disabled","value"]))),128))]),_:1},8,["modelValue","disabled"])]),_:1},512),[[pe,s.type==="model_ref"]]),M(e(T,{label:"默认值",prop:"default"},{default:t(()=>[e(Ie,{modelValue:s.default,"onUpdate:modelValue":l[19]||(l[19]=a=>s.default=a),style:{"--el-switch-on-color":"#13ce66","--el-switch-off-color":"#ff4949"}},null,8,["modelValue"])]),_:1},512),[[pe,s.type==="boolean"]]),M(e(T,{label:"单位",prop:"unit"},{default:t(()=>[e(we,{modelValue:s.unit,"onUpdate:modelValue":l[20]||(l[20]=a=>s.unit=a),style:{width:"120px"}},null,8,["modelValue"])]),_:1},512),[[pe,s.type==="integer"||s.type==="float"]]),e(T,{label:"描述",prop:"description"},{default:t(()=>[e(we,{modelValue:s.description,"onUpdate:modelValue":l[21]||(l[21]=a=>s.description=a),type:"textarea"},null,8,["modelValue"])]),_:1})]),_:1},8,["model","rules"]),R("div",yl,[e(p,{onClick:l[22]||(l[22]=a=>Qe(ue.value))},{default:t(()=>l[30]||(l[30]=[C("取消")])),_:1}),f.value&&!S.value.built_in?M((g(),j(p,{key:0,type:"danger",onClick:l[23]||(l[23]=a=>Ye())},{default:t(()=>l[31]||(l[31]=[C("删除")])),_:1})),[[me,`${(y=x(k).name)==null?void 0:y.replace("_info","")}:delete`]]):Ee("",!0),M((g(),j(p,{type:"primary",onClick:l[24]||(l[24]=a=>We(ue.value))},{default:t(()=>l[32]||(l[32]=[C(" 确定 ")])),_:1})),[[me,`${($e=x(k).name)==null?void 0:$e.replace("_info","")}:edit`]])])])]}),_:1},8,["modelValue"])],64)}}}),Vl=Pe(wl,[["__scopeId","data-v-40577b9b"]]),Cl={style:{width:"100%"}},Fl={class:"table-header"},Ml={class:"header-button-lf"},$l={class:"dialog-footer"},kl=Ne({__name:"ciModelUnique",props:["modelId","modelFieldLists"],setup(Ve,{expose:Q}){const ae=Te(),{proxy:w}=Le(),L=Se(),k=i([]),B=Ve,X=()=>{console.log(B.modelFieldLists),z.value=!0,ne.value=!0},Y=ce(()=>{let v={};return B.modelFieldLists.forEach(n=>{v[n.name]=n.verbose_name}),v}),J=i(""),F=fe({fields:[],validate_null:!1,description:null}),z=i(!1),se=()=>{z.value=!1,K(J.value),console.log(F)},ne=i(!0),D=i({}),q=v=>{D.value=v,z.value=!0,ne.value=!1,ke(()=>{Object.keys(v).forEach(n=>{n!=="id"&&Object.keys(F).indexOf(n)!==-1&&(F[n]=v[n])})})},K=v=>{v&&(console.log(F),v.resetFields(),D.value={},console.log(F))},c=async v=>{await v.validate(async(n,O)=>{if(n)if(ne.value){let V=await w.$api.addCiModelUnique({create_user:L.state.username,update_user:L.state.username,...F,model:B.modelId});V.status=="201"?(b({type:"success",message:"添加成功"}),z.value=!1,K(v),A({model:B.modelId})):b({showClose:!0,message:"添加失败:"+JSON.stringify(V.data),type:"error"})}else{let V=await w.$api.updateCiModelUnique({id:D.value.id,update_user:L.state.username,...F});console.log(V),V.status=="200"?(b({type:"success",message:"更新成功"}),z.value=!1,K(v),A({model:B.modelId})):b({showClose:!0,message:"更新失败:"+JSON.stringify(V.data),type:"error"})}})},de=async v=>{let n=await w.$api.updateCiModelUnique({update_user:L.state.username,...v});n.status=="200"?(b({type:"success",message:"更新成功"}),K(J.value),A({model:B.modelId})):b({showClose:!0,message:"更新失败:"+JSON.stringify(n.data),type:"error"})},_e=v=>{ve.confirm("是否确认删除?","删除",{confirmButtonText:"确认删除",cancelButtonText:"取消",type:"warning",draggable:!0}).then(async()=>{(await w.$api.deleteCiModelUnique(v)).status==204?(b({type:"success",message:"删除成功"}),A({model:B.modelId}),K(J.value),z.value=!1):b({type:"error",message:"删除失败"})}).catch(()=>{b({type:"info",message:"取消删除"})})},Z=ce(()=>{let v={};return k.value.forEach(n=>{var V;let O=n.fields.map(re=>Y.value[re]);v[(V=n.fields)==null?void 0:V.join("+")]=O.join("+")}),v}),A=async v=>{let n=await w.$api.getCiModelUnique(v);k.value=n.data.results};return Q({getTableData:A}),(v,n)=>{const O=d("el-button"),V=d("el-table-column"),re=d("el-switch"),be=d("el-tooltip"),h=d("el-table"),r=d("el-option"),u=d("el-select"),U=d("el-form-item"),$=d("el-input"),ge=d("el-form"),ee=d("el-dialog"),W=je("permission");return g(),G("div",Cl,[R("div",Fl,[R("div",Ml,[e(O,{type:"primary",onClick:X},{default:t(()=>n[5]||(n[5]=[C("添加")])),_:1})])]),e(h,{ref:"multipleTableRef",data:k.value,style:{width:"100%"},border:""},{default:t(()=>[e(V,{prop:"fields",label:"校验规则"},{default:t(_=>[R("span",null,oe(Z.value[_.row.fields.join("+")]),1)]),_:1}),e(V,{prop:"validate_null",label:"空值校验"},{default:t(_=>{var N;return[M(e(re,{modelValue:_.row.validate_null,"onUpdate:modelValue":E=>_.row.validate_null=E,class:"ml-2",style:{"--el-switch-on-color":"#13ce66","--el-switch-off-color":"#ff4949"},onChange:E=>de({id:_.row.id,validate_null:_.row.validate_null}),disabled:_.row.built_in},null,8,["modelValue","onUpdate:modelValue","onChange","disabled"]),[[W,{id:`${(N=x(ae).name)==null?void 0:N.replace("_info","")}:edit`,action:"disabled"}]])]}),_:1}),e(V,{prop:"description",label:"描述"}),e(V,{fixed:"right",width:"100",label:"操作"},{default:t(_=>[e(be,{class:"box-item",effect:"dark",content:"编辑",placement:"top"},{default:t(()=>{var N;return[M(e(O,{link:"",type:"primary",icon:x(Je),onClick:E=>q(_.row)},null,8,["icon","onClick"]),[[W,`${(N=x(ae).name)==null?void 0:N.replace("_info","")}:edit`]])]}),_:2},1024),e(be,{class:"box-item",effect:"dark",content:"删除",placement:"top"},{default:t(()=>{var N;return[M(e(O,{link:"",type:"danger",icon:x(Ae),disabled:_.row.built_in,onClick:E=>_e(_.row.id)},null,8,["icon","disabled","onClick"]),[[W,`${(N=x(ae).name)==null?void 0:N.replace("_info","")}:delete`]])]}),_:2},1024)]),_:1})]),_:1},8,["data"]),e(ee,{modelValue:z.value,"onUpdate:modelValue":n[4]||(n[4]=_=>z.value=_),title:"唯一校验配置",width:"500","before-close":se},{footer:t(()=>[R("div",$l,[e(O,{onClick:se},{default:t(()=>n[6]||(n[6]=[C("取消")])),_:1}),e(O,{type:"primary",onClick:n[3]||(n[3]=_=>c(J.value))},{default:t(()=>n[7]||(n[7]=[C(" 提交 ")])),_:1})])]),default:t(()=>[e(ge,{inline:!0,"label-position":"right",model:F,"label-width":"auto",ref_key:"formRef",ref:J},{default:t(()=>[e(U,{label:"唯一校验组合",prop:"fields"},{default:t(()=>[e(u,{modelValue:F.fields,"onUpdate:modelValue":n[0]||(n[0]=_=>F.fields=_),fields:"选择字段组合",multiple:"","multiple-limit":5,clearable:"",filterable:"",style:{width:"240px"},disabled:!!(D.value.built_in||!ne.value)},{default:t(()=>[(g(!0),G(H,null,te(Ve.modelFieldLists,(_,N)=>(g(),j(r,{label:_.verbose_name,value:_.name,key:N},null,8,["label","value"]))),128))]),_:1},8,["modelValue","disabled"])]),_:1}),e(U,{label:"空置校验",prop:"validate_null"},{default:t(()=>[e(re,{modelValue:F.validate_null,"onUpdate:modelValue":n[1]||(n[1]=_=>F.validate_null=_),class:"ml-2",style:{"--el-switch-on-color":"#13ce66","--el-switch-off-color":"#ff4949"},disabled:D.value.built_in},null,8,["modelValue","disabled"])]),_:1}),e(U,{label:"描述",prop:"description"},{default:t(()=>[e($,{modelValue:F.description,"onUpdate:modelValue":n[2]||(n[2]=_=>F.description=_),style:{width:"240px"},autosize:{minRows:2,maxRows:4},type:"textarea"},null,8,["modelValue"])]),_:1})]),_:1},8,["model"])]),_:1},8,["modelValue"])])}}}),xl={class:"card"},Ul={class:"dialog-footer"},Il=Ne({__name:"modelinfoView",setup(Ve){const Q=Te(),ae=i(""),w=i("");dl();const L=Se(),{proxy:k}=Le();i("");const B=i([]),X=async()=>{let r=await k.$api.getCiModelGroup();console.log(r),B.value=r.data.results,console.log(B.value)},Y=i([]),J=r=>{Y.value=r},F=(r,u)=>{r.props.name==="verification"?ae.value.getTableData({model:K.value}):r.props.name==="field"&&(console.log(123),w.value.getModelField())},z=i("field");console.log(Q);const se=i(!1),ne=()=>{se.value=!0},D=i("ElemeFilled");ul(()=>D.value,r=>{console.log(r)});const q=i({}),K=ce(()=>{var r;return(r=q.value)==null?void 0:r.id}),c=fe({name:"",verbose_name:"",model_group:"",icon:"ElemeFilled",built_in:!1,update_user:"admin"}),de=i(),_e=fe({name:[{required:!0,message:"请输入模型标识",trigger:"blur"},{pattern:/^[a-z][a-z_]{3,20}$/,trigger:"blur",message:"以英文字符开头,可以使用英文,下划线,长度3-20 ",required:!0}],verbose_name:[{required:!0,message:"请输入模型名称",trigger:"blur"}],model_group:[{required:!0,message:"请选择分组",trigger:"blur"}]});i(!1);const Z=i(!1),A=r=>{Z.value=!1,O(r)},v=async r=>{r&&await r.validate(async(u,U)=>{if(u){let $=await k.$api.updateCiModel({id:be.value,...c});console.log($),$.status=="200"?(b({type:"success",message:"更新成功"}),Z.value=!1,O(r),getCiModelInfo(Q.query,Q.query.id)):b({showClose:!0,message:"添加失败:"+JSON.stringify($.data),type:"error"})}})},n=r=>{ve.confirm("是否确认关闭?").then(()=>{r(),O(de.value)}).catch(()=>{})},O=r=>{r&&r.resetFields()},V=cl(),re=r=>{ve.confirm("是否确认删除?","删除组",{confirmButtonText:"确认删除",cancelButtonText:"取消",type:"warning",draggable:!0}).then(async()=>{(await k.$api.deleteCiModel(r)).status==204?(b({type:"success",message:"删除成功"}),V.removeTabs(Q.path,!0)):b({type:"error",message:"删除失败"})}).catch(()=>{b({type:"info",message:"取消删除"})})},be=i(""),h=r=>{console.log(r),c.icon=r.icon,c.verbose_name=r.verbose_name,c.name=r.name,c.model_group=r.model_group,c.update_user=L.state.username,console.log(c),Z.value=!0,be.value=r.id,X()};return il(async()=>{console.log("onMount"),await w.value.getModelField(),await w.value.getCiModelList(),await w.value.getRules(),await w.value.getModelFieldType()}),rl(()=>{console.log("onUnmounted")}),ml(()=>{console.log("onBeforeMount")}),(r,u)=>{const U=d("el-button"),$=d("el-text"),ge=d("el-space"),ee=d("el-col"),W=d("el-row"),_=d("el-tab-pane"),N=d("el-tabs"),E=d("el-scrollbar"),ye=d("el-form-item"),xe=d("el-input"),Oe=d("el-option"),P=d("el-select"),s=d("el-form"),Re=d("el-dialog"),ue=je("permission");return g(),G(H,null,[R("div",xl,[e(E,null,{default:t(()=>[e(W,{class:"cimodelinfo",justify:"space-between"},{default:t(()=>[e(ee,{span:20},{default:t(()=>[e(ge,{size:30,style:{width:"40%"}},{default:t(()=>[e(U,{size:"large",circle:"",disabled:"",style:{margin:"10px"}},{default:t(()=>[e(x(pl),{icon:q.value.icon},null,8,["icon"])]),_:1}),e($,null,{default:t(()=>[u[12]||(u[12]=C("唯一标识:   ")),e($,{tag:"b"},{default:t(()=>[C(oe(q.value.name),1)]),_:1})]),_:1}),e($,null,{default:t(()=>[u[13]||(u[13]=C("名称:   ")),e($,{tag:"b"},{default:t(()=>[C(oe(q.value.verbose_name),1)]),_:1})]),_:1})]),_:1})]),_:1}),e(ee,{span:2,style:{display:"flex","align-items":"center","justify-content":"center"}},{default:t(()=>[e(ge,{alignment:"flex-end"},{default:t(()=>{var f,S;return[M(e(U,{disabled:q.value.built_in,icon:"Delete",onClick:u[0]||(u[0]=Ce=>re(q.value.id)),circle:""},null,8,["disabled"]),[[ue,`${(f=x(Q).name)==null?void 0:f.replace("_info","")}:delete`]]),M(e(U,{disabled:q.value.built_in,icon:"Edit",onClick:u[1]||(u[1]=Ce=>h(q.value)),circle:""},null,8,["disabled"]),[[ue,`${(S=x(Q).name)==null?void 0:S.replace("_info","")}:edit`]])]}),_:1})]),_:1})]),_:1}),e(N,{modelValue:z.value,"onUpdate:modelValue":u[3]||(u[3]=f=>z.value=f),type:"card",class:"demo-tabs",onTabClick:F},{default:t(()=>[e(_,{label:"模型字段",name:"field"},{default:t(()=>[e(Vl,{ref_key:"ciModelFieldRef",ref:w,ciModelInfo:q.value,"onUpdate:ciModelInfo":u[2]||(u[2]=f=>q.value=f),onGetModelField:J},null,8,["ciModelInfo"])]),_:1}),e(_,{label:"唯一校验",name:"verification"},{default:t(()=>[e(kl,{modelId:K.value,modelFieldLists:Y.value,ref_key:"ciModelUniqueRef",ref:ae},null,8,["modelId","modelFieldLists"])]),_:1})]),_:1},8,["modelValue"])]),_:1})]),e(Re,{modelValue:Z.value,"onUpdate:modelValue":u[11]||(u[11]=f=>Z.value=f),title:"编辑模型",width:"500","before-close":n},{footer:t(()=>[R("div",Ul,[e(U,{onClick:u[9]||(u[9]=f=>A(de.value))},{default:t(()=>u[14]||(u[14]=[C("取消")])),_:1}),e(U,{type:"primary",onClick:u[10]||(u[10]=f=>v(de.value))},{default:t(()=>u[15]||(u[15]=[C(" 确认 ")])),_:1})])]),default:t(()=>[e(s,{ref_key:"modelFormRef",ref:de,style:{"max-width":"600px"},model:c,rules:_e,"label-width":"auto",class:"demo-modelForm","status-icon":""},{default:t(()=>[e(ye,{label:"模型图标",prop:"icon"},{default:t(()=>[e(U,{onClick:ne,icon:c.icon},null,8,["icon"]),e(ol,{isShow:se.value,"onUpdate:isShow":u[4]||(u[4]=f=>se.value=f),iconName:c.icon,"onUpdate:iconName":u[5]||(u[5]=f=>c.icon=f)},null,8,["isShow","iconName"])]),_:1}),e(ye,{label:"唯一标识",prop:"name"},{default:t(()=>[e(xe,{modelValue:c.name,"onUpdate:modelValue":u[6]||(u[6]=f=>c.name=f),placeholder:"请输入模型的唯一标识",disabled:""},null,8,["modelValue"])]),_:1}),e(ye,{label:"模型名称",prop:"verbose_name"},{default:t(()=>[e(xe,{modelValue:c.verbose_name,"onUpdate:modelValue":u[7]||(u[7]=f=>c.verbose_name=f)},null,8,["modelValue"])]),_:1}),e(ye,{label:"所属分组",prop:"model_group"},{default:t(()=>[e(P,{modelValue:c.model_group,"onUpdate:modelValue":u[8]||(u[8]=f=>c.model_group=f),placeholder:"选择分组"},{default:t(()=>[(g(!0),G(H,null,te(B.value,(f,S)=>(g(),j(Oe,{label:f.verbose_name,value:f.id,key:S},null,8,["label","value"]))),128))]),_:1},8,["modelValue"])]),_:1})]),_:1},8,["model","rules"])]),_:1},8,["modelValue"])],64)}}}),Sl=Pe(Il,[["__scopeId","data-v-80e80c3e"]]);export{Sl as default};