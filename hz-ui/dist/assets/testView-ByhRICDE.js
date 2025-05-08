import{d as W,g as M,u as X,r as d,q as D,aq as z,e as w,c as y,o as v,b as _,w as g,k as p,a7 as $,a8 as L,t as T,i as R,aX as V}from"./index-CuRggFqw.js";var I=function(r,e){return Object.defineProperty?Object.defineProperty(r,"raw",{value:e}):r.raw=e,r},i;(function(r){r[r.EOS=0]="EOS",r[r.Text=1]="Text",r[r.Incomplete=2]="Incomplete",r[r.ESC=3]="ESC",r[r.Unknown=4]="Unknown",r[r.SGR=5]="SGR",r[r.OSCURL=6]="OSCURL"})(i||(i={}));class Q{constructor(){this.VERSION="6.0.5",this.setup_palettes(),this._use_classes=!1,this.bold=!1,this.faint=!1,this.italic=!1,this.underline=!1,this.fg=this.bg=null,this._buffer="",this._url_allowlist={http:1,https:1},this._escape_html=!0,this.boldStyle="font-weight:bold",this.faintStyle="opacity:0.7",this.italicStyle="font-style:italic",this.underlineStyle="text-decoration:underline"}set use_classes(e){this._use_classes=e}get use_classes(){return this._use_classes}set url_allowlist(e){this._url_allowlist=e}get url_allowlist(){return this._url_allowlist}set escape_html(e){this._escape_html=e}get escape_html(){return this._escape_html}set boldStyle(e){this._boldStyle=e}get boldStyle(){return this._boldStyle}set faintStyle(e){this._faintStyle=e}get faintStyle(){return this._faintStyle}set italicStyle(e){this._italicStyle=e}get italicStyle(){return this._italicStyle}set underlineStyle(e){this._underlineStyle=e}get underlineStyle(){return this._underlineStyle}setup_palettes(){this.ansi_colors=[[{rgb:[0,0,0],class_name:"ansi-black"},{rgb:[187,0,0],class_name:"ansi-red"},{rgb:[0,187,0],class_name:"ansi-green"},{rgb:[187,187,0],class_name:"ansi-yellow"},{rgb:[0,0,187],class_name:"ansi-blue"},{rgb:[187,0,187],class_name:"ansi-magenta"},{rgb:[0,187,187],class_name:"ansi-cyan"},{rgb:[255,255,255],class_name:"ansi-white"}],[{rgb:[85,85,85],class_name:"ansi-bright-black"},{rgb:[255,85,85],class_name:"ansi-bright-red"},{rgb:[0,255,0],class_name:"ansi-bright-green"},{rgb:[255,255,85],class_name:"ansi-bright-yellow"},{rgb:[85,85,255],class_name:"ansi-bright-blue"},{rgb:[255,85,255],class_name:"ansi-bright-magenta"},{rgb:[85,255,255],class_name:"ansi-bright-cyan"},{rgb:[255,255,255],class_name:"ansi-bright-white"}]],this.palette_256=[],this.ansi_colors.forEach(l=>{l.forEach(t=>{this.palette_256.push(t)})});let e=[0,95,135,175,215,255];for(let l=0;l<6;++l)for(let t=0;t<6;++t)for(let u=0;u<6;++u){let a={rgb:[e[l],e[t],e[u]],class_name:"truecolor"};this.palette_256.push(a)}let s=8;for(let l=0;l<24;++l,s+=10){let t={rgb:[s,s,s],class_name:"truecolor"};this.palette_256.push(t)}}escape_txt_for_html(e){return this._escape_html?e.replace(/[&<>"']/gm,s=>{if(s==="&")return"&amp;";if(s==="<")return"&lt;";if(s===">")return"&gt;";if(s==='"')return"&quot;";if(s==="'")return"&#x27;"}):e}append_buffer(e){var s=this._buffer+e;this._buffer=s}get_next_packet(){var e={kind:i.EOS,text:"",url:""},s=this._buffer.length;if(s==0)return e;var l=this._buffer.indexOf("\x1B");if(l==-1)return e.kind=i.Text,e.text=this._buffer,this._buffer="",e;if(l>0)return e.kind=i.Text,e.text=this._buffer.slice(0,l),this._buffer=this._buffer.slice(l),e;if(l==0){if(s<3)return e.kind=i.Incomplete,e;var t=this._buffer.charAt(1);if(t!="["&&t!="]"&&t!="(")return e.kind=i.ESC,e.text=this._buffer.slice(0,1),this._buffer=this._buffer.slice(1),e;if(t=="["){this._csi_regex||(this._csi_regex=j(q||(q=I([`
                        ^                           # beginning of line
                                                    #
                                                    # First attempt
                        (?:                         # legal sequence
                          \x1B[                      # CSI
                          ([<-?]?)              # private-mode char
                          ([d;]*)                    # any digits or semicolons
                          ([ -/]?               # an intermediate modifier
                          [@-~])                # the command
                        )
                        |                           # alternate (second attempt)
                        (?:                         # illegal sequence
                          \x1B[                      # CSI
                          [ -~]*                # anything legal
                          ([\0-:])              # anything illegal
                        )
                    `],[`
                        ^                           # beginning of line
                                                    #
                                                    # First attempt
                        (?:                         # legal sequence
                          \\x1b\\[                      # CSI
                          ([\\x3c-\\x3f]?)              # private-mode char
                          ([\\d;]*)                    # any digits or semicolons
                          ([\\x20-\\x2f]?               # an intermediate modifier
                          [\\x40-\\x7e])                # the command
                        )
                        |                           # alternate (second attempt)
                        (?:                         # illegal sequence
                          \\x1b\\[                      # CSI
                          [\\x20-\\x7e]*                # anything legal
                          ([\\x00-\\x1f:])              # anything illegal
                        )
                    `]))));let a=this._buffer.match(this._csi_regex);if(a===null)return e.kind=i.Incomplete,e;if(a[4])return e.kind=i.ESC,e.text=this._buffer.slice(0,1),this._buffer=this._buffer.slice(1),e;a[1]!=""||a[3]!="m"?e.kind=i.Unknown:e.kind=i.SGR,e.text=a[2];var u=a[0].length;return this._buffer=this._buffer.slice(u),e}else if(t=="]"){if(s<4)return e.kind=i.Incomplete,e;if(this._buffer.charAt(2)!="8"||this._buffer.charAt(3)!=";")return e.kind=i.ESC,e.text=this._buffer.slice(0,1),this._buffer=this._buffer.slice(1),e;this._osc_st||(this._osc_st=Y(N||(N=I([`
                        (?:                         # legal sequence
                          (\x1B\\)                    # ESC                           |                           # alternate
                          (\x07)                      # BEL (what xterm did)
                        )
                        |                           # alternate (second attempt)
                        (                           # illegal sequence
                          [\0-]                 # anything illegal
                          |                           # alternate
                          [\b-]                 # anything illegal
                          |                           # alternate
                          [-]                 # anything illegal
                        )
                    `],[`
                        (?:                         # legal sequence
                          (\\x1b\\\\)                    # ESC \\
                          |                           # alternate
                          (\\x07)                      # BEL (what xterm did)
                        )
                        |                           # alternate (second attempt)
                        (                           # illegal sequence
                          [\\x00-\\x06]                 # anything illegal
                          |                           # alternate
                          [\\x08-\\x1a]                 # anything illegal
                          |                           # alternate
                          [\\x1c-\\x1f]                 # anything illegal
                        )
                    `])))),this._osc_st.lastIndex=0;{let o=this._osc_st.exec(this._buffer);if(o===null)return e.kind=i.Incomplete,e;if(o[3])return e.kind=i.ESC,e.text=this._buffer.slice(0,1),this._buffer=this._buffer.slice(1),e}{let o=this._osc_st.exec(this._buffer);if(o===null)return e.kind=i.Incomplete,e;if(o[3])return e.kind=i.ESC,e.text=this._buffer.slice(0,1),this._buffer=this._buffer.slice(1),e}this._osc_regex||(this._osc_regex=j(H||(H=I([`
                        ^                           # beginning of line
                                                    #
                        \x1B]8;                    # OSC Hyperlink
                        [ -:<-~]*       # params (excluding ;)
                        ;                           # end of params
                        ([!-~]{0,512})        # URL capture
                        (?:                         # ST
                          (?:\x1B\\)                  # ESC                           |                           # alternate
                          (?:\x07)                    # BEL (what xterm did)
                        )
                        ([ -~]+)              # TEXT capture
                        \x1B]8;;                   # OSC Hyperlink End
                        (?:                         # ST
                          (?:\x1B\\)                  # ESC                           |                           # alternate
                          (?:\x07)                    # BEL (what xterm did)
                        )
                    `],[`
                        ^                           # beginning of line
                                                    #
                        \\x1b\\]8;                    # OSC Hyperlink
                        [\\x20-\\x3a\\x3c-\\x7e]*       # params (excluding ;)
                        ;                           # end of params
                        ([\\x21-\\x7e]{0,512})        # URL capture
                        (?:                         # ST
                          (?:\\x1b\\\\)                  # ESC \\
                          |                           # alternate
                          (?:\\x07)                    # BEL (what xterm did)
                        )
                        ([\\x20-\\x7e]+)              # TEXT capture
                        \\x1b\\]8;;                   # OSC Hyperlink End
                        (?:                         # ST
                          (?:\\x1b\\\\)                  # ESC \\
                          |                           # alternate
                          (?:\\x07)                    # BEL (what xterm did)
                        )
                    `]))));let a=this._buffer.match(this._osc_regex);if(a===null)return e.kind=i.ESC,e.text=this._buffer.slice(0,1),this._buffer=this._buffer.slice(1),e;e.kind=i.OSCURL,e.url=a[1],e.text=a[2];var u=a[0].length;return this._buffer=this._buffer.slice(u),e}else if(t=="(")return e.kind=i.Unknown,this._buffer=this._buffer.slice(3),e}}ansi_to_html(e){this.append_buffer(e);for(var s=[];;){var l=this.get_next_packet();if(l.kind==i.EOS||l.kind==i.Incomplete)break;l.kind==i.ESC||l.kind==i.Unknown||(l.kind==i.Text?s.push(this.transform_to_html(this.with_state(l))):l.kind==i.SGR?this.process_ansi(l):l.kind==i.OSCURL&&s.push(this.process_hyperlink(l)))}return s.join("")}with_state(e){return{bold:this.bold,faint:this.faint,italic:this.italic,underline:this.underline,fg:this.fg,bg:this.bg,text:e.text}}process_ansi(e){let s=e.text.split(";");for(;s.length>0;){let l=s.shift(),t=parseInt(l,10);if(isNaN(t)||t===0)this.fg=null,this.bg=null,this.bold=!1,this.faint=!1,this.italic=!1,this.underline=!1;else if(t===1)this.bold=!0;else if(t===2)this.faint=!0;else if(t===3)this.italic=!0;else if(t===4)this.underline=!0;else if(t===21)this.bold=!1;else if(t===22)this.faint=!1,this.bold=!1;else if(t===23)this.italic=!1;else if(t===24)this.underline=!1;else if(t===39)this.fg=null;else if(t===49)this.bg=null;else if(t>=30&&t<38)this.fg=this.ansi_colors[0][t-30];else if(t>=40&&t<48)this.bg=this.ansi_colors[0][t-40];else if(t>=90&&t<98)this.fg=this.ansi_colors[1][t-90];else if(t>=100&&t<108)this.bg=this.ansi_colors[1][t-100];else if((t===38||t===48)&&s.length>0){let u=t===38,a=s.shift();if(a==="5"&&s.length>0){let f=parseInt(s.shift(),10);f>=0&&f<=255&&(u?this.fg=this.palette_256[f]:this.bg=this.palette_256[f])}if(a==="2"&&s.length>2){let f=parseInt(s.shift(),10),o=parseInt(s.shift(),10),x=parseInt(s.shift(),10);if(f>=0&&f<=255&&o>=0&&o<=255&&x>=0&&x<=255){let S={rgb:[f,o,x],class_name:"truecolor"};u?this.fg=S:this.bg=S}}}}}transform_to_html(e){let s=e.text;if(s.length===0||(s=this.escape_txt_for_html(s),!e.bold&&!e.italic&&!e.faint&&!e.underline&&e.fg===null&&e.bg===null))return s;let l=[],t=[],u=e.fg,a=e.bg;e.bold&&l.push(this._boldStyle),e.faint&&l.push(this._faintStyle),e.italic&&l.push(this._italicStyle),e.underline&&l.push(this._underlineStyle),this._use_classes?(u&&(u.class_name!=="truecolor"?t.push(`${u.class_name}-fg`):l.push(`color:rgb(${u.rgb.join(",")})`)),a&&(a.class_name!=="truecolor"?t.push(`${a.class_name}-bg`):l.push(`background-color:rgb(${a.rgb.join(",")})`))):(u&&l.push(`color:rgb(${u.rgb.join(",")})`),a&&l.push(`background-color:rgb(${a.rgb})`));let f="",o="";return t.length&&(f=` class="${t.join(" ")}"`),l.length&&(o=` style="${l.join(";")}"`),`<span${o}${f}>${s}</span>`}process_hyperlink(e){let s=e.url.split(":");return s.length<1||!this._url_allowlist[s[0]]?"":`<a href="${this.escape_txt_for_html(e.url)}">${this.escape_txt_for_html(e.text)}</a>`}}function j(r,...e){let s=r.raw[0],l=/^\s+|\s+\n|\s*#[\s\S]*?\n|\n/gm,t=s.replace(l,"");return new RegExp(t)}function Y(r,...e){let s=r.raw[0],l=/^\s+|\s+\n|\s*#[\s\S]*?\n|\n/gm,t=s.replace(l,"");return new RegExp(t,"g")}var q,N,H;const Z={class:"card"},P=["innerHTML"],ee=W({__name:"testView",setup(r){const{proxy:e}=M();X();const s=d([]),l=d("sseTest"),t=d(null),u=d(null),a=()=>{u.value=new EventSource(t.value),u.value.onmessage=h=>{console.log(h),console.log(typeof h.data),console.log(h.data.status),s.value.push(JSON.parse(h.data)),JSON.parse(h.data).status==="SUCCESS"&&u.value.close()}},f=()=>{u.value.close()};D(()=>{});const o=d(null),x=async()=>{let h=await V.request({url:"/api/v1/test_celery/",method:"post"});o.value=h.data.task_id},S=d(null),A=async h=>{let n=await V.request({url:`/api/v1/check_task/${h}/`});S.value=n.data};z(()=>{u.value&&u.value.close(),b.value&&b.value.close()});const U=new Q,C=d(""),b=d(null),k=d([]),F=()=>{k.value=[],b.value=new WebSocket("/ws/ansible/"),b.value.onmessage=h=>{const n=JSON.parse(h.data);n.type==="output"?(console.log(U.ansi_to_html(n.message+`\r
`)),k.value.push(U.ansi_to_html(n.message+`\r
`))):n.type==="complete"&&(console.log(n),k.value.push(`执行完成，返回码: ${n.returncode}`),b.value.close())},b.value.onopen=()=>{b.value.send(JSON.stringify({module_args:C.value,module_name:"shell",inventory:["192.168.163.160","192.168.163.162"],username:"root",password:"thinker"}))}},G=()=>{b.value.close()};return(h,n)=>{const B=w("el-input"),m=w("el-button"),E=w("el-tab-pane"),J=w("el-tabs");return v(),y("div",Z,[_(J,{modelValue:l.value,"onUpdate:modelValue":n[3]||(n[3]=c=>l.value=c),class:"demo-tabs"},{default:g(()=>[_(E,{label:"SSE测试",name:"sseTest"},{default:g(()=>[_(B,{modelValue:t.value,"onUpdate:modelValue":n[0]||(n[0]=c=>t.value=c),style:{width:"480px"},placeholder:"输入sse接口地址"},null,8,["modelValue"]),_(m,{onClick:a},{default:g(()=>n[4]||(n[4]=[p("开始")])),_:1}),_(m,{type:"danger",onClick:f},{default:g(()=>n[5]||(n[5]=[p("终止")])),_:1}),(v(!0),y($,null,L(s.value,(c,O)=>(v(),y("p",{key:O},T(c),1))),128))]),_:1}),_(E,{label:"celery测试",name:"celery"},{default:g(()=>[_(m,{onClick:x},{default:g(()=>n[6]||(n[6]=[p("提交任务")])),_:1}),_(m,{type:"primary",onClick:n[1]||(n[1]=c=>A(o.value))},{default:g(()=>n[7]||(n[7]=[p("查看任务状态")])),_:1}),p(" "+T(`任务ID是：${o.value}`)+" ",1),R("div",null,T(S.value),1)]),_:1}),_(E,{label:"WebSocket测试",name:"weSocketTest"},{default:g(()=>[_(B,{modelValue:C.value,"onUpdate:modelValue":n[2]||(n[2]=c=>C.value=c),style:{width:"240px"}},null,8,["modelValue"]),_(m,{onClick:F},{default:g(()=>n[8]||(n[8]=[p("执行")])),_:1}),_(m,{type:"danger",onClick:G},{default:g(()=>n[9]||(n[9]=[p("终止")])),_:1}),(v(!0),y($,null,L(k.value,(c,O)=>(v(),y("div",{key:O},[R("div",{innerHTML:c},null,8,P)]))),128))]),_:1})]),_:1},8,["modelValue"])])}}});export{ee as default};
