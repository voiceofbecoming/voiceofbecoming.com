(function(){
document.querySelectorAll(".menu nav a").forEach(function(a){a.addEventListener("click",function(){a.closest("details").removeAttribute("open")})});
var up=document.getElementById("upcoming");if(!up)return;
var t=new Date();t.setHours(0,0,0,0);var left=0;
up.querySelectorAll(".event").forEach(function(e){var d=new Date(e.getAttribute("data-date")+"T23:59:59");if(d<t){e.hidden=true}else{left++}});
var n=document.getElementById("no-upcoming");if(n)n.hidden=left>0;
})();
