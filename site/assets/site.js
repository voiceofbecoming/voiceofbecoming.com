(function(){
document.querySelectorAll(".menu nav a").forEach(function(a){a.addEventListener("click",function(){a.closest("details").removeAttribute("open")})});
var up=document.getElementById("upcoming");if(!up)return;
var t=new Date();t.setHours(0,0,0,0);var left=0;
up.querySelectorAll(".event").forEach(function(e){var d=new Date(e.getAttribute("data-date")+"T23:59:59");if(d<t){e.hidden=true}else{left++}});
var n=document.getElementById("no-upcoming");if(n)n.hidden=left>0;
})();

(function(){
window.__vob=1;
var root=document.documentElement;
var reduce=window.matchMedia&&matchMedia("(prefers-reduced-motion: reduce)").matches;
try{
/* split hero / page-head headings into rising words */
var wi=0;
function split(node){[].slice.call(node.childNodes).forEach(function(c){
  if(c.nodeType===3){var parts=c.textContent.split(/(\s+)/);var f=document.createDocumentFragment();
    parts.forEach(function(p){if(!p)return;if(/^\s+$/.test(p)){f.appendChild(document.createTextNode(" "));return;}
      var o=document.createElement("span");o.className="w";var n=document.createElement("span");n.textContent=p;n.style.setProperty("--i",wi++);o.appendChild(n);f.appendChild(o);});
    c.parentNode.replaceChild(f,c);}
  else if(c.nodeType===1&&c.tagName!=="BR"){split(c);}
});}
var heads=document.querySelectorAll(".hero h1, .page-head h1");
heads.forEach(function(h){wi=0;if(!reduce)split(h);});
[].slice.call(document.querySelectorAll(".wordmark span")).forEach(function(wm){
if(wm&&!reduce){var txt=wm.textContent;wm.textContent="";var li=0;txt.split(" ").forEach(function(word,wi2){if(wi2)wm.appendChild(document.createTextNode(" "));var wd=document.createElement("span");wd.className="wd";word.split("").forEach(function(ch){var l=document.createElement("span");l.className="l";l.textContent=ch;l.style.setProperty("--i",li++);wd.appendChild(l);});wm.appendChild(wd);});wm.style.background="none";}});
var st=document.querySelector(".statement-text"),stWords=[],pill=st?st.querySelector(".pill"):null;
if(st&&!reduce){wi=0;split(st);stWords=[].slice.call(st.querySelectorAll(".w"));}
var intro=[].slice.call(document.querySelectorAll(".hero, .page-head"));
function go(){intro.forEach(function(e){e.classList.add("is-in");});}
if(reduce)go();else{var done=false;var g=function(){if(!done){done=true;requestAnimationFrame(function(){requestAnimationFrame(go);});}};
  if(document.fonts&&document.fonts.ready)document.fonts.ready.then(g);setTimeout(g,700);}

/* scroll reveal with stagger */
var sel=["main section:not(.hero):not(.page-head) .section-head","main .feat-copy > *","main .grid > *","main .quotes > *","main .cta-band","main .signup","main details.faq","main .event","main .post-list > *","main .split > *","main .prose > *","main .checks","main .empty","main .strip","main .article > *",".foot-cta",".foot-grid > *"].join(",");
var els=[].slice.call(document.querySelectorAll(sel)).filter(function(el){return !el.closest(".hero")&&!el.closest(".page-head")&&!el.closest(".stack")&&!el.parentElement.closest(".rv");});
els.forEach(function(el){el.classList.add("rv");var p=el.parentElement,sibs=[].slice.call(p.children).filter(function(x){return els.indexOf(x)>-1;});var k=sibs.indexOf(el);el.style.setProperty("--d",(Math.min(k,6)*0.09)+"s");});
var feats=[].slice.call(document.querySelectorAll(".feat"));
var stats=[].slice.call(document.querySelectorAll(".stats"));
stats.forEach(function(s){[].slice.call(s.children).forEach(function(c,i){c.style.setProperty("--i",i);});});
var counters=[].slice.call(document.querySelectorAll("[data-count]"));
function count(el){var to=+el.dataset.count,from=+(el.dataset.from||0),suf=el.dataset.suffix||"",dur=1600,t0=null;
  if(reduce){el.textContent=to+suf;return;}
  el.textContent=from+suf;
  function step(t){if(!t0)t0=t;var p=Math.min(1,(t-t0)/dur);var e=p>=1?1:1-Math.pow(2,-10*p);el.textContent=Math.round(from+(to-from)*e)+suf;if(p<1)requestAnimationFrame(step);}
  requestAnimationFrame(step);}
var targets=els.concat(feats,stats);
if(!("IntersectionObserver" in window)||reduce){targets.forEach(function(el){el.classList.add("in");});}
else{
  counters.forEach(function(el){el.textContent=(el.dataset.from||0)+(el.dataset.suffix||"");});
  var io=new IntersectionObserver(function(es){es.forEach(function(e){if(!e.isIntersecting)return;var el=e.target;el.classList.add("in");io.unobserve(el);
    if(el.classList.contains("stats"))el.querySelectorAll("[data-count]").forEach(function(c,i){setTimeout(function(){count(c);},200+i*110);});});},{threshold:0.08,rootMargin:"0px 0px -6% 0px"});
  targets.forEach(function(el){io.observe(el);});
  /* safety: anything already scrolled past becomes visible */
  setTimeout(function(){targets.forEach(function(el){if(!el.classList.contains("in")&&el.getBoundingClientRect().bottom<0)el.classList.add("in");});},1200);
}

/* scroll: progress bar, header shadow, parallax */
var bar=document.querySelector(".progress"),hdr=document.querySelector(".site-header");
var hp=document.querySelector(".hero .hero-photo"),wide=window.matchMedia("(min-width:900px)");
var wmEl=document.querySelector(".wordmark"),bq=document.querySelector(".big-q"),cards=[].slice.call(document.querySelectorAll(".stack .card"));
cards.forEach(function(c,i){c.style.setProperty("--i",i);});
var ticking=false;
function onScroll(){var y=window.scrollY||0,H=root.scrollHeight-innerHeight;
  if(bar)bar.style.transform="scaleX("+(H>0?Math.min(1,y/H):0).toFixed(4)+")";
  if(hdr)hdr.classList.toggle("scrolled",y>10);
  if(!reduce){
    if(y<innerHeight*1.5){
      var s=1+Math.min(y,700)/700*0.06;
      if(hp)hp.style.transform="translate3d(0,"+(y*(wide.matches?0.07:0.035)).toFixed(1)+"px,0) scale("+s.toFixed(4)+")";
      
    }
    if(st){var r=st.getBoundingClientRect();if(r.top<innerHeight&&r.bottom>0){
      var p=(innerHeight*0.88-r.top)/(innerHeight*0.55+r.height*0.5);p=Math.max(0,Math.min(1,p));
      var n=Math.round(Math.min(1,p/0.72)*stWords.length);stWords.forEach(function(w,k){w.classList.toggle("on",k<n);});
      if(pill)pill.classList.toggle("on",n>=stWords.length);
      if(bq){var rr=bq.parentElement.getBoundingClientRect();bq.style.transform="translate3d(0,"+(-rr.top*0.25).toFixed(1)+"px,0)";}
    }}
    if(cards.length){cards.forEach(function(c,k){var nx=cards[k+1];if(!nx){c.style.transform="";return;}
      var a=c.getBoundingClientRect(),b2=nx.getBoundingClientRect();var d=b2.top-a.top;var h=a.height||1;var cov=Math.max(0,Math.min(1,1-d/h));
      c.style.transform="scale("+(1-cov*0.05).toFixed(4)+")";});}
  }
  ticking=false;}
window.addEventListener("scroll",function(){if(!ticking){ticking=true;requestAnimationFrame(onScroll);}},{passive:true});
window.addEventListener("resize",onScroll);onScroll();

if(!reduce&&window.matchMedia("(hover:hover) and (pointer:fine)").matches){
  document.querySelectorAll(".btn").forEach(function(bt){
    bt.addEventListener("mousemove",function(e){var r=bt.getBoundingClientRect();var dx=e.clientX-(r.left+r.width/2),dy=e.clientY-(r.top+r.height/2);bt.style.transform="translate3d("+(dx*0.22).toFixed(1)+"px,"+(dy*0.3-2).toFixed(1)+"px,0)";});
    bt.addEventListener("mouseleave",function(){bt.style.transform="";});
  });
  var cur=document.createElement("div");cur.className="cursor";cur.setAttribute("aria-hidden","true");document.body.appendChild(cur);
  var mx=-100,my=-100,cx=-100,cy=-100,run=false;
  function loop(){cx+=(mx-cx)*0.2;cy+=(my-cy)*0.2;cur.style.transform="translate3d("+cx.toFixed(1)+"px,"+cy.toFixed(1)+"px,0)";if(Math.abs(mx-cx)>0.3||Math.abs(my-cy)>0.3)requestAnimationFrame(loop);else run=false;}
  document.addEventListener("mousemove",function(e){mx=e.clientX;my=e.clientY;cur.classList.add("on");cur.classList.toggle("big",!!e.target.closest("a,button,summary"));if(!run){run=true;requestAnimationFrame(loop);}},{passive:true});
  document.addEventListener("mouseleave",function(){cur.classList.remove("on");});
}
}catch(err){root.classList.remove("js");}
})();


