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
var wm=document.querySelector(".wordmark span");
if(wm&&!reduce){var txt=wm.textContent;wm.textContent="";var li=0;txt.split("").forEach(function(ch){if(ch===" "){wm.appendChild(document.createTextNode(" "));return;}var l=document.createElement("span");l.className="l";l.textContent=ch;l.style.setProperty("--i",li++);wm.appendChild(l);});wm.style.background="none";}
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
      if(hp)hp.style.transform="translate3d(0,"+(y*(wide.matches?0.14:0.06)).toFixed(1)+"px,0) scale("+s.toFixed(4)+")";
      if(wmEl)wmEl.style.transform="translate3d(0,"+(y*(wide.matches?0.22:0.1)).toFixed(1)+"px,0)";
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
