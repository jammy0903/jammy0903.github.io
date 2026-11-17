var E=Object.defineProperty;var R=(a,t,e)=>t in a?E(a,t,{enumerable:!0,configurable:!0,writable:!0,value:e}):a[t]=e;var d=(a,t,e)=>R(a,typeof t!="symbol"?t+"":t,e);import{j as L}from"./i18n-q_CoB2ph.js";class w{constructor(t){d(this,"home",null);this.el=t}moveInto(t){!this.home&&this.el.parentNode&&(this.home={parent:this.el.parentNode,next:this.el.nextSibling}),t.append(this.el)}restore(){this.home&&(this.home.parent.insertBefore(this.el,this.home.next),this.home=null)}}const y=8,M=6,T=3,v="retryMatrix.ts",A=new Set(["import","type","from","export","const","function","return","as","true","false","null","async","await","new","if","else","interface","readonly","default"]),C=new Set(["number","string","boolean","RetryPolicy","Route","Record","Promise","Response","Request"]),$=a=>a.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");function k(a){const t=a.match(/^(\s*)(\/\/.*|\/\*\*?.*|\*.*)$/);if(t)return`${t[1]}<span class="t-com">${$(t[2])}</span>`;const e=/('[^']*'|`[^`]*`)|(\b\d+(?:\.\d+)?\b)|([A-Za-z_$][\w$]*)|(\s+)|(.)/g;let s="",i;for(;i=e.exec(a);){const[n,l,c,r]=i;if(l)s+=`<span class="t-str">${$(l)}</span>`;else if(c)s+=`<span class="t-num">${c}</span>`;else if(r){const h=a.slice(e.lastIndex).trimStart()[0];A.has(r)?s+=`<span class="t-kw">${r}</span>`:C.has(r)?s+=`<span class="t-type">${r}</span>`:/^[A-Z][A-Z0-9_]+$/.test(r)?s+=`<span class="t-const">${r}</span>`:h==="("?s+=`<span class="t-fn">${r}</span>`:s+=`<span class="t-var">${r}</span>`}else s+=$(n)}return s}function I(a,t){const e=`  [${new Array(a).fill("null").join(", ")}],`;return["import type { RetryPolicy } from '../types/network';","import { DEFAULT_BACKOFF } from './constants';","","/**"," * Retry backoff matrix (x100ms). rows = region, cols = attempt."," * TODO(perf): rebalance before Q4 release (PERF-1123)"," */","export const RETRY_MATRIX: (number | null)[][] = [",...new Array(t).fill(e),"];","","export const MATRIX_STATS = {","  remaining: 0,","  resolved: 0,","  candidates: 0,","  streak: 0,","  maxStreak: 0,","} as const;","","export function nextBackoff(region: number, attempt: number): number {","  const v = RETRY_MATRIX[region]?.[attempt] ?? null;","  return v === null ? DEFAULT_BACKOFF : v * 100;","}","","export const policy: RetryPolicy = {","  maxAttempts: RETRY_MATRIX[0].length,","  jitter: true,","  retryOn: ['ECONNRESET', 'ETIMEDOUT', 503, 429],","};"]}const O=["import type { Route } from './types';","import { lazy } from './lazy';","","export const routes: Route[] = [","  { path: '/', component: lazy(() => import('./pages/Dashboard')) },","  { path: '/orders', component: lazy(() => import('./pages/Orders')) },","  { path: '/orders/:id', component: lazy(() => import('./pages/OrderDetail')) },","  { path: '/settlement', component: lazy(() => import('./pages/Settlement')) },","  { path: '/settings', component: lazy(() => import('./pages/Settings')), auth: true },","];","","export async function prefetch(path: string): Promise<void> {","  const route = routes.find((r) => r.path === path);","  if (!route) return;","  await route.component.preload?.();","}","","// TODO: move auth guard into middleware once API v3 ships","export function requiresAuth(path: string): boolean {","  return routes.some((r) => r.path === path && r.auth === true);","}"],q=["remaining","resolved","candidates","streak","maxStreak"];class N{constructor(t,e){d(this,"root");d(this,"code");d(this,"alt");d(this,"term");d(this,"pop");d(this,"board");d(this,"settings");d(this,"mounted",!1);d(this,"cols",5);d(this,"rows",4);d(this,"statusText","Ready");d(this,"flashTimer",0);this.board=new w(t),this.settings=new w(e),this.root=document.createElement("div"),this.root.className="dv",this.root.hidden=!0,this.root.innerHTML=`
      <div class="dv-title">
        <span class="dv-logo" aria-hidden="true"></span>
        <span class="dv-menu">File&nbsp;&nbsp;Edit&nbsp;&nbsp;Selection&nbsp;&nbsp;View&nbsp;&nbsp;Go&nbsp;&nbsp;Run&nbsp;&nbsp;Terminal&nbsp;&nbsp;Help</span>
        <button class="dv-guide" data-act="tour" id="dv-guide">↻ <span data-i18n="dv.guide"></span></button>
        <span class="dv-search">⌕ web-console</span>
        <span class="dv-win">
          <button tabindex="-1" title="Minimize">─</button>
          <button data-act="fullscreen" id="dv-full" title="Maximize">☐</button>
          <button tabindex="-1" title="Close">✕</button>
        </span>
      </div>
      <div class="dv-main">
        <div class="dv-activity">
          <span class="on" title="Explorer">⧉</span><span title="Search">⌕</span><span title="Source Control">⑂</span>
          <span title="Run and Debug">▷</span><span title="Extensions">⊞</span>
          <button class="dv-gear" id="dv-gear" title="Manage">⚙</button>
        </div>
        <div class="dv-side">
          <div class="dv-side-h">EXPLORER</div>
          <div class="dv-tree">
            <div class="dv-proj">⌄ WEB-CONSOLE</div>
            <div class="d1">› .github</div>
            <div class="d1">› node_modules</div>
            <div class="d1">⌄ src</div>
            <div class="d2">› api</div>
            <div class="d2">› components</div>
            <div class="d2">⌄ config</div>
            <div class="d3 ts">constants.ts</div>
            <div class="d3 ts">featureFlags.ts</div>
            <div class="d3 ts on" id="dv-file-main">${v}</div>
            <div class="d3 ts" id="dv-file-alt">routes.ts</div>
            <div class="d2">› hooks</div>
            <div class="d2">› pages</div>
            <div class="d2 tsx">App.tsx</div>
            <div class="d2 tsx">main.tsx</div>
            <div class="d1 dim">.env.example</div>
            <div class="d1 json">package.json</div>
            <div class="d1 md">README.md</div>
            <div class="d1 json">tsconfig.json</div>
          </div>
          <div class="dv-side-h small">› OUTLINE</div>
          <div class="dv-side-h small">› TIMELINE</div>
        </div>
        <div class="dv-editor">
          <div class="dv-tabs">
            <span class="dv-tab on" id="dv-tab-main"><i class="ts">TS</i>${v}<b id="dv-dirty">×</b></span>
            <span class="dv-tab" id="dv-tab-alt"><i class="ts">TS</i>routes.ts<b>×</b></span>
            <span class="dv-tab"><i class="tsx">⚛</i>App.tsx<b>×</b></span>
            <span class="dv-tools">
              <button data-act="undo" title="Undo (Ctrl+Z)">↶</button>
              <button data-act="hint" title="Quick Fix (Ctrl+.)">✦</button>
              <button data-act="restart" title="Revert File">⟲</button>
              <button data-act="new" title="New File">＋</button>
              <span>⋯</span>
            </span>
          </div>
          <div class="dv-crumbs" id="dv-crumbs">src › config › ${v} › <span class="t-const">RETRY_MATRIX</span></div>
          <div class="dv-code" id="dv-code"></div>
          <div class="dv-code" id="dv-alt" hidden></div>
          <div class="dv-panel">
            <div class="dv-ptabs"><span>PROBLEMS</span><span>OUTPUT</span><span>DEBUG CONSOLE</span><span class="on">TERMINAL</span><span>PORTS</span></div>
            <div class="dv-term" id="dv-term"></div>
          </div>
        </div>
      </div>
      <div class="dv-status">
        <span>⑂ main*</span><span>⟳</span><span id="dv-problems">⊗ 0  ⚠ 0</span>
        <span id="dv-msg">Ready</span>
        <span class="r" id="dv-undo"></span>
        <span class="r" id="dv-pos">Ln 1, Col 1</span><span>Spaces: 2</span><span>UTF-8</span><span>LF</span><span>{ } TypeScript</span><span>🔔</span>
      </div>
      <div class="dv-pop" id="dv-pop" hidden></div>
    `,document.body.append(this.root);const s=i=>this.root.querySelector(`#${i}`);this.code=s("dv-code"),this.alt=s("dv-alt"),this.term=s("dv-term"),this.pop=s("dv-pop"),this.alt.innerHTML=this.renderLines(O),s("dv-gear").addEventListener("click",i=>{i.stopPropagation(),this.pop.hidden=!this.pop.hidden}),document.addEventListener("click",i=>{!this.pop.hidden&&!this.pop.contains(i.target)&&(this.pop.hidden=!0)}),s("dv-tab-alt").addEventListener("click",()=>this.setBoss(!0)),s("dv-file-alt").addEventListener("click",()=>this.setBoss(!0)),s("dv-tab-main").addEventListener("click",()=>this.setBoss(!1)),s("dv-file-main").addEventListener("click",()=>this.setBoss(!1)),this.log("$ npm run dev","cmd"),this.log("> web-console@2.14.0 dev","dim"),this.log("> node scripts/dev-server.mjs","dim"),this.log("  ready in 412 ms","ok"),this.log("  ➜  Local:   http://localhost:3000/",""),this.log("  ➜  Network: use --host to expose","dim")}renderLines(t,e=!1){return t.map((s,i)=>{let n=k(s);if(e){const l=q.find(c=>s.trim().startsWith(`${c}:`));l&&(n=`  <span class="t-var">${l}</span>: <span class="t-num" data-stat="${l}">0</span>,`)}return`<div class="dv-ln" data-ln="${i}"><span class="no">${i+1}</span><span class="tx">${n||" "}</span></div>`}).join("")}mount(){this.mounted||(this.mounted=!0,this.root.hidden=!1,this.board.moveInto(this.code),this.settings.moveInto(this.pop),this.layout())}unmount(){this.mounted&&(this.mounted=!1,this.board.restore(),this.settings.restore(),this.root.hidden=!0,this.setBoss(!1))}setPuzzle(t,e,s){this.cols=e,this.rows=s,this.layout(),this.log(`[watch] change detected in src/config/${v}, rebuilding…`,"dim"),this.log(`✓ built in ${180+t%240}ms`,"ok")}layout(){if(!this.mounted)return;const t=this.code.querySelector(".board-wrap");this.code.innerHTML=this.renderLines(I(this.cols,this.rows),!0),this.code.insertAdjacentHTML("afterbegin",'<div class="dv-curline" id="dv-curline" hidden></div>'),t?this.code.append(t):this.board.moveInto(this.code);const e=this.code.querySelector(".board-wrap");e.style.top=`calc(${y} * var(--lh) + var(--pad-top))`,e.style.left=`calc(var(--gut) + ${T}ch)`}update(t){if(!this.mounted)return;const e={remaining:t.remaining,resolved:t.moves,candidates:t.pairCount,streak:t.combo,maxStreak:t.maxCombo};for(const n of this.code.querySelectorAll("[data-stat]"))n.textContent=String(e[n.dataset.stat]??0);this.root.querySelector("#dv-dirty").textContent=t.moves>0?"●":"×",this.root.querySelector("#dv-problems").textContent=`⊗ 0  ⚠ ${t.pairCount}`,this.root.querySelector("#dv-undo").textContent=`↶ ${t.undosLeft}`;const s=this.root.querySelector("#dv-curline"),i=t.selection;i?(this.root.querySelector("#dv-pos").textContent=`Ln ${y+i.r+1}, Col ${T+i.c*M+1}`,s&&(s.hidden=!1,s.style.top=`calc(${y+i.r} * var(--lh) + var(--pad-top))`)):s&&(s.hidden=!0)}showMove(t,e){this.mounted&&this.log(`[hmr] update /src/config/${v} (RETRY_MATRIX[${t.r}][${t.c}], [${e.r}][${e.c}])`,"hmr")}setStatus(t){this.statusText=t,this.flashTimer||(this.root.querySelector("#dv-msg").textContent=t)}flashStatus(t){const e=this.root.querySelector("#dv-msg");e.textContent=t,this.log(`[hmr] ${t}`,"hmr"),clearTimeout(this.flashTimer),this.flashTimer=window.setTimeout(()=>{this.flashTimer=0,e.textContent=this.statusText},1400)}setLang(t){L(this.root,t)}toggleBoss(){this.setBoss(!this.root.classList.contains("boss"))}setBoss(t){this.root.classList.toggle("boss",t),this.alt.hidden=!t,this.code.hidden=t,this.root.querySelector("#dv-tab-main").classList.toggle("on",!t),this.root.querySelector("#dv-tab-alt").classList.toggle("on",t),this.root.querySelector("#dv-file-main").classList.toggle("on",!t),this.root.querySelector("#dv-file-alt").classList.toggle("on",t),this.root.querySelector("#dv-crumbs").innerHTML=t?'src › config › routes.ts › <span class="t-var">routes</span>':`src › config › ${v} › <span class="t-const">RETRY_MATRIX</span>`}log(t,e){const s=new Date,i=[s.getHours(),s.getMinutes(),s.getSeconds()].map(l=>String(l).padStart(2,"0")).join(":"),n=document.createElement("div");for(n.className=`tl ${e}`,n.textContent=e==="hmr"?`${i} ${t}`:t,this.term.append(n);this.term.childElementCount>60;)this.term.firstElementChild.remove();this.term.scrollTop=this.term.scrollHeight}}const b=6;class P{constructor(){d(this,"root");d(this,"steps",[]);d(this,"index",0);d(this,"onClose",null);d(this,"labels",{next:"다음",prev:"이전",done:"시작!",close:"닫기"});d(this,"redraw",()=>this.draw());this.root=document.createElement("div"),this.root.className="tour",this.root.hidden=!0,this.root.setAttribute("role","dialog"),this.root.setAttribute("aria-modal","true"),document.body.append(this.root),this.root.addEventListener("click",t=>{var s;const e=(s=t.target.closest("[data-tour]"))==null?void 0:s.dataset.tour;e==="close"?this.close():e==="next"?this.go(this.index+1):e==="prev"&&this.go(this.index-1),t.stopPropagation()})}get active(){return!this.root.hidden}start(t,e,s){s&&(this.labels=s),this.steps=t,this.onClose=e,this.root.hidden=!1,window.addEventListener("resize",this.redraw),this.go(0)}close(){if(!this.active)return;this.root.hidden=!0,this.root.innerHTML="",window.removeEventListener("resize",this.redraw);const t=this.onClose;this.onClose=null,t==null||t()}go(t){if(t>=this.steps.length){this.close();return}this.index=Math.max(0,t),this.draw()}draw(){const t=this.steps[this.index];if(!t)return;const e=window.innerWidth,s=window.innerHeight,i=t.targets().filter(o=>!!o&&o.offsetParent!==null).map(o=>o.getBoundingClientRect()).filter(o=>o.width>0&&o.height>0).map(o=>({x:Math.max(0,o.left-b),y:Math.max(0,o.top-b),w:Math.min(e,o.width+b*2),h:Math.min(s,o.height+b*2)})),n=i.map(o=>`<rect x="${o.x}" y="${o.y}" width="${o.w}" height="${o.h}" rx="6" fill="black"/>`).join(""),l=i.map(o=>`<div class="tour-ring" style="left:${o.x}px;top:${o.y}px;width:${o.w}px;height:${o.h}px"></div>`).join(""),c=this.index===this.steps.length-1,r=this.labels,h=this.steps.map((o,u)=>`<i class="${u===this.index?"on":""}"></i>`).join(""),m=`
      <div class="tour-card" id="tour-card">
        <button class="tour-x" data-tour="close" aria-label="${r.close}">✕</button>
        <h3>${t.title}</h3>
        ${t.text?`<p>${t.text}</p>`:""}
        <div class="tour-btns">
          <span class="tour-dots" aria-label="${this.index+1} / ${this.steps.length}">${h}</span>
          ${this.index>0?`<button data-tour="prev">${r.prev}</button>`:""}
          <button class="primary" data-tour="next">${c?r.done:r.next}</button>
        </div>
      </div>`;this.root.innerHTML=`
      <svg class="tour-dim" width="${e}" height="${s}" aria-hidden="true">
        <defs><mask id="tour-mask"><rect width="${e}" height="${s}" fill="white"/>${n}</mask></defs>
        <rect width="${e}" height="${s}" fill="rgba(0,0,0,0.62)" mask="url(#tour-mask)"/>
      </svg>
      ${l}
      <div class="tour-arrow" id="tour-arrow" hidden></div>
      ${m}`,this.place(i[0],e,s)}place(t,e,s){const i=this.root.querySelector("#tour-card"),n=this.root.querySelector("#tour-arrow"),l=i.offsetWidth,c=i.offsetHeight,r=46,h=x=>Math.min(Math.max(12,x),e-l-12),m=x=>Math.min(Math.max(12,x),s-c-12);if(!t){i.style.left=`${(e-l)/2}px`,i.style.top=`${(s-c)/2}px`;return}const o=t.x+t.w/2,u=t.y+t.h/2;let f,g,p;if(t.y+t.h+r+c<s)p="up",f=h(o-l/2),g=t.y+t.h+r;else if(t.y-r-c>0)p="down",f=h(o-l/2),g=t.y-r-c;else if(t.x+t.w+r+l<e)p="left",f=t.x+t.w+r,g=m(u-c/2);else if(t.x-r-l>0)p="right",f=t.x-r-l,g=m(u-c/2);else{i.style.left=`${h(o-l/2)}px`,i.style.top=`${m(t.y+t.h-c-16)}px`;return}i.style.left=`${f}px`,i.style.top=`${g}px`,n.hidden=!1,n.className=`tour-arrow ${p}`;const S={up:"⬆",down:"⬇",left:"⬅",right:"➡"}[p];n.textContent=S,p==="up"?(n.style.left=`${o-16}px`,n.style.top=`${t.y+t.h+6}px`):p==="down"?(n.style.left=`${o-16}px`,n.style.top=`${t.y-40}px`):p==="left"?(n.style.left=`${t.x+t.w+6}px`,n.style.top=`${u-18}px`):(n.style.left=`${t.x-40}px`,n.style.top=`${u-18}px`)}}function D(a){try{return localStorage.getItem(`gnm.tour.${a}.v1`)==="1"}catch{return!0}}function _(a){try{localStorage.setItem(`gnm.tour.${a}.v1`,"1")}catch{}}async function j(){var a;try{if(document.fullscreenElement)return await document.exitFullscreen(),!0;await document.documentElement.requestFullscreen()}catch{return!1}try{const t=navigator.keyboard;await((a=t==null?void 0:t.lock)==null?void 0:a.call(t,["Escape"]))}catch{}return!0}export{w as B,N as D,P as T,D as a,k as h,_ as m,j as t};
