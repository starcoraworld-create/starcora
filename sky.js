(function(){
  var flash=document.querySelector('.flash');
  var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll('.island').forEach(function(isl){
    isl.addEventListener('click',function(e){
      if(reduce)return;e.preventDefault();
      var r=isl.getBoundingClientRect();
      flash.style.setProperty('--fx',(r.left+r.width/2)+'px');flash.style.setProperty('--fy',(r.top+r.height*.3)+'px');
      isl.classList.add('go');
      setTimeout(function(){flash.classList.add('on')},700);
      setTimeout(function(){location.href=isl.getAttribute('href')},1200);
    });
  });
})();
