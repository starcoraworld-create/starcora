/* Starcora name icons: the badge replaces an "o" in each name (S☀la, ☾ro, R✿se).
   The real letter stays in the page underneath, so search engines and screen readers still read "Sola", "Oro" and "Rose". */
(function(){
  var ICON={Sola:{i:'sun',at:1},Oro:{i:'moon',at:0},Rose:{i:'flower',at:1}};
  var base=(document.currentScript&&document.currentScript.src||'').replace(/names\.js.*$/,'');
  var css=document.createElement('style');
  css.textContent='.cn{white-space:nowrap}.cn .co{display:inline-block;width:.95em;text-align:center;color:transparent;margin:0 .02em;background:center 55%/.95em .95em no-repeat}.cn .co.cap{width:1.08em;background-size:1.08em 1.08em}';
  document.head.appendChild(css);
  var RX=/\b(Sola|Oro|Rose)\b/g,HAS=/\b(Sola|Oro|Rose)\b/,SKIP={SCRIPT:1,STYLE:1,TITLE:1,TEXTAREA:1,NOSCRIPT:1,OPTION:1};
  function make(name){
    var c=ICON[name],s=document.createElement('span');s.className='cn';
    var a=name.slice(0,c.at),o=name.charAt(c.at),z=name.slice(c.at+1);
    if(a)s.appendChild(document.createTextNode(a));
    var b=document.createElement('span');b.className='co'+(o==='O'?' cap':'');b.textContent=o;
    b.style.backgroundImage='url('+base+'assets/stickers/'+c.i+'.webp)';s.appendChild(b);
    if(z)s.appendChild(document.createTextNode(z));
    return s;
  }
  function walk(root){
    var w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,{acceptNode:function(n){
      var p=n.parentNode;if(!p||SKIP[p.nodeName])return 2;
      if(p.closest&&p.closest('.cn,.no-ico,svg'))return 2;
      return HAS.test(n.nodeValue)?1:2}}),list=[],n;
    while((n=w.nextNode()))list.push(n);
    list.forEach(function(t){
      var f=document.createDocumentFragment(),s=t.nodeValue,last=0,m;RX.lastIndex=0;
      while((m=RX.exec(s))){if(m.index>last)f.appendChild(document.createTextNode(s.slice(last,m.index)));f.appendChild(make(m[1]));last=m.index+m[1].length}
      if(last<s.length)f.appendChild(document.createTextNode(s.slice(last)));
      t.parentNode.replaceChild(f,t);
    });
  }
  function start(){walk(document.body);
    new MutationObserver(function(ms){ms.forEach(function(m){m.addedNodes.forEach(function(nd){if(nd.nodeType===1&&!(nd.closest&&nd.closest('.cn')))walk(nd);else if(nd.nodeType===3&&nd.parentNode)walk(nd.parentNode)})})}).observe(document.body,{childList:true,subtree:true});
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);else start();
})();
