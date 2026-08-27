/* SideKix — article behaviour. Shared by every article page. */
(function(){
  var RM = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* reading progress */
  var bar=document.getElementById('progress');
  var body=document.querySelector('.body');
  function progress(){
    if(!bar||!body) return;
    var r=body.getBoundingClientRect();
    var h=window.innerHeight||document.documentElement.clientHeight;
    var total=r.height-h*0.4;
    var done=(h*0.6)-r.top;
    var p=total>0 ? done/total : 0;
    bar.style.width=(Math.max(0,Math.min(1,p))*100)+'%';
  }

  /* build the contents from the h2s, so every article gets one for free */
  var toc=document.getElementById('toc-list');
  var heads=[].slice.call(document.querySelectorAll('.body h2'));
  if(toc && heads.length){
    heads.forEach(function(h,i){
      if(!h.id) h.id='s'+(i+1)+'-'+(h.textContent||'').toLowerCase()
        .replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'').slice(0,40);
      var li=document.createElement('li');
      var a=document.createElement('a');
      a.href='#'+h.id; a.textContent=h.textContent;
      li.appendChild(a); toc.appendChild(li);
    });
  }
  var links=[].slice.call(document.querySelectorAll('#toc-list a'));
  function mark(){
    if(!heads.length) return;
    var best=0;
    for(var i=0;i<heads.length;i++){
      if(heads[i].getBoundingClientRect().top < 140) best=i;
    }
    links.forEach(function(a,i){ a.classList.toggle('here', i===best); });
  }

  var raf=null;
  function onScroll(){
    if(raf) return;
    raf=requestAnimationFrame(function(){ raf=null; progress(); mark(); });
  }
  addEventListener('scroll',onScroll,{passive:true});
  addEventListener('resize',onScroll,{passive:true});
  progress(); mark();
})();
