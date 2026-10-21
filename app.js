/* 好康網前端：會員狀態＋降價追蹤（Supabase 未設定時靜默停用） */
function hkClient() {
  try {
    if (!(window.HK_SUPABASE_URL && window.HK_SUPABASE_ANON_KEY)) return null;
    if (!window.supabase) return null;
    if (!window._hk) window._hk = window.supabase.createClient(window.HK_SUPABASE_URL, window.HK_SUPABASE_ANON_KEY);
    return window._hk;
  } catch (e) { return null; }
}
async function hkRefreshUserbar() {
  const a = document.getElementById('userLink');
  if (!a) return;
  const sb = hkClient();
  if (!sb) return;
  try {
    const { data } = await sb.auth.getSession();
    if (data.session) { a.textContent = '👤 會員中心'; a.href = 'my.html'; }
  } catch (e) {}
}
/* 卡片上的 🔔 追蹤降價按鈕 */
async function watchDeal(btn) {
  const sb = hkClient();
  if (!sb) { alert('追蹤功能即將上線，敬請期待！'); return; }
  const { data } = await sb.auth.getSession();
  if (!data.session) {
    location.href = 'login.html?next=' + encodeURIComponent(location.pathname + location.search);
    return;
  }
  const row = {
    user_id: data.session.user.id,
    deal_key: btn.dataset.key,
    title: btn.dataset.title,
    price_now: Number(btn.dataset.price)
  };
  const { error } = await sb.from('watchlist').upsert(row, { onConflict: 'user_id,deal_key' });
  if (error) { alert('追蹤失敗：' + error.message); return; }
  btn.classList.add('on');
  alert('已加入追蹤！降價會顯示在「我的追蹤」。');
}
document.addEventListener('DOMContentLoaded', hkRefreshUserbar);

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
      b.style.cssText = 'position:fixed;right:12px;bottom:12px;z-index:9999;box-shadow:0 2px 8px rgba(0,0,0,.25)';
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
