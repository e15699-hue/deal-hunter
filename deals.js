/* 好康網：商品動態載入（Supabase deals 表）
   頁面保留靜態快照（SEO 用），載入後從 DB 抓最新情報並即時更新。
   商品更新只需寫入資料庫，不用推 git。 */
(function () {
  'use strict';

  function sb() {
    try {
      if (!(window.HK_SUPABASE_URL && window.HK_SUPABASE_ANON_KEY)) return null;
      if (!window.supabase) return null;
      if (!window._hk) window._hk = window.supabase.createClient(window.HK_SUPABASE_URL, window.HK_SUPABASE_ANON_KEY);
      return window._hk;
    } catch (e) { return null; }
  }

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function dealKey(url) { return String(url || '').split('?')[0].split('#')[0].trim(); }

  function cardHTML(d) {
    var price = Number(d.price) || 0;
    var market = Number(d.market_price) || 0;
    var badge, was;
    if (market > price) {
      var off = Math.round((1 - price / market) * 100);
      badge = '<span class="badge">便宜 ' + off + '%</span>';
      was = '<span class="was">市價 $' + market.toLocaleString() + '</span>';
    } else {
      badge = '<span class="badge good">好價</span>';
      was = '';
    }
    var url = String(d.url || '').trim();
    var btn = '';
    if (/^https?:/.test(url)) {
      var key = esc(dealKey(url)), title = esc(d.name);
      btn = '<div class="btnrow"><a class="btn" href="' + esc(url) + '" target="_blank" rel="noopener">去看看 →</a>'
        + '<button class="watchbtn" data-key="' + key + '" data-title="' + title + '" data-price="' + price
        + '" onclick="watchDeal(this)" title="追蹤降價通知">🔔</button></div>';
    }
    var img = String(d.image || '').trim();
    var pic = /^https?:/.test(img)
      ? '<div class="pic"><img loading="lazy" src="' + esc(img) + '" alt="" onerror="this.closest(\'.pic\').style.display=\'none\'"></div>'
      : '';
    return '<div class="card"><div class="row">' + pic + '<div class="body">'
      + '<div class="top"><h3>' + esc(d.name) + '</h3>' + badge + '</div>'
      + '<div class="price"><span class="now">$' + price.toLocaleString() + '</span>' + was + '</div>'
      + '<div class="meta"><span>📦 ' + esc(d.source) + '</span><span>👤 ' + esc(d.seller) + '</span><br><span>📝 ' + esc(d.note) + '</span></div>'
      + btn + '</div></div></div>';
  }

  function flashHTML(d) {
    var price = Number(d.price) || 0, market = Number(d.market_price) || 0;
    var off = market > price ? '下殺 ' + Math.round((1 - price / market) * 100) + '%' : 'Bug 價';
    var url = String(d.url || '').trim();
    var btn = /^https?:/.test(url)
      ? '<div style="margin-top:10px"><a class="btn" style="background:#fff;color:#e53935" href="' + esc(url) + '" target="_blank" rel="noopener">手刀去搶 →</a></div>'
      : '';
    return '<div class="flash"><h3>⚡ ' + esc(d.name) + '</h3>'
      + '<div style="font-size:1.4rem;font-weight:bold;margin:6px 0">$' + price.toLocaleString()
      + ' <span style="font-size:.8rem;opacity:.85">(' + off + ')</span></div>'
      + '<div class="time">🕐 發現時間：' + esc(d.found_at) + '・' + esc(d.source) + '・' + esc(d.note) + '</div>'
      + btn + '</div>';
  }

  // 頁面類型：首頁（全部＋每類前3）或分類頁（data-cat 屬性）
  async function refresh() {
    var client = sb();
    if (!client) return;
    var main = document.querySelector('main.content');
    if (!main) return;
    var catFilter = main.getAttribute('data-cat'); // 分類頁才有

    try {
      var q = client.from('deals').select('*').eq('is_active', true).order('created_at', { ascending: false }).limit(300);
      if (catFilter) q = q.eq('category', catFilter);
      var res = await q;
      if (res.error || !res.data || !res.data.length) return;
      var deals = res.data;

      // 快訊區
      var flash = deals.filter(function (d) { return d.flash; }).slice(0, 5);
      var flashSec = main.querySelector('.flash-sec');
      if (flash.length) {
        var fhtml = '<section class="flash-sec"><h2>⚡ 限時快訊（手刀要快）</h2>\n' + flash.map(flashHTML).join('\n') + '\n</section>';
        if (flashSec) flashSec.outerHTML = fhtml;
        else main.insertAdjacentHTML('afterbegin', fhtml);
      } else if (flashSec) { flashSec.remove(); }

      // 囤貨快報區（歷史低點消耗品）
      var stockup = deals.filter(function (d) { return d.stockup && !d.flash; }).slice(0, 6);
      var oldStockup = main.querySelector('.stockup-sec');
      if (oldStockup) oldStockup.remove();
      if (stockup.length && !catFilter) {
        var shead = '<section class="deal-sec stockup-sec"><h2>📦 囤貨快報（歷史低點）</h2>\n';
        var shtml = shead + stockup.map(cardHTML).join('\n') + '</section>';
        var anchor = main.querySelector('.flash-sec') || main.firstChild;
        if (anchor && anchor.insertAdjacentHTML) anchor.insertAdjacentHTML('afterend', shtml);
        else main.insertAdjacentHTML('afterbegin', shtml);
      }

      // 分類區
      var order = [], byCat = {};
      deals.filter(function (d) { return !d.flash && !d.stockup; }).forEach(function (d) {
        var c = d.category || '其他';
        if (!byCat[c]) { byCat[c] = []; order.push(c); }
        byCat[c].push(d);
      });
      // 移除舊的 deal-sec（保留 sponsored 結構則重建）
      main.querySelectorAll('section.deal-sec').forEach(function (s) { s.remove(); });
      var html = '';
      order.forEach(function (c) {
        var items = byCat[c];
        var show = catFilter ? items : items.slice(0, 3);
        var cards = show.map(cardHTML).join('\n');
        var count = '<span class="dealcount">' + items.length + ' 則</span>';
        var more = '';
        if (!catFilter && items.length > 3) {
          var slug = (window.HK_CAT_SLUGS || {})[c];
          if (slug) more = '<div class="morebtn"><a href="cat/' + slug + '.html">看更多' + esc(c) + '優惠 →</a></div>';
        }
        html += '<section class="deal-sec"><h2>' + esc(c) + count + '</h2>\n' + cards + '\n' + more + '</section>';
      });
      if (!html) html = '<section><h2>暫無情報</h2><div class="card"><div class="body">此分類尚無優惠情報，站長搜刮中，敬請期待！</div></div></section>';
      // 插到 flash 後面（或最前面）
      var ref = main.querySelector('.flash-sec');
      if (ref) ref.insertAdjacentHTML('afterend', html);
      else main.insertAdjacentHTML('afterbegin', html);

      // 更新 hero 計數
      var stat = document.querySelector('.hero-stats b');
      if (stat) stat.textContent = deals.length;
    } catch (e) { /* 靜默：保留靜態快照 */ }
  }

  // 分類 slug 對照（首頁「看更多」用）
  window.HK_CAT_SLUGS = {
    '3C數位': '3c', '家電': 'appliance', '美妝保養': 'beauty',
    '服飾鞋包': 'fashion', '食品日用': 'grocery', '母嬰玩具': 'baby',
    '運動戶外': 'sports', '居家生活': 'home', '寵物生活': 'pet'
  };

  document.addEventListener('DOMContentLoaded', function () {
    // 等 supabase script 載入後再跑
    var tries = 0;
    (function wait() {
      if (window.supabase || tries++ > 20) refresh();
      else setTimeout(wait, 250);
    })();
  });
})();
