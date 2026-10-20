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

  // ===== 商品排序（客戶端純函式，不影響靜態快照順序） =====
  var SORTS = [
    { k: 'rec',   label: '推薦' },
    { k: 'off',   label: '折扣力度' },
    { k: 'plow',  label: '價格↑' },
    { k: 'phigh', label: '價格↓' },
    { k: 'new',   label: '最新上架' }
  ];
  var SORT_KEY = 'hk_sort';

  function getSortMode() {
    try {
      var v = localStorage.getItem(SORT_KEY);
      for (var i = 0; i < SORTS.length; i++) if (SORTS[i].k === v) return v;
    } catch (e) {}
    return 'rec';
  }
  function setSortMode(v) {
    try { localStorage.setItem(SORT_KEY, v); } catch (e) {}
  }
  function num(v) { var n = Number(v); return isFinite(n) ? n : 0; }
  function tsOf(d) {
    var t = Date.parse(String(d.found_at || '').replace(/\//g, '-'));
    if (!isFinite(t)) t = Date.parse(String(d.created_at || '').replace(/\//g, '-'));
    return isFinite(t) ? t : 0;
  }
  // 排序純函式：回傳新陣列，Array.prototype.sort 為穩定排序，同鍵維持原順序
  function sortDeals(list, mode) {
    var arr = list.slice();
    if (mode === 'rec') return arr;
    function disc(d) {
      var p = num(d.price), m = num(d.market_price);
      return m > 0 ? (m - p) / m : -9999; // 沒有市價的排最後
    }
    arr.sort(function (a, b) {
      if (mode === 'off') return disc(b) - disc(a);
      if (mode === 'plow') return num(a.price) - num(b.price);
      if (mode === 'phigh') return num(b.price) - num(a.price);
      if (mode === 'new') return tsOf(b) - tsOf(a);
      return 0;
    });
    return arr;
  }
  function paintSortbar(bar) {
    var cur = getSortMode();
    Array.prototype.forEach.call(bar.querySelectorAll('button'), function (b) {
      if (b.getAttribute('data-sort') === cur) b.classList.add('on');
      else b.classList.remove('on');
    });
  }
  function ensureSortbar(main) {
    var bar = main.querySelector('.sortbar');
    if (!bar) {
      bar = document.createElement('div');
      bar.className = 'sortbar';
      bar.innerHTML = '<span class="sortcap">排序</span>' + SORTS.map(function (s) {
        return '<button data-sort="' + s.k + '">' + s.label + '</button>';
      }).join('');
      bar.addEventListener('click', function (e) {
        var b = e.target.closest ? e.target.closest('button[data-sort]') : null;
        if (!b) return;
        setSortMode(b.getAttribute('data-sort'));
        paintSortbar(bar);
        renderAll();
      });
      main.insertBefore(bar, main.firstElementChild);
    }
    paintSortbar(bar);
    return bar;
  }

  function cardHTML(d) {
    var price = Number(d.price) || 0;
    var market = Number(d.market_price) || 0;
    var badge, was, saveHtml;
    if (market > price) {
      var off = Math.round((1 - price / market) * 100);
      var save = market - price;
      // 蝦皮/momo 式：折扣 % 大標籤＋現省金額
      badge = '<span class="badge">-' + off + '%</span>';
      was = '<span class="was">市價 $' + market.toLocaleString() + '</span>';
      saveHtml = '<span class="save">現省 $' + save.toLocaleString() + '</span>';
    } else {
      badge = '<span class="badge good">好價</span>';
      was = '';
      saveHtml = '';
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
      + '<div class="price"><span class="now">$' + price.toLocaleString() + '</span>' + was + saveHtml + '</div>'
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
  var _cache = null, _catFilter = null;

  async function refresh() {
    var client = sb();
    if (!client) return;
    var main = document.querySelector('main.content');
    if (!main) return;
    _catFilter = main.getAttribute('data-cat'); // 分類頁才有

    try {
      var q = client.from('deals').select('*').eq('is_active', true).order('created_at', { ascending: false }).limit(300);
      if (_catFilter) q = q.eq('category', _catFilter);
      var res = await q;
      if (res.error || !res.data || !res.data.length) return;
      _cache = res.data;
      renderAll();
    } catch (e) { /* 靜默：保留靜態快照 */ }
  }

  function renderAll() {
    var main = document.querySelector('main.content');
    if (!main || !_cache) return;
    var deals = _cache, catFilter = _catFilter, mode = getSortMode();

    // 排序列（情報列表上方）：記住使用者偏好，點選即重排，不重抓資料
    ensureSortbar(main);

    // 快訊區（維持發現順序，不參與排序）
    var flash = deals.filter(function (d) { return d.flash; }).slice(0, 5);
    var flashSec = main.querySelector('.flash-sec');
    if (flash.length) {
      var fhtml = '<section class="flash-sec"><h2>⚡ 限時快訊（手刀要快）</h2>\n' + flash.map(flashHTML).join('\n') + '\n</section>';
      if (flashSec) flashSec.outerHTML = fhtml;
      else {
        var sbEl = main.querySelector('.sortbar');
        if (sbEl) sbEl.insertAdjacentHTML('afterend', fhtml);
        else main.insertAdjacentHTML('afterbegin', fhtml);
      }
    } else if (flashSec) { flashSec.remove(); }

    // 囤貨快報區（歷史低點消耗品）
    var stockup = sortDeals(deals.filter(function (d) { return d.stockup && !d.flash; }), mode).slice(0, 6);
    var oldStockup = main.querySelector('.stockup-sec');
    if (oldStockup) oldStockup.remove();
    if (stockup.length && !catFilter) {
      var shead = '<section class="deal-sec stockup-sec"><h2>📦 囤貨快報（歷史低點）</h2>\n';
      var shtml = shead + stockup.map(cardHTML).join('\n') + '</section>';
      var anchor = main.querySelector('.flash-sec') || main.querySelector('.sortbar');
      if (anchor && anchor.insertAdjacentHTML) anchor.insertAdjacentHTML('afterend', shtml);
      else main.insertAdjacentHTML('afterbegin', shtml);
    }

    // 分類區：先依原順序分組（版塊順序不變），再在每組內依偏好排序
    var order = [], byCat = {};
    deals.filter(function (d) { return !d.flash && !d.stockup; }).forEach(function (d) {
      var c = d.category || '其他';
      if (!byCat[c]) { byCat[c] = []; order.push(c); }
      byCat[c].push(d);
    });
    // 移除舊的 deal-sec（囤貨快報區 stockup-sec 已另外重建，不可刪；保留 sponsored 結構則重建）
    main.querySelectorAll('section.deal-sec:not(.stockup-sec)').forEach(function (s) { s.remove(); });
    var html = '';
    order.forEach(function (c) {
      var items = sortDeals(byCat[c], mode);
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
    // 插到囤貨快報後面（無囤貨時插到 flash 後面，再無 flash 插到排序列後面）
    var ref = main.querySelector('.stockup-sec') || main.querySelector('.flash-sec') || main.querySelector('.sortbar');
    if (ref) ref.insertAdjacentHTML('afterend', html);
    else main.insertAdjacentHTML('afterbegin', html);

    // 更新 hero 計數
    var stat = document.querySelector('.hero-stats b');
    if (stat) stat.textContent = deals.length;
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
