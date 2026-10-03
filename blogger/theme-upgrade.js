/* Gujarat Bole Che — lightweight client-side interactions */
(function(){
  'use strict';
  function init(){
    var root=document.querySelector('.gbc-shell'); if(!root)return;
    var input=root.querySelector('[data-gbc-search]');
    if(input){input.addEventListener('input',function(){var q=this.value.toLowerCase().trim();document.querySelectorAll('.post-outer,.date-outer').forEach(function(p){var t=(p.innerText||'').toLowerCase();p.classList.toggle('gbc-hidden',q && t.indexOf(q)===-1);});});}
    var theme=document.querySelector('[data-gbc-theme]');
    if(theme)theme.addEventListener('click',function(){document.documentElement.classList.toggle('gbc-dark');});
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
