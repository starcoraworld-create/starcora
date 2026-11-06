/* Storybooks teaser (see teaser.css). Markup on the page:
   <div class="tz-card" id="tzCard"><button class="tz" data-avoid=".island,.titles" ...>...</button></div>  (straight after the hero)
   optional <button class="tz-pill" data-tz-open>...</button> inside the hero (phones). */
(function(){
  var btn=document.querySelector('.tz');if(!btn)return;
  var card=document.getElementById('tzCard'),hero=document.querySelector('.hero');
  var vid=btn.querySelector('video'),frame=btn.querySelector('.frame');
  var SRC_SMALL=btn.getAttribute('data-src'),SRC_BIG=btn.getAttribute('data-src-big')||SRC_SMALL;
  var avoid=btn.getAttribute('data-avoid')||'';
  var calm=matchMedia('(prefers-reduced-motion: reduce)').matches||(navigator.connection&&navigator.connection.saveData);

  /* 1. Where it sits: float in the sky only if it touches nothing */
  function box(el){if(/^(H1|H2|P)$/.test(el.tagName)){var g=document.createRange();g.selectNodeContents(el);return g.getBoundingClientRect()}return el.getBoundingClientRect()}
  function hit(a,b){var p=10;return a.left<b.right+p&&a.right>b.left-p&&a.top<b.bottom+p&&a.bottom>b.top-p}
  function place(){
    if(hero){var hd=document.querySelector('.site-header');hero.style.setProperty('--tz-top',Math.max(80,(hd?hd.getBoundingClientRect().bottom-hero.getBoundingClientRect().top:90)+18)+'px')}
    if(!hero||innerWidth<761){toCard();return}
    if(btn.parentNode!==hero)hero.appendChild(btn);
    var head=document.querySelector('.site-header');var top=(head?head.getBoundingClientRect().bottom-hero.getBoundingClientRect().top:90)+18;
    hero.style.setProperty('--tz-top',Math.max(80,top)+'px');
    btn.classList.add('tz-float');btn.style.animation='none';
    var sides=(btn.getAttribute('data-sides')||'right').split(','),ok=false,els=avoid?hero.querySelectorAll(avoid):[];
    for(var k=0;k<sides.length&&!ok;k++){
      btn.classList.toggle('tz-left',sides[k]==='left');
      var r=btn.getBoundingClientRect(),h=hero.getBoundingClientRect();ok=r.bottom<h.bottom-12&&r.left>h.left&&r.right<h.right;
      for(var i=0;i<els.length&&ok;i++){var e=box(els[i]);if(e.width&&hit(r,e))ok=false}
    }
    btn.style.animation='';
    if(!ok)toCard();else{if(card)card.hidden=true;pill(false)}
  }
  var home=card&&card.parentNode,next=card&&card.nextSibling,ph=btn.getAttribute('data-phone-after');
  var pl=document.querySelector('.tz-pill');function pill(on){if(pl)pl.hidden=!on}
  function toCard(){btn.classList.remove('tz-float');pill(!(ph&&innerWidth<761));if(!card)return;card.hidden=false;if(btn.parentNode!==card)card.insertBefore(btn,card.firstChild);
    var t=ph&&innerWidth<761&&document.querySelector(ph);
    if(t){if(card.previousSibling!==t)t.parentNode.insertBefore(card,t.nextSibling);card.classList.add('tz-in')}
    else if(card.parentNode!==home||card.nextSibling!==next){home.insertBefore(card,next);card.classList.remove('tz-in')}}
  var rt;addEventListener('resize',function(){if(!settled)return;clearTimeout(rt);rt=setTimeout(place,150)});
  /* islands and books float in, so decide once they have settled (and again on resize) */
  btn.style.visibility='hidden';if(pl)pl.hidden=true;
  var settled=false;function settle(){if(settled)return;settled=true;place();btn.style.visibility='';watch()}
  addEventListener('load',function(){setTimeout(settle,1700)});setTimeout(settle,4000);

  /* 2. The muted loop: loads only when on screen, pauses when off screen */
  var loaded=false;
  function start(){if(calm)return;if(!loaded){vid.src=SRC_SMALL;loaded=true}var p=vid.play();if(p&&p.catch)p.catch(function(){})}
  function watch(){if('IntersectionObserver' in window){new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting)start();else if(loaded)vid.pause()})},{threshold:.35}).observe(btn)}else start()}

  /* 3. The full video with sound */
  var m,mv;
  function build(){
    m=document.createElement('div');m.className='tzm';m.hidden=true;m.setAttribute('role','dialog');m.setAttribute('aria-modal','true');m.setAttribute('aria-label','How the Starcora storybooks work');
    var onShelf=/stories(\.html)?$/.test(location.pathname)||!!document.querySelector('.books');
    m.innerHTML='<div class="box"><button class="x" type="button" aria-label="Close"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg></button>'+
      '<div class="vid"><video playsinline preload="none" poster="'+(vid.getAttribute('poster')||'')+'"></video>'+
      '<div class="end"><a class="go" href="books/book-0/index.html?shelf=1">Start with Book 0</a>'+
      (onShelf?'<button class="again" type="button" data-close>Choose a book</button>':'<a class="again" href="stories.html">See all storybooks</a>')+'</div></div>'+
      '<p class="note">Every storybook reads to you. Then you play the game!</p></div>';
    document.body.appendChild(m);mv=m.querySelector('video');
    m.addEventListener('click',function(e){if(e.target===m||e.target.closest('.x,[data-close]'))close()});
    mv.addEventListener('ended',function(){m.classList.add('done')});
    mv.addEventListener('click',function(){if(m.classList.contains('done'))return;mv.paused?mv.play():mv.pause()});
  }
  var back;
  function open(e){
    if(e)e.preventDefault();if(!m)build();back=document.activeElement;
    document.querySelectorAll('audio').forEach(function(a){try{a.pause()}catch(_){}});if(loaded)vid.pause();
    m.classList.remove('done');m.hidden=false;requestAnimationFrame(function(){m.classList.add('on')});
    if(!mv.src)mv.src=innerWidth>760?SRC_BIG:SRC_SMALL;mv.currentTime=0;mv.muted=false;var p=mv.play();if(p&&p.catch)p.catch(function(){mv.controls=true});
    m.querySelector('.x').focus();document.documentElement.style.overflow='hidden';
  }
  function close(){if(!m||m.hidden)return;mv.pause();m.classList.remove('on');m.hidden=true;document.documentElement.style.overflow='';if(loaded&&!calm)vid.play().catch(function(){});if(back&&back.focus)back.focus()}
  btn.addEventListener('click',open);
  document.querySelectorAll('[data-tz-open]').forEach(function(b){b.addEventListener('click',open)});
  addEventListener('keydown',function(e){if(e.key==='Escape')close()});
})();
