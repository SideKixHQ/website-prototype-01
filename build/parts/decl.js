
/* ---- the signature wall ----
   Every name is drawn in one of six hands at a slight angle, chosen from the
   name itself rather than at random, so a person's signature looks the same
   every time the page loads. Scanning for a name you know is the point, so
   there is a search that lifts the match rather than hiding the rest.

   Reading comes from signatures.json. Writing needs an endpoint, which is the
   one part that cannot be static: see WRITE below. */
(function(){
  var wall=document.getElementById('sigwall');
  if(!wall) return;
  var countEl=document.getElementById('sigcount'),
      box=document.getElementById('signbox');
  var ALL=[];

  function esc(s){ return String(s==null?'':s).replace(/[&<>"]/g,function(c){
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }

  /* a stable number from the name, so the same person always gets the same
     hand and the same tilt */
  function hash(s){
    var h=0; for(var i=0;i<s.length;i++){ h=(h*31+s.charCodeAt(i))|0; }
    return Math.abs(h);
  }

  function render(list){
    /* ---- scattered, angled, never touching ----
       A jittered grid alone produces overlap, which is what a signed sleeve
       looks like but is not what is wanted here. So the names are placed, then
       measured, then pushed apart until nothing collides.

       Measuring matters because a rotated name needs a bigger box than its
       own width: a 14 degree tilt on a long name adds real height. Each box
       is the rotated bounding box, not the flat one, so the gaps hold at every
       angle. */
    var n=list.length;
    if(!n){ wall.innerHTML=''; countEl.textContent=''; return; }

    var cols = n<=6 ? 3 : n<=12 ? 4 : n<=24 ? 5 : n<=48 ? 6 : 7;
    var rows = Math.ceil(n/cols);
    var H = rows*128 + 70;          /* provisional; corrected once measured */
    wall.style.height = H + 'px';

    /* shuffled by name, so signing order is not display order */
    var order=list.slice().sort(function(a,b){
      return hash(a.name+'|cell') - hash(b.name+'|cell'); });

    /* 1. draw them so they can be measured */
    wall.innerHTML=order.map(function(s){
      var h=hash(s.name);
      var hand=(h%6)+1;
      var tilt=(((h>>4)%25)-12);
      var size=0.84+((h>>7)%8)*0.05;
      return '<span class="sig sig-h'+hand+'" '+
        'style="--r:'+tilt+'deg;--z:'+size.toFixed(2)+'" '+
        'data-n="'+esc(s.name.toLowerCase())+'" tabindex="0" '+
        'aria-label="'+esc(s.name)+'">'+esc(s.name)+'</span>';
    }).join('');

    var els=[].slice.call(wall.querySelectorAll('.sig'));
    var W = wall.clientWidth || 880;

    var items=els.map(function(el,i){
      var h=hash(el.getAttribute('data-n'));
      var r=el.getBoundingClientRect();
      var deg=parseFloat(el.style.getPropertyValue('--r'))||0;
      var rad=Math.abs(deg*Math.PI/180);
      var bw=r.width||120, bh=r.height||30;
      /* the rotated bounding box, plus a little air so nothing sits flush */
      /* the padding is the gap between neighbours. The relaxation settles at
         exactly zero separation, so the air has to be built into the box. */
      var w2=(bw*Math.cos(rad)+bh*Math.sin(rad))+30;
      var h2=(bw*Math.sin(rad)+bh*Math.cos(rad))+22;

      var cx=(i%cols), cy=Math.floor(i/cols);
      var jx=(((h>>2)%100)/100-.5)*0.9;
      var jy=(((h>>9)%100)/100-.5)*0.8;
      return {
        el:el,
        x:((cx+.5+jx)/cols)*W,
        y:((cy+.5+jy)/rows)*H,
        w:w2, h:h2
      };
    });

    /* the height above was a guess from the count. Now that every box has
       been measured, the sheet is sized to the area they genuinely need. A
       relaxation cannot separate names that do not fit, which is what caused
       overlap to reappear at thirty names and worsen from there. The 1.55
       is packing slack: a scattered layout wastes space by design, and
       without it the names end up in neat rows again. */
    var need=0;
    items.forEach(function(it){ need += it.w*it.h; });
    var wantH = Math.max(H, Math.ceil((need*1.55)/W) + 90);
    if(wantH!==H){
      items.forEach(function(it){ it.y = it.y/H*wantH; });
      H=wantH; wall.style.height=H+'px';
    }

    /* 2. place them one at a time, and only ever where there is room.
       Relaxation was the wrong tool: pushing everybody apart at once never
       settled, because separating one pair pushed another together, and the
       clamp that kept names on the sheet shoved them back into each other.

       This cannot fail to converge. Each name is offered its jittered target
       first, and if that spot is taken it spirals outward until it finds
       clear space. Biggest first, because a long name has fewer places it can
       go and should get the choice. */
    items.sort(function(a,b){ return (b.w*b.h)-(a.w*a.h); });

    var placed=[];
    function clear(x,y,it){
      if(x-it.w/2<4 || x+it.w/2>W-4 || y-it.h/2<4 || y+it.h/2>H-4) return false;
      for(var i=0;i<placed.length;i++){
        var o=placed[i];
        if((it.w+o.w)/2 - Math.abs(x-o.x) > 0) {
          if((it.h+o.h)/2 - Math.abs(y-o.y) > 0) return false;
        }
      }
      return true;
    }

    items.forEach(function(it){
      if(clear(it.x,it.y,it)){ it.px=it.x; it.py=it.y; placed.push({x:it.x,y:it.y,w:it.w,h:it.h}); return; }
      /* an outward spiral from where it wanted to be, so it lands as near to
         its scattered position as the space allows */
      var step=13, found=false;
      for(var ring=1; ring<160 && !found; ring++){
        var r=ring*step;
        for(var a=0; a<ring*7; a++){
          var ang=(a/(ring*7))*Math.PI*2 + (ring*0.7);
          var nx=it.x+Math.cos(ang)*r, ny=it.y+Math.sin(ang)*r*0.72;
          if(clear(nx,ny,it)){
            it.px=nx; it.py=ny; placed.push({x:nx,y:ny,w:it.w,h:it.h});
            found=true; break;
          }
        }
      }
      if(!found){
        /* nowhere left: the sheet grows and it goes at the bottom, which is
           better than dropping a name or letting one sit on another */
        H += it.h + 16;
        wall.style.height = H + 'px';
        it.px=Math.max(it.w/2+4, Math.min(W-it.w/2-4, it.x));
        it.py=H - it.h/2 - 8;
        placed.push({x:it.px,y:it.py,w:it.w,h:it.h});
      }
    });

    /* 3. and place them */
    items.forEach(function(it){
      it.el.style.left=(it.px/W*100).toFixed(3)+'%';
      it.el.style.top =(it.py/H*100).toFixed(3)+'%';
    });

    countEl.textContent = n===1 ? 'One name so far' : n+' names so far';
  }


  /* ---- WRITE ----
     Signing needs somewhere to write to, which a static site cannot do. This
     posts to /api/sign and expects the new list back. Until that endpoint
     exists the form says so plainly rather than pretending it worked. */
  function form(){
    box.innerHTML=
      '<p class="sign-note">Signatures are added when someone joins SideKix. '+
      'If you have already joined, add your name here.</p>'+
      '<div class="sign-row">'+
        '<input id="signname" type="text" maxlength="60" placeholder="Your name or company" '+
          'aria-label="Your name or company">'+
        '<button type="button" class="kx-mag kx-trace kx-gold" id="signgo">Sign it</button>'+
      '</div>'+
      '<p class="sign-msg" id="signmsg" role="status"></p>';
  }
  form();

  document.addEventListener('click', function(e){
    if(!e.target || !e.target.closest || !e.target.closest('#signgo')) return;
    var name=(document.getElementById('signname').value||'').trim();
    var msg=document.getElementById('signmsg');
    if(name.length<2){ msg.textContent='A name is needed.'; return; }
    msg.textContent='Signing...';

    fetch('/api/sign', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({name:name})
    }).then(function(r){
      if(!r.ok) throw new Error(r.status);
      return r.json();
    }).then(function(d){
      ALL=(d.signatures||ALL);
      render(ALL);
      box.innerHTML='<p class="sign-done">Added. Look for your name above.</p>';
      /* the only remaining use of data-n: pointing you at the name you just
         added, so you do not have to hunt for it */
      var el=wall.querySelector('[data-n="'+name.toLowerCase().replace(/"/g,'')+'"]');
      if(el){ el.classList.add('sig-hit');
        if(el.scrollIntoView) try{ el.scrollIntoView({behavior:'smooth',block:'center'}); }catch(x){} }
    }).catch(function(){
      msg.textContent='Signing is not switched on yet. The wall below is live; '+
        'adding a name needs the endpoint at /api/sign.';
    });
  });

  fetch('signatures.json').then(function(r){ return r.json(); }).then(function(d){
    ALL=d.signatures||[];
    render(ALL);
  }).catch(function(){
    countEl.textContent='';
    wall.innerHTML='<p class="sign-note">The signatures could not load.</p>';
  });
})();
