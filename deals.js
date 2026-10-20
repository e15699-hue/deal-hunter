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
      btn = '<div class="btnrow"><a class="btn" href="' + esc(url) + '" target="_blank" rel="noopener">' + '去看看 →' + '</a>'
        + '<button class="watchbtn" data-key="' + key + '" data-title="' + title + '" data-price="' + price
        + '" onclick="watchDeal(this)" title="追蹤降價通知">🔔</button></div>';
    }
    var img = String(d.image || '').trim();
    var pic = /^https?:/.test(img)
      ? '<div class="pic"><img loading="lazy" src="' + esc(img) + '" alt="" onerror="this.closest(\'.pic\').style.display=\'none\'"></div>'
      : '';
    var nowTxt = '$' + price.toLocaleString();
    return '<div class="card"><div class="row">' + pic + '<div class="body">'
      + '<div class="top"><h3>' + esc(d.name) + '</h3>' + badge + '</div>'
      + '<div class="price"><span class="now">' + nowTxt + '</span>' + was + saveHtml + '</div>'
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

  // 頁面類型：首頁（百貨樓層，每層折扣最高前 8 筆）或分類頁（data-cat 屬性，整層全顯示）
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

  // 百貨樓層對照（與 shared/categories.json 同步）：name＝資料分類名，fname＝樓層顯示名
  var HK_FLOORS = [
    { name: '美妝保養', slug: 'beauty', floor: '1F', fname: '美妝保養', desc: '保養・彩妝・香氛・身體護理' },
    { name: '服飾鞋包', slug: 'fashion', floor: '2F', fname: '精品時尚', desc: '男女服飾・鞋・包・配件' },
    { name: '3C數位', slug: '3c', floor: '3F', fname: '3C 數位', desc: '電腦・手機・相機・遊戲・穿戴' },
    { name: '家電', slug: 'appliance', floor: '4F', fname: '家電', desc: '大家電・小家電・廚房家電' },
    { name: '居家生活', slug: 'home', floor: '5F', fname: '居家生活', desc: '寢具・收納・修繕・居家佈置' },
    { name: '母嬰玩具', slug: 'baby', floor: '6F', fname: '母嬰親子', desc: '奶粉尿布・童裝・玩具' },
    { name: '運動戶外', slug: 'sports', floor: '7F', fname: '運動休閒', desc: '運動・健身・戶外・休閒' },
    { name: '寵物生活', slug: 'pet', floor: '8F', fname: '寵物用品', desc: '飼料・用品・寵物保健' },
    { name: '食品日用', slug: 'grocery', floor: 'B1', fname: '美食生鮮', desc: '零食・生鮮・保健・清潔日用' }
  ];
  var HK_FLOOR_BY_NAME = {};
  HK_FLOORS.forEach(function (f) { HK_FLOOR_BY_NAME[f.name] = f; });

  // 樓層招牌（與 render.py 靜態快照同結構）
  function floorHeadHTML(fm, total) {
    return '<div class="floor-head"><span class="floor-no">' + fm.floor + '</span>'
      + '<div class="floor-tt"><h2>' + esc(fm.fname) + '</h2><p>' + esc(fm.desc) + '</p></div>'
      + '<span class="dealcount">' + total + ' 則</span></div>';
  }

  function renderAll() {
    var main = document.querySelector('main.content');
    if (!main || !_cache) return;
    var deals = _cache, catFilter = _catFilter, mode = getSortMode();

    // 排序列：只保留在分類頁（首頁改百貨樓層制，固定以折扣力度排序，不顯示排序列）
    if (catFilter) ensureSortbar(main);
    else { var oldBar = main.querySelector('.sortbar'); if (oldBar) oldBar.remove(); }

    // 快訊區（維持發現順序，不參與排序）
    var flash = deals.filter(function (d) { return d.flash; }).slice(0, 5);
    var flashSec = main.querySelector('.flash-sec');
    if (flash.length) {
      var fhtml = '<section class="flash-sec"><h2>⚡ 限時特賣會場（手刀要快）</h2>\n' + flash.map(flashHTML).join('\n') + '\n</section>';
      if (flashSec) flashSec.outerHTML = fhtml;
      else main.insertAdjacentHTML('afterbegin', fhtml);
    } else if (flashSec) { flashSec.remove(); }

    // 分組（不含 flash；stockup／推薦／贊助一律回到所屬樓層，與靜態快照一致）
    var order = [], byCat = {};
    deals.filter(function (d) { return !d.flash; }).forEach(function (d) {
      var c = d.category || '其他';
      if (!byCat[c]) { byCat[c] = []; order.push(c); }
      byCat[c].push(d);
    });
    // 移除舊的 deal-sec（樓層與分類區全部重建）
    main.querySelectorAll('section.deal-sec').forEach(function (s) { s.remove(); });
    var html = '';
    if (!catFilter) {
      // 首頁：百貨樓層（1F→8F→B1），每層折扣力度最高前 8 筆＋「逛完整層」
      var covered = {};
      HK_FLOORS.forEach(function (fm) {
        var items = byCat[fm.name];
        if (!items || !items.length) return;
        covered[fm.name] = true;
        var show = sortDeals(items, 'off').slice(0, 8);
        html += '<section class="deal-sec floor-sec" id="floor-' + fm.slug + '" aria-label="' + fm.floor + ' ' + fm.fname + '">\n'
          + floorHeadHTML(fm, items.length) + '\n'
          + show.map(cardHTML).join('\n')
          + '\n<div class="morebtn"><a href="cat/' + fm.slug + '.html">逛完整層 →</a></div></section>';
      });
      // 不在樓層對照內的分類（保險：新分類未設樓層時仍露出）
      order.forEach(function (c) {
        if (covered[c]) return;
        var items = sortDeals(byCat[c], 'off');
        html += '<section class="deal-sec"><h2>' + esc(c) + '<span class="dealcount">' + items.length + ' 則</span></h2>\n'
          + items.slice(0, 8).map(cardHTML).join('\n') + '\n</section>';
      });
    } else {
      // 分類頁：整層全顯示，標題用樓層名，排序依使用者偏好
      order.forEach(function (c) {
        var items = sortDeals(byCat[c], mode);
        var fm = HK_FLOOR_BY_NAME[c];
        var label = fm ? fm.floor + ' ' + fm.fname : c;
        html += '<section class="deal-sec"><h2>' + esc(label) + '<span class="dealcount">' + items.length + ' 則</span></h2>\n'
          + items.map(cardHTML).join('\n') + '\n</section>';
      });
    }
    if (!html) html = '<section><h2>暫無情報</h2><div class="card"><div class="body">此分類尚無優惠情報，站長搜刮中，敬請期待！</div></div></section>';
    // 插到特賣會場後面（沒有時插到排序列後面，再無則插到主欄最前）
    var ref = main.querySelector('.flash-sec') || main.querySelector('.sortbar');
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
