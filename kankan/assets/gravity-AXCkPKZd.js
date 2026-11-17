var Ht=Object.defineProperty;var At=(e,t,s)=>t in e?Ht(e,t,{enumerable:!0,configurable:!0,writable:!0,value:s}):e[t]=s;var f=(e,t,s)=>At(e,typeof t!="symbol"?t+"":t,s);import{D as Rt,c as V,f as G,a as vt,b as It,r as Pt,d as gt,g as dt,B as ct,O as v,u as w,e as Ft,h as Q,i as yt,j as Nt,T as qt,k as Ut,L as Bt,M as Dt,t as Ot,l as wt,m as Wt,n as jt}from"./tour-HdxlbHa2.js";class ut extends Error{}const ht=e=>e.cells.map(t=>t??0).join("");function O(e,t=Rt,s={}){const o=s.maxStates??2e5,n=new Map,l=new Map,a=(h,x)=>{const g=n.get(x);if(g)return g;if(n.size>=o)throw new ut;const y=V(h);let b;if(y===0)b={ways:1,pSuccess:1,maxRemoved:0,branching:0,best:null,bestNext:null,children:[]};else{const k=G(h,t);b={ways:0,pSuccess:0,maxRemoved:0,branching:k.length,best:null,bestNext:null,children:[]};let B=-1;for(const C of k){const F=vt(h,C[0],C[1],t).board,M=ht(F);l.set(M,F);const L=a(F,M);b.children.push(M),b.ways+=L.ways,b.pSuccess+=L.pSuccess;const E=2+L.maxRemoved,z=E*4+(L.ways>0?2:0);z>B&&(B=z,b.maxRemoved=E,b.best=C,b.bestNext=M)}k.length>0&&(b.pSuccess/=k.length)}return n.set(x,b),b},d=ht(e),c=V(e),r=G(e,t).length;try{const h=a(e,d);let x=0;for(const C of n.values())x+=C.branching;const g=[];let y=h;for(;y!=null&&y.best&&y.bestNext;)g.push(y.best),y=n.get(y.bestNext);const b=new Map,k=C=>{const F=b.get(C);if(F)return F;const M=n.get(C),L=M.children.filter(Y=>n.get(Y).ways>0);let E=0,z=0;if(L.length>0){for(const Y of L){const rt=k(Y);E+=rt.forks,z+=rt.forced}E=E/L.length+(L.length<M.children.length?1:0),z=z/L.length+(M.children.length===1?1:0)}const it={forks:E,forced:z};return b.set(C,it),it},B=h.ways>0?k(d):{forks:0,forced:0};return{exact:!0,expectedForks:B.forks,expectedForced:B.forced,solvable:h.ways>0,solutionPaths:h.ways,randomSuccessRate:h.pSuccess,deadEndRate:1-h.pSuccess,maxRemoved:h.maxRemoved,totalNumbers:c,firstMoves:r,avgBranching:x/n.size,states:n.size,bestLine:g}}catch(h){if(!(h instanceof ut))throw h;return{exact:!1,expectedForks:0,expectedForced:0,solvable:!1,solutionPaths:0,randomSuccessRate:0,deadEndRate:1,maxRemoved:0,totalNumbers:c,firstMoves:r,avgBranching:0,states:n.size,bestLine:[]}}}class Gt{constructor(t,s,o=1/0){f(this,"snap");f(this,"history",[]);f(this,"moveLog",[]);f(this,"selected",null);f(this,"undosUsed",0);this.initial=t,this.rules=s,this.undoLimit=o;let n=0;const l=t.cells.map(a=>a===null?-1:n++);this.snap={board:t,ids:l,lastMoved:new Set,combo:0,maxCombo:0,moves:0}}get board(){return this.snap.board}get ids(){return this.snap.ids}get selection(){return this.selected}get combo(){return this.snap.combo}get maxCombo(){return this.snap.maxCombo}get moves(){return this.snap.moves}get remaining(){return V(this.snap.board)}get canUndo(){return this.history.length>0&&this.undosLeft>0}get undosLeft(){return Math.max(0,this.undoLimit-this.undosUsed)}get pairCount(){return G(this.snap.board,this.rules).length}get cleared(){return this.remaining===0}get stuck(){return!this.cleared&&this.pairCount===0}get lastMoved(){return this.snap.lastMoved}idAt(t){return this.snap.ids[t.r*this.snap.board.cols+t.c]??-1}tap(t){if(this.idAt(t)<0)return{kind:"ignore"};const s=this.selected;return s?s.r===t.r&&s.c===t.c?(this.selected=null,{kind:"deselect"}):It(this.snap.board,s,t,this.rules)?this.play(s,t):(this.selected=t,{kind:"switch",pos:t,rejected:s}):(this.selected=t,{kind:"select",pos:t})}play(t,s){const o=this.snap,n=vt(o.board,t,s,this.rules),l=this.idAt(t),a=this.idAt(s),d=o.lastMoved.has(l)||o.lastMoved.has(a),c=n.origin.map(x=>x<0?-1:o.ids[x]??-1),r=new Set;n.origin.forEach((x,g)=>{x>=0&&x!==g&&r.add(c[g])});const h=d?o.combo+1:0;return this.history.push(o),this.moveLog.push([t,s]),this.snap={board:n.board,ids:c,lastMoved:r,combo:h,maxCombo:Math.max(o.maxCombo,h),moves:o.moves+1},this.selected=null,{kind:"match",removed:[l,a],values:n.values,chain:d}}undo(){return this.canUndo?(this.undosUsed++,this.pop()):!1}pop(){const t=this.history.pop();return t?(this.moveLog.pop(),this.snap=t,this.selected=null,!0):!1}rewind(t){let s=0;for(;s<t&&this.pop();)s++;return s}get timeline(){return[...this.history.map(t=>t.board),this.snap.board]}get moveHistory(){return this.moveLog}clearSelection(){this.selected=null}}const _t={easy:[0,1.5],normal:[1.5,3.5],hard:[3.5,1/0],any:[0,1/0]};function Kt(e,[t,s]){return e<t?t-e:e>s?e-s:0}function Jt(e,t,s,o={}){const n=o.onlySolvable??!0,l=o.difficulty??"any",a=_t[l],d=o.stateBudget??6e5,c=gt(e);let r=null,h=null,x=0,g=0;for(;g<3e3;){g++;const y=Pt(c,{rows:t.rows,cols:t.cols},s),b=O(y,s,{maxStates:6e4});if(x+=b.states,h={board:y,report:b},!n)return{seed:e,board:y,report:b,tries:g,guaranteed:b.solvable,difficulty:l,difficultyMatched:!1};if(b.solvable){const k=Kt(b.expectedForks,a);if((!r||k<r.dist)&&(r={board:y,report:b,dist:k}),k===0)break}if(x>=d)break}return r?{seed:e,board:r.board,report:r.report,tries:g,guaranteed:!0,difficulty:l,difficultyMatched:r.dist===0}:{seed:e,...h,tries:g,guaranteed:!1,difficulty:l,difficultyMatched:!1}}const pt=6e4;function Yt(e,t,s){const o=a=>{const d=O(a,s,{maxStates:pt});return d.exact?d.solvable:null},n=e.length-1,l=o(e[n]);if(l===null)return{kind:"unknown"};if(l)return{kind:"alive"};for(let a=n-1;a>=0;a--){const d=o(e[a]);if(d===null)return{kind:"unknown"};if(!d)continue;const c=e[a],r=t[a],h=O(c,s,{maxStates:pt}),x=h.bestLine.length?[h.bestLine[0]]:[];return{kind:"fatal",moveIndex:a,movesAgo:n-a,pair:r,values:[dt(c,r[0])??0,dt(c,r[1])??0],alternatives:x}}return{kind:"initial"}}const H=76,A=24;class Qt{constructor(t,s){f(this,"root");f(this,"cells");f(this,"labels");f(this,"fake");f(this,"colHead");f(this,"rowHead");f(this,"optionsPop");f(this,"mounted",!1);f(this,"cols",5);f(this,"rows",4);f(this,"seed",0);f(this,"board");f(this,"settings");f(this,"flashTimer",0);f(this,"statusText","");f(this,"lang","ko");this.boardWrap=t,this.board=new ct(t),this.settings=new ct(s),this.root=document.createElement("div"),this.root.className="xl",this.root.hidden=!0,this.root.innerHTML=`
      <div class="xl-title">
        <span class="xl-icon" aria-hidden="true"></span>
        <span class="xl-qat">
          <button data-i18n-title="xl.save" tabindex="-1">▣</button>
          <button data-act="undo" data-i18n-title="xl.undoTip">↶</button>
        </span>
        <span class="xl-doc" data-i18n="xl.doc"></span>
        <span class="xl-search" data-i18n="xl.search"></span>
        <span class="xl-win">
          <button tabindex="-1" data-i18n-title="xl.min">─</button>
          <button data-act="fullscreen" id="xl-full" data-i18n-title="xl.max">☐</button>
          <button tabindex="-1" data-i18n-title="xl.close">✕</button>
        </span>
      </div>
      <div class="xl-menu">
        <span data-i18n="xl.m.file"></span><span class="on" data-i18n="xl.m.home"></span><span data-i18n="xl.m.insert"></span>
        <span data-i18n="xl.m.layout"></span><span data-i18n="xl.m.formulas"></span><span data-i18n="xl.m.data"></span>
        <span data-i18n="xl.m.review"></span><span data-i18n="xl.m.view"></span><span data-i18n="xl.m.help"></span>
        <button class="xl-guide" data-act="tour" id="xl-guide">↻ <span data-i18n="app.guide"></span></button>
      </div>
      <div class="xl-ribbon">
        <div class="xl-group">
          <div class="xl-row"><button class="xl-big" tabindex="-1"><i>📋</i><span data-i18n="xl.paste"></span></button>
          <div class="xl-col"><button tabindex="-1" data-i18n="xl.cut"></button><button tabindex="-1" data-i18n="xl.copy"></button></div></div>
          <span class="xl-glabel" data-i18n="xl.g.clipboard"></span>
        </div>
        <div class="xl-group">
          <div class="xl-col">
            <div class="xl-row"><span class="xl-field" style="width:110px" data-i18n="xl.font"></span><span class="xl-field" style="width:36px">11</span></div>
            <div class="xl-row"><button tabindex="-1"><b>B</b></button><button tabindex="-1"><i>I</i></button><button tabindex="-1"><u>U</u></button><button tabindex="-1">▦</button></div>
          </div>
          <span class="xl-glabel" data-i18n="xl.g.font"></span>
        </div>
        <div class="xl-group" id="xl-edit">
          <div class="xl-row">
            <button class="xl-big" data-act="undo"><i>↶</i><span class="undo-n"></span></button>
            <button class="xl-big" data-act="hint"><i>✦</i><span data-i18n="xl.hint"></span></button>
            <button class="xl-big" data-act="restart"><i>⟳</i><span data-i18n="xl.restart"></span></button>
            <button class="xl-big" data-act="new"><i>＋</i><span data-i18n="xl.new"></span></button>
          </div>
          <span class="xl-glabel" data-i18n="xl.g.edit"></span>
        </div>
        <div class="xl-group xl-opt">
          <div class="xl-row"><button class="xl-big" id="xl-opt-btn"><i>⚙</i><span data-i18n="xl.options"></span></button></div>
          <span class="xl-glabel" data-i18n="xl.g.settings"></span>
          <div class="xl-pop" id="xl-pop" hidden></div>
        </div>
      </div>
      <div class="xl-fbar">
        <div class="xl-name" id="xl-name">A1</div>
        <div class="xl-fx">ƒx</div>
        <div class="xl-formula" id="xl-formula"></div>
      </div>
      <div class="xl-sheet">
        <div class="xl-corner"></div>
        <div class="xl-colhead" id="xl-colhead"></div>
        <div class="xl-rowhead" id="xl-rowhead"></div>
        <div class="xl-cells" id="xl-cells">
          <div class="xl-labels" id="xl-labels"></div>
          <div class="xl-fake" id="xl-fake" hidden></div>
        </div>
      </div>
      <div class="xl-tabs">
        <span class="xl-nav">◀ ▶</span>
        <span class="xl-tab" data-i18n="xl.t.summary"></span>
        <span class="xl-tab on" id="xl-tab"></span>
        <span class="xl-tab" data-i18n="xl.t.raw"></span>
        <button class="xl-tab xl-add" data-act="new" data-i18n-title="xl.t.add">＋</button>
      </div>
      <div class="xl-status">
        <span id="xl-ready"></span>
        <span class="xl-sum" id="xl-sum"></span>
        <span class="xl-zoom">▤ ▥ ▧ ─────●───── 100%</span>
      </div>
    `,document.body.append(this.root);const o=n=>this.root.querySelector(`#${n}`);this.cells=o("xl-cells"),this.labels=o("xl-labels"),this.fake=o("xl-fake"),this.colHead=o("xl-colhead"),this.rowHead=o("xl-rowhead"),this.optionsPop=o("xl-pop"),this.root.style.setProperty("--cw",`${H}px`),this.root.style.setProperty("--ch",`${A}px`),o("xl-opt-btn").addEventListener("click",n=>{n.stopPropagation(),this.optionsPop.hidden=!this.optionsPop.hidden}),document.addEventListener("click",n=>{!this.optionsPop.hidden&&!this.optionsPop.contains(n.target)&&(this.optionsPop.hidden=!0)}),this.cells.addEventListener("scroll",()=>{this.colHead.scrollLeft=this.cells.scrollLeft,this.rowHead.scrollTop=this.cells.scrollTop}),window.addEventListener("resize",()=>this.mounted&&this.drawHeaders())}mount(){this.mounted||(this.mounted=!0,this.board.moveInto(this.cells),this.settings.moveInto(this.optionsPop),this.root.hidden=!1,this.layout())}unmount(){this.mounted&&(this.mounted=!1,this.board.restore(),this.settings.restore(),this.boardWrap.style.left="",this.boardWrap.style.top="",this.root.hidden=!0,this.setBoss(!1))}setPuzzle(t,s,o){this.seed=t,this.cols=s,this.rows=o,this.root.querySelector("#xl-tab").textContent=`Q4_${t}`,this.setBoss(!1),this.layout()}layout(){this.mounted&&(this.boardWrap.style.left=`${v.col*H}px`,this.boardWrap.style.top=`${v.row*A}px`,this.drawLabels(),this.drawFake(),this.drawHeaders())}cell(t,s,o,n="",l=""){return`<div class="xl-c ${n}" ${l} style="left:${t*H}px;top:${s*A}px">${o}</div>`}drawLabels(){const{cols:t,rows:s}=this,o=v.row+s,n=v.col+t+1;let l="";const a=this.lang,d=w(a,"xl.teams").split(",");l+=this.cell(0,0,w(a,"xl.title"),"title"),l+=this.cell(0,1,w(a,"xl.unit"),"muted"),l+=this.cell(1,v.row-1,w(a,"xl.col"),"th");for(let r=0;r<t;r++)l+=this.cell(v.col+r,v.row-1,w(a,"xl.week",{n:r+1}),"th");for(let r=0;r<s;r++)l+=this.cell(1,v.row+r,d[r%d.length],"rh");l+=this.cell(1,o,w(a,"xl.total"),"th");for(let r=0;r<t;r++)l+=this.cell(v.col+r,o,"","num total",`data-sum="${r}"`);l+=this.cell(n,v.row-1,w(a,"xl.item"),"th"),l+=this.cell(n+1,v.row-1,w(a,"xl.value"),"th"),["xl.k0","xl.k1","xl.k2","xl.k3","xl.k4"].map(r=>w(a,r)).forEach((r,h)=>{l+=this.cell(n,v.row+h,r,"rh"),l+=this.cell(n+1,v.row+h,"","num",`data-k="${h}"`)}),l+=this.cell(0,o+2,w(a,"xl.note"),"muted"),this.labels.innerHTML=l}drawFake(){const t=gt(this.seed*31+7),{cols:s,rows:o}=this,n=new Array(s).fill(0);let l="";for(let a=0;a<o;a++)for(let d=0;d<s;d++){const c=120+Math.floor(t()*1880);n[d]+=c,l+=this.cell(d,a,c.toLocaleString(),"num")}n.forEach((a,d)=>l+=this.cell(d,o,a.toLocaleString(),"num total")),this.fake.innerHTML=l,this.fake.style.left=`${v.col*H}px`,this.fake.style.top=`${v.row*A}px`,this.fake.style.width=`${s*H}px`,this.fake.style.height=`${(o+1)*A}px`}drawHeaders(){const t=Math.max(this.cells.clientWidth,window.innerWidth),s=Math.max(this.cells.clientHeight,window.innerHeight),o=Math.ceil(t/H)+2,n=Math.ceil(s/A)+2;this.colHead.innerHTML=Array.from({length:o},(l,a)=>`<span>${Ft(a)}</span>`).join(""),this.rowHead.innerHTML=Array.from({length:n},(l,a)=>`<span>${a+1}</span>`).join(""),this.labels.style.width=`${o*H}px`,this.labels.style.height=`${n*A}px`}update(t){if(!this.mounted)return;const{board:s}=t,o=new Array(s.cols).fill(0);let n=0,l=0;s.cells.forEach((c,r)=>{c!==null&&(o[r%s.cols]+=c,n+=c,l++)});for(const c of this.labels.querySelectorAll("[data-sum]"))c.textContent=String(o[Number(c.dataset.sum)]??0);const a=[t.remaining,t.moves,t.pairCount,t.combo,t.maxCombo];for(const c of this.labels.querySelectorAll("[data-k]"))c.textContent=String(a[Number(c.dataset.k)]??"");this.root.querySelector("#xl-sum").textContent=l?w(this.lang,"xl.sum",{avg:(n/l).toFixed(1),count:l,sum:n}):"";const d=t.selection;d&&(this.root.querySelector("#xl-name").textContent=Q(d),this.root.querySelector("#xl-formula").textContent=String(s.cells[d.r*s.cols+d.c]??""))}showMove(t,s,o){if(!this.mounted)return;const[n,l]=[Q(t),Q(s)],a=o[0]===o[1]?`=${n}-${l}`:`=SUM(${n},${l})`;this.root.querySelector("#xl-name").textContent=l,this.root.querySelector("#xl-formula").textContent=a}setStatus(t){this.statusText=t,this.flashTimer||(this.root.querySelector("#xl-ready").textContent=t)}flashStatus(t){const s=this.root.querySelector("#xl-ready");s.textContent=t,clearTimeout(this.flashTimer),this.flashTimer=window.setTimeout(()=>{this.flashTimer=0,s.textContent=this.statusText},1400)}setLang(t){this.lang=t,yt(this.root,t),this.mounted&&this.drawLabels()}toggleBoss(){this.setBoss(this.fake.hidden)}setBoss(t){this.fake.hidden=!t,this.root.classList.toggle("boss",t)}}const Xt=["basic","sheet","dev"],St={"4x4":{cols:4,rows:4},"5x4":{cols:5,rows:4},"6x4":{cols:6,rows:4}},D={size:"5x4",diagonal:!0,collapseColumns:!0,onlySolvable:!0,difficulty:"normal",theme:"basic",lang:Nt()},Zt=["easy","normal","hard","any"],Vt=3,kt="gnm.settings.v1";function te(){try{const e=localStorage.getItem(kt);if(e){const t={...D,...JSON.parse(e)};return St[t.size]||(t.size=D.size),Xt.includes(t.theme)||(t.theme="basic"),Zt.includes(t.difficulty)||(t.difficulty=D.difficulty),Bt.includes(t.lang)||(t.lang=D.lang),t}}catch{}return{...D}}function at(e){try{localStorage.setItem(kt,JSON.stringify(e))}catch{}}const ee=document.querySelector("#app");ee.innerHTML=`
  <header>
    <h1><span data-i18n="app.title"></span> <small style="font-weight:400;color:var(--muted)" data-i18n="app.proto"></small></h1>
    <span class="head-btns">
      <span class="seed" id="seed"></span>
      <button data-act="tour" id="btn-tour" data-i18n-title="app.guide">?</button>
      <button data-act="fullscreen" id="btn-full" data-i18n-title="app.full">⛶</button>
    </span>
  </header>
  <div class="stats">
    <div class="stat"><b id="st-left">0</b><span data-i18n="st.left"></span></div>
    <div class="stat"><b id="st-moves">0</b><span data-i18n="st.moves"></span></div>
    <div class="stat"><b id="st-pairs">0</b><span data-i18n="st.pairs"></span></div>
    <div class="stat" id="st-combo-box"><b id="st-combo">0</b><span data-i18n="st.combo"></span></div>
  </div>
  <div class="board-wrap" id="board-wrap">
    <div class="board" id="board" role="grid" data-i18n-aria="board"></div>
    <div class="toast" id="toast"></div>
  </div>
  <div class="status" id="status"></div>
  <div class="actions">
    <button class="btn" data-act="undo" id="btn-undo"></button>
    <button class="btn" data-act="hint" data-i18n="btn.hint"></button>
    <button class="btn" data-act="restart" data-i18n="btn.restart"></button>
    <button class="btn primary" data-act="new" data-i18n="btn.new"></button>
  </div>
  <details id="settings-box">
    <summary data-i18n="set.summary"></summary>
    <div class="settings" id="settings">
      <label><span data-i18n="set.size"></span> <select id="set-size">
        <option value="4x4" data-i18n="size.4x4"></option>
        <option value="5x4" data-i18n="size.5x4"></option>
        <option value="6x4" data-i18n="size.6x4"></option>
      </select></label>
      <label><span data-i18n="set.difficulty"></span> <select id="set-difficulty">
        <option value="easy" data-i18n="diff.easy"></option>
        <option value="normal" data-i18n="diff.normal"></option>
        <option value="hard" data-i18n="diff.hard"></option>
        <option value="any" data-i18n="diff.any"></option>
      </select></label>
      <label><span data-i18n="set.diagonal"></span> <input type="checkbox" id="set-diagonal" /></label>
      <label><span data-i18n="set.collapse"></span> <input type="checkbox" id="set-collapse" /></label>
      <label><span data-i18n="set.solvable"></span> <input type="checkbox" id="set-solvable" /></label>
      <label><span data-i18n="set.theme"></span> <select id="set-theme">
        <option value="basic" data-i18n="theme.basic"></option>
        <option value="sheet" data-i18n="theme.sheet"></option>
        <option value="dev" data-i18n="theme.dev"></option>
      </select></label>
      <label><span data-i18n="set.lang"></span> <select id="set-lang">
        <option value="ko">한국어</option>
        <option value="en">English</option>
      </select></label>
    </div>
  </details>
  <details id="dev-box">
    <summary data-i18n="dev.summary"></summary>
    <div class="dev" id="dev"></div>
  </details>
  <div class="overlay" id="overlay" hidden>
    <div class="dialog" role="dialog" aria-modal="true" aria-labelledby="ov-title">
      <div class="dialog-head"><span id="ov-title"></span><button class="dialog-x" data-act="close" data-i18n-aria="close">✕</button></div>
      <p id="ov-text"></p>
      <div class="dialog-actions" id="ov-actions"></div>
    </div>
  </div>
`;const u=e=>document.getElementById(e),q=u("board"),bt=u("board-wrap"),X=u("toast"),j=u("overlay"),ft=u("settings"),Lt=u("set-size"),N=e=>document.querySelector(e);function se(e,t){const s=wt[t];if(e==="sheet"||e==="dev"){const o=e==="sheet",n=o?["#board","#xl-edit","#xl-opt-btn","#xl-full","#xl-guide"]:["#board",".dv-tools","#dv-gear","#dv-full","#dv-guide"];return[{targets:()=>n.map(N),...s.real},{targets:()=>[N("#board")],...s.rule},{targets:()=>[N(o?"#xl-edit":".dv-tools")],title:s.buttons.title,text:o?s.buttonsSheet:s.buttonsDev},{targets:()=>[],title:s.boss.title,text:o?s.bossSheet:s.bossDev}]}return[{targets:()=>[N("#board")],...s.rule},{targets:()=>[N(".actions")],...s.buttons},{targets:()=>[N("#settings-box")],...s.settings}]}const _=new qt;function $t(){if(_.active)return;const e=p.theme,t=p.lang,s=wt[t],o={next:s.next,prev:s.prev,done:s.done,close:w(t,"close")};requestAnimationFrame(()=>_.start(se(e,t),()=>Wt(e),o))}const mt=new Set;function Ct(){const e=p.theme;mt.has(e)||(mt.add(e),jt(e)||$t())}let p=te(),m,i,R=null,I=!1,W=!1,K=!1,U=null;const P=new Map,nt={sheet:new Qt(bt,ft),dev:new Ut(bt,ft)},T=()=>p.theme==="basic"?null:nt[p.theme],Tt=e=>({diagonal:e.diagonal,collapseColumns:e.collapseColumns}),S=()=>Dt[p.lang][p.theme];function ae(){Lt.value=p.size,u("set-difficulty").value=p.difficulty,u("set-diagonal").checked=p.diagonal,u("set-collapse").checked=p.collapseColumns,u("set-solvable").checked=p.onlySolvable,u("set-theme").value=p.theme,u("set-lang").value=p.lang}function Mt(){const e=p.lang;document.documentElement.lang=e,yt(document,e);for(const t of Object.values(nt))t.setLang(e);document.title=S().title,m&&(u("seed").textContent=e==="ko"?`판 #${m.seed}`:`#${m.seed}`),i&&$()}function Et(){document.documentElement.dataset.skin=p.theme;const e=T();for(const t of Object.values(nt))t!==e&&t.unmount();e==null||e.mount(),m&&e&&e.setPuzzle(m.seed,m.board.cols,m.board.rows),i&&Ct(),document.title=S().title,i&&$()}let J=null;if(typeof Worker<"u")try{J=new Worker(new URL(""+new URL("puzzle.worker-Bygk6O6M.js",import.meta.url).href,import.meta.url),{type:"module"})}catch{J=null}let tt=0;function ne(e,t,s,o){const n=++tt;if(!J)return new Promise(a=>setTimeout(()=>a(Jt(e,t,s,o)),16));const l=J;return new Promise(a=>{const d=r=>{r.data.id===n&&(l.removeEventListener("message",d),a(r.data.puzzle))};l.addEventListener("message",d);const c={id:n,seed:e,size:t,rules:s,opts:o};l.postMessage(c)})}function ot(e){var n;const t=St[p.size],s=S().waiting;u("status").textContent=s,(n=T())==null||n.setStatus(s),I=!0;const o=tt+1;ne(e,t,Tt(p),{onlySolvable:p.onlySolvable,difficulty:p.difficulty}).then(l=>{o===tt&&(m=l,I=!1,zt())})}function zt(){var s;i=new Gt(m.board,Tt(p),Vt),R=null,W=!1,K=!1,U=null,q.innerHTML="",P.clear();const{cols:e,rows:t}=m.board;q.style.setProperty("--cols",String(e)),q.style.setProperty("--rows",String(t)),q.style.aspectRatio=`${e} / ${t}`,i.board.cells.forEach((o,n)=>{const l=i.ids[n];if(o===null||l<0)return;const a=document.createElement("button");a.className="tile",a.style.width=`${100/e}%`,a.style.height=`${100/t}%`,a.innerHTML=`<span class="face">${o}</span>`,a.dataset.id=String(l),q.append(a),P.set(l,a)}),u("seed").textContent=p.lang==="ko"?`판 #${m.seed}`:`#${m.seed}`,location.hash=String(m.seed),(s=T())==null||s.setPuzzle(m.seed,e,t),$(),Ct()}function $(){var l;const{cols:e}=i.board,t=i.selection,s=t?i.idAt(t):-1,o=new Set(R?R.map(a=>i.idAt(a)):[]),n=new Set;i.ids.forEach((a,d)=>{if(a<0)return;n.add(a);const c=P.get(a);if(!c)return;const r=Math.floor(d/e),h=d%e;c.style.transform=`translate(${h*100}%, ${r*100}%)`,c.dataset.r=String(r),c.dataset.c=String(h),c.hidden=!1,c.classList.remove("gone"),c.classList.toggle("sel",a===s),c.classList.toggle("hint",o.has(a)),c.classList.toggle("moved",i.lastMoved.has(a)),c.setAttribute("aria-label",`${c.textContent}, ${r+1}행 ${h+1}열`)});for(const[a,d]of P)n.has(a)||(d.hidden=!0);u("st-left").textContent=String(i.remaining),u("st-moves").textContent=String(i.moves),u("st-pairs").textContent=String(i.pairCount),u("st-combo").textContent=String(i.combo),u("st-combo-box").classList.toggle("hot",i.combo>0);for(const a of document.querySelectorAll('[data-act="undo"]')){a.disabled=!i.canUndo;const d=a.querySelector(".undo-n")??a;(a.classList.contains("xl-big")||a.id==="btn-undo")&&(d.textContent=S().undoN(i.undosLeft))}oe(),le(),re(),(l=T())==null||l.update(i)}function oe(){var t;if(I)return;let e="";!i.cleared&&!i.stuck&&(e=i.selection?S().selected:S().idle),u("status").textContent=e,(t=T())==null||t.setStatus(e||S().idle)}function le(){const e=u("ov-actions"),t=S();if(i.cleared&&!W)u("ov-title").textContent=t.clearTitle,u("ov-text").textContent=t.clearText(i.moves,i.maxCombo),e.innerHTML=`<button class="btn primary" data-act="new">${t.next}</button>`,j.hidden=!1;else if(i.stuck&&K){const s=ie();u("ov-title").textContent=t.recapTitle,u("ov-text").textContent=s.kind==="fatal"?t.fatal(s.movesAgo,s.pair,s.values):s.kind==="initial"?t.initial:t.unknown,e.innerHTML=`<button class="btn" data-act="restart">${t.restart}</button><button class="btn primary" data-act="new">${t.newGame}</button>`,j.hidden=!1}else i.stuck&&!W?(u("ov-title").textContent=t.stuckTitle,u("ov-text").textContent=t.stuckText(i.remaining),e.innerHTML=(i.canUndo?`<button class="btn" data-act="undo">${t.undoN(i.undosLeft)}</button>`:"")+`<button class="btn primary" data-act="giveup">${t.giveUp}</button>`,j.hidden=!1):j.hidden=!0}function ie(){return(U==null?void 0:U.moves)!==i.moves&&(U={moves:i.moves,result:Yt(i.timeline,i.moveHistory,i.rules)}),U.result}function re(){const e=m.report,t=n=>`${(n*100).toFixed(1)}%`,s=i.cleared?null:O(i.board,i.rules,{maxStates:6e4}),o=s?s.exact?s.solvable?`<b>깰 수 있음</b> (정답 수순 ${s.solutionPaths.toLocaleString()}개, 무작위 성공률 ${t(s.randomSuccessRate)})`:`<span class="bad"><b>이미 못 깸</b></span> (최대 ${s.maxRemoved}개 더 지울 수 있음)`:"계산 한도 초과":"<b>클리어</b>";u("dev").innerHTML=[`처음 판: ${e.exact?e.solvable?"깰 수 있음":'<span class="bad">못 깸</span>':"계산 한도 초과"} · ${m.tries}번째로 뽑은 판`,e.exact&&e.solvable?`처음 판 난이도: 예상 갈림길 <b>${e.expectedForks.toFixed(1)}번</b>`+(m.difficulty==="any"?"":m.difficultyMatched?" (목표 범위 안)":' <span class="bad">(목표 범위 밖, 가장 가까운 판)</span>')+` · 외길 ${e.expectedForced.toFixed(1)}번 · 무작위 성공률 ${t(e.randomSuccessRate)} · 정답 수순 ${e.solutionPaths.toLocaleString()}개`:"",`지금 상태: ${o}`,`규칙: 대각선 ${i.rules.diagonal?"켬":"끔"} · 빈 열 당기기 ${i.rules.collapseColumns?"켬":"끔"} · 연쇄 = 직전에 떨어진 숫자(점 표시)를 바로 쓰기`].filter(Boolean).join("<br>")}let xt=0;function et(e){const t=T();if(t){t.flashStatus(e);return}X.textContent=e,X.classList.add("show"),clearTimeout(xt),xt=window.setTimeout(()=>X.classList.remove("show"),900)}function de(e){const t=P.get(e);t&&(t.classList.remove("shake"),t.offsetWidth,t.classList.add("shake"))}q.addEventListener("click",e=>{var l,a;if(I)return;const t=e.target.closest(".tile");if(!t||t.hidden)return;const s={r:Number(t.dataset.r),c:Number(t.dataset.c)},o=i.selection,n=i.tap(s);if(R=null,n.kind==="switch"){o&&de(i.idAt(n.rejected)),$();return}if(n.kind!=="match"){$();return}(l=T())==null||l.showMove(o,s,n.values),I=!0;for(const d of n.removed)(a=P.get(d))==null||a.classList.add("gone");n.chain&&et(S().chain(i.combo)),setTimeout(()=>{I=!1;for(const d of n.removed){const c=P.get(d);c&&(c.hidden=!0)}$()},160)});function st(e){if(e==="fullscreen"){Ot().then(t=>{t||et(S().fullscreenFail)});return}if(e==="tour"){$t();return}if(!(!e||I))switch(e){case"undo":if(!i.undo())return;R=null,W=!1,$();return;case"hint":{if(i.cleared)return;const t=O(i.board,i.rules,{maxStates:6e4});t.exact&&t.solvable&&t.bestLine[0]?R=t.bestLine[0]:(R=G(i.board,i.rules)[0]??null,et(t.exact?S().unsolvable:S().hintLimit)),i.clearSelection(),$();return}case"restart":zt();return;case"new":ot(lt());return;case"giveup":K=!0,$();return;case"close":W=!0,K=!1,$();return}}document.addEventListener("click",e=>{const t=e.target.closest("[data-act]");t&&!t.disabled&&st(t.dataset.act)});document.addEventListener("keydown",e=>{if(_.active){e.key==="Escape"&&(e.preventDefault(),_.close());return}e.key==="Escape"&&T()?(e.preventDefault(),T().toggleBoss()):(e.ctrlKey||e.metaKey)&&e.key==="."?(e.preventDefault(),st("hint")):(e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==="z"&&(e.preventDefault(),st("undo"))});function ce(){p={...p,size:Lt.value,difficulty:u("set-difficulty").value,diagonal:u("set-diagonal").checked,collapseColumns:u("set-collapse").checked,onlySolvable:u("set-solvable").checked},at(p),ot((m==null?void 0:m.seed)??lt())}for(const e of["set-size","set-difficulty","set-diagonal","set-collapse","set-solvable"])u(e).addEventListener("change",ce);u("set-lang").addEventListener("change",()=>{p={...p,lang:u("set-lang").value},at(p),Mt()});u("set-theme").addEventListener("change",()=>{p={...p,theme:u("set-theme").value},at(p),Et()});function lt(){return Math.floor(Math.random()*1e6)}ae();Mt();Et();const Z=Number(location.hash.slice(1));ot(Number.isInteger(Z)&&Z>0?Z:lt());
