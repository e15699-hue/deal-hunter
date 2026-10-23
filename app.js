/* 好康網前端 */
/* ===== 導覽切轉：側欄功能與會員中心（一次只顯示一個面板） ===== */
function hkInitSwitchGroup(buttonSelector, panelSelector, buttonKey, panelKey, defaultKey) {
  const buttons = Array.from(document.querySelectorAll(buttonSelector));
  const panels = Array.from(document.querySelectorAll(panelSelector));
  if (!buttons.length || !panels.length) return;
  function activate(key, updateHash) {
    const target = panels.some(panel => panel.dataset[panelKey] === key)
      ? key
      : (panels[0].dataset[panelKey] || defaultKey);
    panels.forEach(panel => { panel.hidden = panel.dataset[panelKey] !== target; });
    buttons.forEach(button => {
      const on = button.dataset[buttonKey] === target;
      button.classList.toggle('on', on);
      button.setAttribute('aria-selected', on ? 'true' : 'false');
    });
    if (updateHash && target) history.replaceState(null, '', '#' + target);
  }
  buttons.forEach(button => button.addEventListener('click', () => activate(button.dataset[buttonKey], false)));
  const fromHash = location.hash ? location.hash.slice(1) : '';
  activate(panels.some(panel => panel.dataset[panelKey] === fromHash) ? fromHash : defaultKey, false);
}

document.addEventListener('DOMContentLoaded', () => {
  hkInitSwitchGroup('[data-side-tab]', '[data-side-panel]', 'sideTab', 'sidePanel', 'hot');
  hkInitSwitchGroup('[data-member-tab]', '[data-member-panel]', 'memberTab', 'memberPanel', 'tips');
  // hero 新手引導：同頁 #guide 等 hash 變化時切到側欄對應 tab 並捲過去
  function hkSideTabFromHash(scroll) {
    const k = (location.hash || '').slice(1);
    const btn = document.querySelector('[data-side-tab="' + k + '"]');
    if (!btn) return;
    btn.click();
    if (scroll) {
      const sb = document.querySelector('.sidebar');
      if (sb) sb.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }
  window.addEventListener('hashchange', () => hkSideTabFromHash(true));
  document.querySelectorAll('a.hero-newbie').forEach(a => {
    a.addEventListener('click', () => setTimeout(() => hkSideTabFromHash(true), 60));
  });
});

/* ===== 銀髮友善：字體放大開關（2026-10-21 銀髮長輩視角）=====
   header .userbar 旁加「🔠 大字」按鈕；html.font-lg 把根字體 16px→20px
   （全站多用 rem，整站文字等比放大）；localStorage 記憶偏好。 */
(function hkFontToggle() {
  var KEY = 'hk_fontlg';
  function isLarge() { try { return localStorage.getItem(KEY) === '1'; } catch (e) { return false; } }
  function apply() {
    document.documentElement.classList.toggle('font-lg', isLarge());
    var b = document.getElementById('fontToggle');
    if (b) b.textContent = isLarge() ? '🔠 標準字' : '🔠 大字';
  }
  function mount() {
    if (document.getElementById('fontToggle')) return;
    var b = document.createElement('button');
    b.id = 'fontToggle'; b.className = 'fontbtn'; b.type = 'button';
    b.setAttribute('aria-label', '切換大字體');
    b.addEventListener('click', function () {
      try { localStorage.setItem(KEY, isLarge() ? '0' : '1'); } catch (e) {}
      apply();
    });
    var ub = document.querySelector('.userbar');
    if (ub) { ub.appendChild(b); }
    else {
      /* 2026-10-23 會員功能移除後 .userbar 已不存在，走此分支：
         固定於右下角、疊在 #toTop（bottom:16px＋44px 高）上方，避免重疊 */
      b.style.cssText = 'position:fixed;right:12px;bottom:70px;z-index:9999;box-shadow:0 2px 8px rgba(0,0,0,.25)';
      document.body.appendChild(b);
    }
    apply();
  }
  try { if (isLarge()) document.documentElement.classList.add('font-lg'); } catch (e) {}
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
})();

/* 底部導覽列目前頁面高亮（v3 框架，2026-10-21） */
(function(){try{var p=location.pathname.split('/').pop()||'index.html';document.querySelectorAll('.tabbar a').forEach(function(a){var h=(a.getAttribute('href')||'').split('/').pop();if(h&&h===p)a.classList.add('on');});}catch(e){}})();

/* 左側導覽欄目前頁面高亮（v5，2026-10-22） */
(function(){try{var p=location.pathname;document.querySelectorAll('.rail a.rl').forEach(function(a){var h=a.getAttribute('href')||'';if(h&&p.endsWith(h))a.classList.add('on');});}catch(e){}})();

/* 特賣會情報地區過濾器（2026-10-22 使用者定版：ALL/北部/中部/南部 篩選，不改架構） */
(function(){try{
  var bar=document.querySelector('.evfilters');if(!bar)return;
  var cards=[].slice.call(document.querySelectorAll('.events-sec .event-card'));
  bar.addEventListener('click',function(ev){
    var b=ev.target.closest('.evf');if(!b)return;
    bar.querySelectorAll('.evf').forEach(function(x){x.classList.toggle('on',x===b);});
    var f=b.getAttribute('data-f');
    cards.forEach(function(c){c.style.display=(f==='ALL'||c.getAttribute('data-region')===f)?'':'none';});
  });
}catch(e){}})();

/* 特賣會日期狀態（2026-10-22 使用者定版：進行中/即將開始/已結束由 JS 依今天判斷，不動主架構） */
(function(){function run(){try{
  var cards=document.querySelectorAll('.events-sec .event-card');if(!cards.length)return;
  var n=new Date();
  function p(x){return String(x).padStart(2,'0');}
  var today=n.getFullYear()+'-'+p(n.getMonth()+1)+'-'+p(n.getDate());
  function md(d){return d?d.slice(5).replace('-','/'):'';}
  cards.forEach(function(c){
    var s=c.getAttribute('data-start')||'', e=c.getAttribute('data-end')||'';
    var ed=c.querySelector('.edate');if(!ed)return;
    var b=ed.querySelector('b'), sp=ed.querySelector('span');if(!b||!sp)return;
    if(e&&e<today){c.classList.add('ended');b.textContent='已結束';sp.textContent='至 '+md(e);}
    else if(s&&s>today){b.textContent=md(s);sp.textContent='即將開始';}
    else{b.textContent='進行中';sp.textContent='至 '+md(e);}
  });
}catch(err){}}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',run);else run();})();
