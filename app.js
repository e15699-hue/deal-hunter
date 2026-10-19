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
  alert('已加入追蹤！降價時會通知你。');
}
document.addEventListener('DOMContentLoaded', hkRefreshUserbar);
