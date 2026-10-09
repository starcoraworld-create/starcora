(function(){
  var hero=document.querySelector('.hero'),svg=document.querySelector('.trail'),guide=document.querySelector('.guide'),say=guide.querySelector('.say');
  var flash=document.querySelector('.flash');
  var books=[].slice.call(document.querySelectorAll('.book'));
  var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // progress lives in this browser only; a book adds its number here when the last page is solved
  // for testing: stories.html?reset=1 clears which books are finished on this device
  if(/[?&]reset=1/.test(location.search)){try{localStorage.removeItem('starcora-read')}catch(e){}}
  function getRead(){try{return JSON.parse(localStorage.getItem('starcora-read')||'[]')}catch(e){return[]}}
  function setRead(list){try{localStorage.setItem('starcora-read',JSON.stringify(list))}catch(e){}}
  window.starcoraMarkRead=function(n){var r=getRead();if(r.indexOf(n)<0)r.push(n);setRead(r);update()};

  var next=null;
  function update(){
    var read=getRead();next=null;
    books.forEach(function(b){
      var n=+b.dataset.n;b.classList.toggle('done',read.indexOf(n)>=0);b.classList.remove('next');
      if(next===null&&b.classList.contains('ready')&&read.indexOf(n)<0)next=n;
    });
    if(next!==null)books[next].classList.add('next');
    draw();place();
  }

  function centre(b){
    var h=hero.getBoundingClientRect(),t=b.querySelector('.tome').getBoundingClientRect();
    return [t.left-h.left+t.width/2,t.top-h.top+t.height/2,t];
  }

  // a dotted trail of stars from book to book; the part already travelled glows gold
  function draw(){
    var read=getRead(),out='';
    for(var i=0;i<books.length-1;i++){
      var a=centre(books[i]),b=centre(books[i+1]);
      var mx=(a[0]+b[0])/2,dy=Math.abs(b[1]-a[1]);
      var c1=[mx,a[1]+ (window.innerWidth<760?0:-60)],c2=[mx,b[1]+(window.innerWidth<760?0:60)];
      if(window.innerWidth<760){c1=[a[0],(a[1]+b[1])/2];c2=[b[0],(a[1]+b[1])/2]}
      var lit=read.indexOf(i)>=0;
      out+='<path class="'+(lit?'lit':'dim')+'" d="M'+a[0]+' '+a[1]+' C'+c1[0]+' '+c1[1]+' '+c2[0]+' '+c2[1]+' '+b[0]+' '+b[1]+'"/>';
    }
    svg.innerHTML=out;
  }

  // Sola stands beside the book to read next
  function place(){
    var target=next!==null?books[next]:books.filter(function(b){return b.classList.contains('done')}).pop()||books[0];
    var c=centre(target),t=c[2],h=hero.getBoundingClientRect();
    // she stands on the open side: book on the left, Sola on the right, and the other way round
    var onRight=(t.left+t.width/2-h.left)<h.width/2;
    guide.classList.toggle('right',onRight);
    guide.style.left=((onRight?t.right:t.left)-h.left)+'px';guide.style.top=(t.top-h.top+t.height*.55)+'px';
  }

  // the narrator's recorded lines (no robot voice)
  var CLIPS={'Coming soon!':'soon','Try book 0 first!':'try0','Try book 1 first!':'try1','Try book 2 first!':'try2'},clip=null;
  function voice(text){
    var k=CLIPS[text];if(!k)return;
    try{if(clip){clip.pause()}clip=new Audio('assets/voice/'+k+'.mp3');np('Starcora');var p=clip.play();p&&p.catch(function(){})}catch(e){}
  }
  function talk(text,ms,speak){say.textContent=text;say.classList.add('on');clearTimeout(say._t);say._t=setTimeout(function(){say.classList.remove('on')},ms||2600);if(speak)voice(text)}

  update();

  // narrator intro: tries to play on arrival (once per visit); if the browser blocks sound, it plays on the first tap.
  // The glowing speaker replays it any time.
  var hear=document.getElementById('hear'),intro=null,introDone=false;
  function playIntro(){
    try{
      if(intro){intro.pause();intro.currentTime=0}
      intro=new Audio('assets/voice/shelf-intro.mp3');np('Follow the stars');
      hear&&hear.classList.add('playing');hear&&hear.classList.remove('glow');
      intro.onended=function(){hear&&hear.classList.remove('playing')};
      var pr=intro.play();introDone=true;
      if(pr&&pr.catch)pr.catch(function(){introDone=false;hear&&hear.classList.remove('playing');hear&&hear.classList.add('glow')});
    }catch(e){}
  }
  function stopIntro(){try{intro&&intro.pause();hear&&hear.classList.remove('playing')}catch(e){}}
  if(hear)hear.addEventListener('click',function(e){e.stopPropagation();if(intro&&!intro.paused){stopIntro()}else playIntro()});
  var seen=false;try{seen=sessionStorage.getItem('starcora-intro')==='1';sessionStorage.setItem('starcora-intro','1')}catch(e){}
  if(!seen){
    hear&&hear.classList.add('glow');
    setTimeout(playIntro,reduce?300:900);
    document.addEventListener('pointerdown',function first(ev){
      document.removeEventListener('pointerdown',first,true);
      if(!introDone&&!(ev.target.closest&&ev.target.closest('.book,.hear,a')))playIntro();
    },true);
  }
  window.addEventListener('resize',function(){draw();place()});
  setTimeout(function(){
    var read=getRead();
    talk(next===null?'More books soon!':(read.length?'Next one!':'Start here!'),3200);
  },reduce?200:1200);

  var pending=null,pendTimer;
  books.forEach(function(b){
    var a=b.querySelector('a'),n=+b.dataset.n;
    a.addEventListener('click',function(e){
      e.preventDefault();
      if(b.classList.contains('soon')){b.classList.remove('shake');void b.offsetWidth;b.classList.add('shake');talk('Coming soon!',2000,true);return}
      // any ready book opens straight away; Sola and the glow just suggest the next one
      open(b,a.getAttribute('href'));
    });
  });

  // the Starcora jingle plays as the cover swings open, then the book starts on page 1
  var jingle=null;
  function np(t){try{if('mediaSession' in navigator&&window.MediaMetadata)navigator.mediaSession.metadata=new MediaMetadata({title:t,artist:'Starcora',artwork:[{src:new URL('assets/now-playing.jpg',location.href).href,sizes:'512x512',type:'image/jpeg'}]})}catch(e){}}
  function playJingle(){try{jingle=new Audio('assets/jingle.mp3');np('Starcora');var p=jingle.play();p&&p.catch(function(){})}catch(e){}}
  function open(b,href){
    say.classList.remove('on');stopIntro();
    var t=b.querySelector('.tome').getBoundingClientRect();
    flash.style.setProperty('--fx',(t.left+t.width/2)+'px');flash.style.setProperty('--fy',(t.top+t.height/2)+'px');
    playJingle();
    b.classList.add('open');
    href+=(href.indexOf('?')<0?'?':'&')+'shelf=1';
    if(reduce){setTimeout(function(){go(b,href)},1800);return}
    setTimeout(function(){flash.classList.add('on')},1900);
    setTimeout(function(){go(b,href)},2500);
  }
  function go(b,href){if(window.showBook)showBook(b);else location.href=href}

  window.addEventListener('pageshow',function(e){if(e.persisted){flash.classList.remove('on');books.forEach(function(b){b.classList.remove('open')});update()}});
})();