/* v7 motion: glide scroll, hero-to-card, stacked panels, statement zoom */
(function(){
var root=document.documentElement;
var reduce=window.matchMedia&&matchMedia("(prefers-reduced-motion: reduce)").matches;
var main=document.getElementById("main");if(reduce||!main)return;
try{
var fine=matchMedia("(hover:hover) and (pointer:fine)").matches;
var wide=matchMedia("(min-width:900px)");
var hero=main.querySelector(":scope > .hero"),hdr=document.querySelector(".site-header");
var kids=[].slice.call(main.children);
var panels=kids.filter(function(el){return el.tagName==="SECTION"&&el!==hero&&!el.classList.contains("page-head");});
var overs=hero?kids.slice(kids.indexOf(hero)+1).filter(function(el){return panels.indexOf(el)<0;}):[];
var first=hero?kids[kids.indexOf(hero)+1]:null;
var stt=document.querySelector(".statement-text");
root.classList.add("mo");
function dimEl(p){var d=document.createElement("i");d.className="mo-dim";d.setAttribute("aria-hidden","true");p.appendChild(d);return d;}
var heroDim=hero?dimEl(hero):null;
var pd=panels.map(dimEl);
var hH=0,stick=[],heroTop=0,on=false;
function clamp(v){return v<0?0:v>1?1:v;}
function eo(t){return 1-Math.pow(1-t,3);}
function layout(){
  hH=hdr?hdr.getBoundingClientRect().height:0;
  on=wide.matches&&!!hero;root.classList.toggle("mo-panels",on);
  heroTop=hero?Math.min(hH,innerHeight-hero.offsetHeight):0;
  if(hero)hero.style.top=on?heroTop+"px":"";
  stick=panels.map(function(p,i){var t=Math.min(hH,innerHeight-p.offsetHeight);p.style.top=on?t+"px":"";p.style.zIndex=on?(3+i):"";
    p.style.transformOrigin="50% "+(((hH+innerHeight)/2)-t).toFixed(0)+"px";return t;});
  if(hero)hero.style.transformOrigin=on?"50% "+(((hH+innerHeight)/2)-heroTop).toFixed(0)+"px":"50% 100%";
  frame();
}
function frame(){
  var ih=innerHeight;
  if(hero){var e=0;
    if(on){if(first){var ft=first.getBoundingClientRect().top,base=Math.min(ih,ft+scrollY);e=clamp((base-ft)/Math.max(1,base-heroTop));}}
    else{var hr=hero.getBoundingClientRect();e=clamp((hH-hr.top)/Math.max(1,hr.height*0.9));}
    var k=eo(e),sc=on?1-0.1*k:1-0.07*k;
    hero.style.transform=e>0?"scale("+sc.toFixed(4)+")":"";
    hero.style.borderRadius=e>0?((on?32:24)*Math.min(1,k*1.6)).toFixed(1)+"px":"";
    heroDim.style.opacity=(k*(on?0.42:0.3)).toFixed(3);
    hero.style.visibility=(on&&first&&first.getBoundingClientRect().top<=hH-ih*0.5)?"hidden":"";
  }
  if(on){for(var i=0;i<panels.length;i++){var p=panels[i],nx=panels[i+1],c=0;
      if(nx){var nt=nx.getBoundingClientRect().top;c=clamp(1-(nt-stick[i])/Math.max(1,ih-stick[i]));}
      var k2=eo(c);p.style.transform=c>0?"scale("+(1-0.05*k2).toFixed(4)+")":"";pd[i].style.opacity=(k2*0.5).toFixed(3);
      var n2=panels[i+2];p.style.visibility=(n2&&n2.getBoundingClientRect().top<=hH+1&&n2.offsetHeight>=ih-hH-2)?"hidden":"";}}
  else{panels.forEach(function(p,i){p.style.transform="";p.style.visibility="";pd[i].style.opacity=0;});}
  if(stt){var r=stt.parentElement.getBoundingClientRect();if(r.top<ih&&r.bottom>0){var q=eo(clamp((ih-r.top)/(ih*0.8)));
      stt.style.transform="translate3d(0,"+((1-q)*50).toFixed(1)+"px,0) scale("+((wide.matches?0.85:0.9)+(wide.matches?0.15:0.1)*q).toFixed(4)+")";}}
}
var tk=false;function req(){if(!tk){tk=true;requestAnimationFrame(function(){tk=false;frame();});}}
window.addEventListener("scroll",req,{passive:true});
window.addEventListener("resize",layout);
if(window.ResizeObserver){var ro=new ResizeObserver(function(){layout();});kids.forEach(function(k){ro.observe(k);});}
if(document.fonts&&document.fonts.ready)document.fonts.ready.then(layout);
window.addEventListener("load",layout);
layout();

/* glide: inertial wheel scrolling on mouse/trackpad devices only */
if(fine){
  root.classList.add("glide");
  var cur=scrollY,tgt=scrollY,run=false,last=0,set=-1;
  var maxY=function(){return Math.max(0,root.scrollHeight-innerHeight);};
  var step=function(t){var dt=Math.min(64,t-(last||t-16));last=t;var d=tgt-cur;cur+=d*(1-Math.exp(-dt/105));
    if(Math.abs(d)<0.4){cur=tgt;run=false;}set=Math.round(cur);window.scrollTo(0,cur);if(run)requestAnimationFrame(step);else last=0;};
  var go=function(y){if(!run){cur=scrollY;}tgt=Math.max(0,Math.min(maxY(),y));if(!run){run=true;last=0;requestAnimationFrame(step);}};
  window.addEventListener("wheel",function(e){
    if(e.ctrlKey||e.defaultPrevented)return;
    if(Math.abs(e.deltaX)>Math.abs(e.deltaY))return;
    for(var n=e.target;n&&n.nodeType===1&&n!==document.body;n=n.parentElement){if(n.scrollHeight>n.clientHeight+2){var oy=getComputedStyle(n).overflowY;if(oy==="auto"||oy==="scroll")return;}}
    if(document.querySelector("details.menu[open]"))return;
    e.preventDefault();
    var dy=e.deltaY*(e.deltaMode===1?40:e.deltaMode===2?innerHeight:1);
    go((run?tgt:scrollY)+dy);
  },{passive:false});
  window.addEventListener("scroll",function(){if(run&&Math.abs(scrollY-set)>4&&Math.abs(scrollY-Math.round(cur))>4){run=false;}if(!run){cur=tgt=scrollY;}},{passive:true});
  document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest('a[href^="#"]');if(!a)return;var id=a.getAttribute("href").slice(1);var t=id?document.getElementById(id):null;
    if(!id){e.preventDefault();go(0);return;}if(t){e.preventDefault();go(t.getBoundingClientRect().top+scrollY-hH-10);}});
}
}catch(err){root.classList.remove("mo","mo-panels","glide");}
})();
