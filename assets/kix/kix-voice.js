/* KixVoice: the Kix voice visual, adapted from James's "Sidekix · Kix voice visual" artifact.
   Changes: transparent ground, pauses when off screen, reduced-motion aware. */
(function(root){'use strict';
const TAU=Math.PI*2,clamp=(v,a,b)=>Math.max(a,Math.min(b,v)),lerp=(a,b,t)=>a+(b-a)*t;
const P={idle:{base:.18,gain:0,speed:.35,sparks:.25},listening:{base:.26,gain:.45,speed:.55,sparks:.5},thinking:{base:.30,gain:0,speed:1.6,sparks:.7},speaking:{base:.34,gain:.9,speed:1,sparks:1}};
const RM=matchMedia('(prefers-reduced-motion: reduce)').matches;
class KixVoice{
 constructor(c,o={}){this.canvas=c;this.ctx=c.getContext('2d');this.o=Object.assign({color:[255,186,72],hot:[255,244,214],strands:22,maxSparks:200,maxDpr:2,scale:1},o);
  this.state='idle';this.preset=Object.assign({},P.idle);this.targetLevel=0;this.level=0;this.energy=.18;this.t=0;this.phaseT=0;this.introT=RM?1:0;this.analyser=null;this.visible=true;
  this.strands=[];for(let i=0;i<this.o.strands;i++)this.strands.push({f1:1.2+Math.random()*2.6,f2:.6+Math.random()*1.8,p1:Math.random()*TAU,p2:Math.random()*TAU,s1:(.6+Math.random()*1.2)*(Math.random()<.5?-1:1),s2:.3+Math.random()*.8,amp:.55+Math.random()*.6,bright:.35+Math.random()*.65,warm:Math.random(),f3:5+Math.random()*7,wob:.08+Math.random()*.14});
  this.sparks=[];this._acc=0;this._resize=this._resize.bind(this);this._frame=this._frame.bind(this);
  new ResizeObserver(this._resize).observe(c);this._resize();
  new IntersectionObserver(es=>{this.visible=es[0].isIntersecting;if(this.visible&&!this._raf){this._last=performance.now();this._raf=requestAnimationFrame(this._frame);}}).observe(c);
  this._last=performance.now();this._raf=requestAnimationFrame(this._frame);}
 setState(s){if(P[s])this.state=s}
 setLevel(v){this.targetLevel=clamp(+v||0,0,1)}
 attachAnalyser(a){this.analyser=a;this._buf=a?new Float32Array(a.fftSize):null}
 _resize(){const d=Math.min(devicePixelRatio||1,this.o.maxDpr),r=this.canvas.getBoundingClientRect();this.dpr=d;this.w=Math.max(1,Math.round(r.width*d));this.h=Math.max(1,Math.round(r.height*d));this.canvas.width=this.w;this.canvas.height=this.h}
 _frame(now){this._raf=null;if(!this.visible||document.body.classList.contains('still'))return;const dt=Math.min(.05,(now-this._last)/1000);this._last=now;
  if(this.analyser){this.analyser.getFloatTimeDomainData(this._buf);let s=0;for(let i=0;i<this._buf.length;i++)s+=this._buf[i]*this._buf[i];this.targetLevel=clamp((Math.log10(Math.sqrt(s/this._buf.length)+1e-5)+2.3)/1.8,0,1)}
  this._update(RM?dt*.5:dt);this._draw();this._raf=requestAnimationFrame(this._frame)}
 _update(dt){const tg=P[this.state];for(const k in tg)this.preset[k]=lerp(this.preset[k],tg[k],1-Math.exp(-dt*4));
  const k=this.targetLevel>this.level?18:6;this.level=lerp(this.level,this.targetLevel,1-Math.exp(-dt*k));
  let e=this.preset.base+this.preset.gain*this.level;if(this.state==='thinking')e+=.08*Math.sin(this.t*3.2);if(this.state==='idle')e+=.03*Math.sin(this.t*1.1);
  this.energy=lerp(this.energy,e,1-Math.exp(-dt*10));this.t+=dt;this.phaseT+=dt*this.preset.speed*(.7+this.level*.9);if(this.introT<1)this.introT=Math.min(1,this.introT+dt/1.6);
  const W=this.w,H=this.h;this._acc+=dt*140*this.preset.sparks*(.3+this.energy)*(RM?.3:1);
  while(this._acc>1&&this.sparks.length<this.o.maxSparks){this._acc-=1;const u=(Math.random()*2-1)*.85,dir=Math.sign(u)||1;
   this.sparks.push({x:u*W*.5*this._spread(),y:(Math.random()-.5)*H*.18*this._env(u)*(.5+this.energy),vx:dir*(20+Math.random()*90)*this.dpr*(.5+this.energy),vy:(Math.random()-.5)*30*this.dpr,life:0,max:.6+Math.random()*1.4,size:(.4+Math.random()*1.3)*this.dpr})}
  if(this._acc>1)this._acc=0;for(let i=this.sparks.length-1;i>=0;i--){const p=this.sparks[i];p.life+=dt;p.x+=p.vx*dt;p.y+=p.vy*dt;p.vy*=.98;if(p.life>p.max)this.sparks.splice(i,1)}}
 _env(u){const a=Math.abs(u);return Math.exp(-a*a*3.4)*(1-.55*Math.exp(-((a/.09)**2)))}
 _spread(){return .12+.88*(1-Math.pow(1-this.introT,3))}
 _draw(){const{ctx,w:W,h:H,dpr}=this,[r,g,b]=this.o.color,[hr,hg,hb]=this.o.hot,cx=W/2,cy=H/2,E=this.energy,sp=this._spread(),halfW=W*.5*sp,amp=Math.min(H*.32,W*.09)*(.35+E*1.1)*this.o.scale;
  ctx.globalCompositeOperation='source-over';ctx.clearRect(0,0,W,H);ctx.globalCompositeOperation='lighter';
  const hz=ctx.createRadialGradient(cx,cy,0,cx,cy,Math.max(W,H)*.55);hz.addColorStop(0,`rgba(${r},${g-40},${b-40},${.10+.22*E})`);hz.addColorStop(1,'rgba(0,0,0,0)');ctx.fillStyle=hz;ctx.fillRect(0,0,W,H);
  const lg=ctx.createLinearGradient(cx-halfW*1.15,0,cx+halfW*1.15,0);lg.addColorStop(0,`rgba(${r},${g},${b},0)`);lg.addColorStop(.5,`rgba(${hr},${hg},${hb},${.7+.3*E})`);lg.addColorStop(1,`rgba(${r},${g},${b},0)`);
  ctx.fillStyle=lg;ctx.fillRect(cx-halfW*1.15,cy-.75*dpr,halfW*2.3,1.5*dpr);ctx.globalAlpha=.25;ctx.fillRect(cx-halfW*1.15,cy-3*dpr,halfW*2.3,6*dpr);ctx.globalAlpha=1;
  const st=Math.max(2,Math.round(3*dpr)),T=this.phaseT;
  for(const s of this.strands){ctx.beginPath();for(let px=-halfW;px<=halfW;px+=st){const u=px/halfW,env=this._env(u),wave=Math.sin(u*s.f1*TAU+s.p1+T*s.s1*2.2)*Math.cos(u*s.f2*TAU+s.p2-T*s.s2*1.6),fib=1+s.wob*Math.sin(u*s.f3*TAU-T*3.1+s.p2),y=cy+wave*fib*env*amp*s.amp;if(px===-halfW)ctx.moveTo(cx+px,y);else ctx.lineTo(cx+px,y)}
   const cr=Math.round(lerp(r,255,s.warm*.3)),cg=Math.round(lerp(g-30,g+20,s.warm));ctx.strokeStyle=`rgba(${cr},${cg},${b},${.05*s.bright*(.6+E)})`;ctx.lineWidth=6*dpr;ctx.stroke();ctx.strokeStyle=`rgba(${cr},${cg},${b+20},${.34*s.bright*(.5+E*.8)})`;ctx.lineWidth=.75*dpr;ctx.stroke()}
  for(const p of this.sparks){const a=Math.sin(p.life/p.max*Math.PI)*(.5+.5*E);ctx.fillStyle=`rgba(${r},${g+20},${b+40},${a})`;ctx.fillRect(cx+p.x,cy+p.y,p.size,p.size)}
  const cR=Math.min(W,H)*(.06+.32*E*E+.05*E),co=ctx.createRadialGradient(cx,cy,0,cx,cy,cR);co.addColorStop(0,`rgba(255,255,255,${.75+.25*E})`);co.addColorStop(.12,`rgba(${hr},${hg},${hb},${.55+.4*E})`);co.addColorStop(.35,`rgba(${r},${g-20},${b-40},${.22+.3*E})`);co.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=co;ctx.beginPath();ctx.arc(cx,cy,cR,0,TAU);ctx.fill();
  this._ray(cx,cy,Math.min(H*.5,W*.3)*(.25+.95*E),2.2*dpr*(.6+E),Math.PI/2,.85*(.4+E));this._ray(cx,cy,halfW*(.3+.5*E),2.5*dpr*(.6+E),0,.6*(.4+E));
  for(let i=0;i<4;i++)this._ray(cx,cy,Math.min(W,H)*.22*E,1.2*dpr,this.t*.05+i*Math.PI/4+Math.PI/8,.18*E);ctx.globalCompositeOperation='source-over'}
 _ray(cx,cy,len,th,ang,al){if(len<1||al<=.01)return;const{ctx}=this,[hr,hg,hb]=this.o.hot,[r,g,b]=this.o.color;ctx.save();ctx.translate(cx,cy);ctx.rotate(ang);
  const gr=ctx.createLinearGradient(-len,0,len,0);gr.addColorStop(0,`rgba(${r},${g},${b},0)`);gr.addColorStop(.5,`rgba(${hr},${hg},${hb},${clamp(al,0,1)})`);gr.addColorStop(1,`rgba(${r},${g},${b},0)`);ctx.fillStyle=gr;ctx.fillRect(-len,-th/2,len*2,th);
  ctx.scale(1,th*4/len);const ha=ctx.createRadialGradient(0,0,0,0,0,len*.7);ha.addColorStop(0,`rgba(${r},${g},${b},${clamp(al*.35,0,1)})`);ha.addColorStop(1,`rgba(${r},${g},${b},0)`);ctx.fillStyle=ha;ctx.beginPath();ctx.arc(0,0,len*.7,0,TAU);ctx.fill();ctx.restore()}
}
KixVoice.prototype.kick=function(){if(!this._raf&&this.visible){this._last=performance.now();this._raf=requestAnimationFrame(this._frame)}};
root.KixVoice=KixVoice;})(window);
