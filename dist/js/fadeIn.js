function fadeIn(o){let e=document.querySelector(o);e.style.opacity=0;const t={root:null,threshold:.1,rootMargin:"-15%"};document.addEventListener("scroll",function(){new IntersectionObserver(n=>{n.forEach(r=>{const s=r.intersectionRatio*1.3;e.style.opacity=s.toFixed(2)})},t).observe(e)})}
