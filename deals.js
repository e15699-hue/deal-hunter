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
  function hkHash(s) { var h = 5381; for (var i = 0; i < s.length; i++) { h = ((h * 33) + s.charCodeAt(i)) >>> 0; } return ('0000000' + h.toString(16)).slice(-8); }
  function flashSlugOf(d) { return hkHash(dealKey(d.url || '')); }

  // ===== 商品排序（客戶端純函式，不影響靜態快照順序） =====
  // 歷史價格（3C 玩家視角：靜態快照有「📉 歷史低價」標示，前端重繪時要一併保留，
  // 否則卡片重繪後標示消失、3C 客少了判斷依據）
  var HK_HIST = null;
  function loadHist() {
    if (HK_HIST !== null) return Promise.resolve(HK_HIST);
    return fetch('/price_history.json').then(function (r) {
      return r && r.ok ? r.json() : null;
    }).then(function (j) {
      HK_HIST = j || null;
      if (HK_HIST) renderAll(); // 歷史價格載入後重繪一次補上標示
    }).catch(function () { HK_HIST = null; });
  }
  function histHTML(d, price) {
    if (!HK_HIST) return '';
    var recs = HK_HIST[dealKey(d.url || '')];
    if (!recs || !recs.length) return '';
    var lows = recs.map(function (r) { return Number(r.p) || 0; }).filter(function (p) { return p > 0; });
    var low = lows.length ? Math.min.apply(null, lows) : 0;
    if (low > 0 && low < price) return '<div class="hist">📉 歷史低 <b>$' + low.toLocaleString() + '</b></div>';
    if (recs.length >= 2) return '<div class="hist">📉 <b>歷史新低價</b></div>';
    return '';
  }
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
  function verifiedBench(d) {
    // 折扣只認多平台比價：對照價來自其他賣場平均價或歷史均價才算真折扣，
    // 不比單一平台自標價（2026-10-21 使用者定版：單平台折價水分太大）
    return !!d && (d.benchmark_src === 'avg_others' || d.benchmark_src === 'history_avg');
  }

  function isExpiring(d) {
    // 即期品判定（2026-10-21 使用者定版）：名稱有「即期」字眼或 expiring 旗標者進專區
    return !!d && (!!d.expiring || String(d.name || '').indexOf('即期') >= 0);
  }

  function listableDeal(d) {
    // 上架閘門（2026-10-21 使用者嚴格定版）：沒跨平台比價證明、或比完沒有比較便宜的
    // 商品一律不上架；快訊（flash）為即時驗證的標錯價／限時特價，獨立成立；
    // 即期品經雷達驗證價格後進專區。
    if (!d) return false;
    if (d.flash || isExpiring(d)) return true;
    return verifiedBench(d) && num(d.market_price) > num(d.price);
  }

  function sortDeals(list, mode) {
    var arr = list.slice();
    if (mode === 'rec') return arr;
    function disc(d) {
      if (!verifiedBench(d)) return -9999; // 未經多平台比價驗證的不以折扣排序
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
    if (market > price && verifiedBench(d)) {
      var off = Math.round((1 - price / market) * 100);
      var save = market - price;
      // 蝦皮/momo 式：折扣 % 大標籤＋現省金額
      badge = '<span class="badge">-' + off + '%</span>';
      was = '<span class="was">對照 $' + market.toLocaleString() + '</span>';
      saveHtml = '<span class="save">現省 $' + save.toLocaleString() + '</span>';
    } else {
      badge = '<span class="badge good" title="本站收錄優惠・多平台比價驗證中">好價</span>';
      was = '';
      saveHtml = '';
    }
    var url = String(d.url || '').trim();
    var btn = '';
    if (/^https?:/.test(url)) {
      var key = esc(dealKey(url)), title = esc(d.name);
      btn = '<div class="btnrow"><a class="btn" href="' + esc(url) + '" target="_blank" rel="noopener" title="跳到 momo、PChome、蝦皮等大網站結帳，本站不經手付款">' + '去看看 →' + '</a>'
        + '<button class="watchbtn" data-key="' + key + '" data-title="' + title + '" data-price="' + price
        + '" onclick="watchDeal(this)" title="追蹤降價">🔔</button></div>';
    }
    var img = String(d.image || '').trim();
    var pic = /^https?:/.test(img)
      ? '<div class="pic"><img loading="lazy" src="' + esc(img) + '" alt="' + esc(d.name) + '" onerror="this.closest(\'.pic\').style.display=\'none\'"></div>'
      : '';
    var nowTxt = '$' + price.toLocaleString();
    // 免運標示（學生視角：低價小物先看有沒有免運；與 render.py 同步）
    var shipTxt = String(d.name || '') + ' ' + String(d.note || '');
    var shipHtml = shipTxt.indexOf('免運') >= 0 ? '<span class="badge ship">🚚 免運</span>' : '';
    // 來源/賣家去重：相同時只顯示來源（與 render.py 同步）
    var src = String(d.source || '').trim(), sel = String(d.seller || '').trim();
    var norm = function (s) { return s.toLowerCase().replace(/[\s　]/g, ''); };
    var sellerHtml = (!sel || norm(sel) === norm(src)) ? '' : '<span>👤 ' + esc(sel) + '</span>';
    return '<div class="card"><div class="row">' + pic + '<div class="body">'
      + '<div class="top"><h3>' + esc(d.name) + '</h3>' + badge + shipHtml + '</div>'
      + '<div class="price"><span class="now">' + nowTxt + '</span>' + was + saveHtml + '</div>'
      + histHTML(d, price)
      + '<div class="meta"><span>📦 ' + esc(src) + '</span>' + sellerHtml + '<br><span>📝 ' + esc(d.note) + '</span></div>'
      + btn + '</div></div></div>';
  }

  function expiringHTML(d) {
    var price = Number(d.price) || 0, market = Number(d.market_price) || 0;
    var off = market > price ? '下殺 ' + Math.round((1 - price / market) * 100) + '%' : '即期特價';
    var base = _catFilter ? '../' : '';
    var href = base + 'flash/' + flashSlugOf(d) + '.html';
    return '<article class="flash exp"><h3><a href="' + href + '">⏳ ' + esc(d.name) + '</a></h3>'
      + '<div class="fprice">$' + price.toLocaleString()
      + ' <span class="foff">(' + off + ')</span></div>'
      + '<div class="time">📰 來源：' + esc(d.source) + '・發現時間：' + esc(d.found_at) + '</div>'
      + '<p class="fexc">' + esc(d.note) + '</p>'
      + '<div style="margin-top:8px"><a class="btn flashbtn" href="' + href + '">看消息 →</a></div></article>';
  }

  function flashHTML(d) {
    var price = Number(d.price) || 0, market = Number(d.market_price) || 0;
    var off = (market > price && verifiedBench(d)) ? '下殺 ' + Math.round((1 - price / market) * 100) + '%' : '特賣價';
    var base = _catFilter ? '../' : '';
    var href = base + 'flash/' + flashSlugOf(d) + '.html';
    return '<article class="flash"><h3><a href="' + href + '">⚡ ' + esc(d.name) + '</a></h3>'
      + '<div class="fprice">$' + price.toLocaleString()
      + ' <span class="foff">(' + off + ')</span></div>'
      + '<div class="time">📰 來源：' + esc(d.source) + '・發現時間：' + esc(d.found_at) + '</div>'
      + '<p class="fexc">' + esc(d.note) + '</p>'
      + '<div style="margin-top:8px"><a class="btn flashbtn" href="' + href + '">看消息 →</a></div></article>';
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
      loadHist(); // 歷史價格到手後再重繪一次補上「📉 歷史低」標示
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
    return '<div class="floor-head">'
      + '<div class="floor-tt"><h2>' + esc(fm.fname) + '</h2><p>' + esc(fm.desc) + '</p></div>'
      + '<span class="dealcount">' + total + ' 則</span></div>';
  }

  function renderAll() {
    var main = document.querySelector('main.content');
    if (!main || !_cache) return;
    var _sy = window.scrollY || document.documentElement.scrollTop || 0; // 重繪前記住捲動位置，避免動態載入時版面跳動（午休滑動情境）
    var deals = _cache.filter(listableDeal), catFilter = _catFilter, mode = getSortMode();

    // 排序列：只保留在分類頁（首頁改百貨樓層制，固定以折扣力度排序，不顯示排序列）
    if (catFilter) ensureSortbar(main);
    else { var oldBar = main.querySelector('.sortbar'); if (oldBar) oldBar.remove(); }

    // 快訊區（維持發現順序，不參與排序；即期品不混快訊，獨立成專區）
    var flash = deals.filter(function (d) { return d.flash && !isExpiring(d); }).slice(0, 5);
    var flashSec = main.querySelector('.flash-sec:not(.expiring-sec)');
    if (flash.length) {
      var fhtml = '<section class="flash-sec"><h2>⚡ 特賣消息・清場快訊</h2>\n' + flash.map(flashHTML).join('\n') + '\n</section>';
      if (flashSec) flashSec.outerHTML = fhtml;
      else main.insertAdjacentHTML('afterbegin', fhtml);
    } /* 抓到的資料無快閃時保留靜態快照的快閃區（同步延遲時也不讓快閃消失，2026-10-20 事故防呆） */

    // 即期品專區（2026-10-21 使用者定版：即期品獨立成區，不混快訊與商品列）
    var exp = deals.filter(isExpiring);
    var expSec = main.querySelector('.expiring-sec');
    if (exp.length && !_catFilter) {
      var ehtml = '<section class="flash-sec expiring-sec"><h2>⏳ 即期品專區</h2>\n'
        + exp.slice(0, 5).map(expiringHTML).join('\n')
        + (exp.length > 5 ? '\n<p class="expmore"><a href="expiring.html">看全部即期品 →</a></p>' : '')
        + '\n</section>';
      if (expSec) expSec.outerHTML = ehtml;
      else if (flashSec) flashSec.insertAdjacentHTML('afterend', ehtml);
      else main.insertAdjacentHTML('afterbegin', ehtml);
    }

    // 分組（不含 flash 與即期品；stockup／推薦／贊助一律回到所屬樓層，與靜態快照一致）
    var order = [], byCat = {};
    deals.filter(function (d) { return !d.flash && !isExpiring(d); }).forEach(function (d) {
      var c = d.category || '其他';
      if (!byCat[c]) { byCat[c] = []; order.push(c); }
      byCat[c].push(d);
    });
    // 移除舊的 deal-sec（樓層與分類區全部重建）
    main.querySelectorAll('section.deal-sec:not(.articles-sec)').forEach(function (s) { s.remove(); }); // 保留文章專區（2026-10-21 修正：原本會被一起清掉，使用者找不到文章入口）
    var html = '';
    if (!catFilter) {
      // 首頁：百貨樓層（1F→8F→B1），每層折扣力度最高前 8 筆＋「逛完整層」
      var covered = {};
      HK_FLOORS.forEach(function (fm) {
        var items = byCat[fm.name];
        if (!items || !items.length) return;
        covered[fm.name] = true;
        var show = sortDeals(items, 'off').slice(0, 8);
        html += '<section class="deal-sec floor-sec" id="floor-' + fm.slug + '" aria-label="' + fm.fname + '">\n'
          + floorHeadHTML(fm, items.length) + '\n'
          + show.map(cardHTML).join('\n')
          + '\n<div class="morebtn"><a href="cat/' + fm.slug + '.html">看全部優惠 →</a></div></section>';
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
        var label = fm ? fm.fname : c;
        html += '<section class="deal-sec"><h2>' + esc(label) + '<span class="dealcount">' + items.length + ' 則</span></h2>\n'
          + items.map(cardHTML).join('\n') + '\n</section>';
      });
    }
    if (!html) html = '<section><h2>暫無情報</h2><div class="card"><div class="body">此分類尚無優惠情報，站長搜刮中，敬請期待！</div></div></section>';
    // 插到特賣會場後面（沒有時插到排序列後面，再無則插到主欄最前）
    var ref = main.querySelector('.flash-sec') || main.querySelector('.sortbar');
    if (ref) ref.insertAdjacentHTML('afterend', html);
    else main.insertAdjacentHTML('afterbegin', html);

    setupTabs(main);
    setupFeatureTabs(main);
    setupPagination(main);
    // 更新 hero 計數
    var stat = document.querySelector('.hero-stats b');
    if (stat) stat.textContent = deals.length;
    if (_sy) window.scrollTo(0, _sy); // 恢復捲動位置
  }

  // 分類 slug 對照（首頁「看更多」用）
  window.HK_CAT_SLUGS = {
    '3C數位': '3c', '家電': 'appliance', '美妝保養': 'beauty',
    '服飾鞋包': 'fashion', '食品日用': 'grocery', '母嬰玩具': 'baby',
    '運動戶外': 'sports', '居家生活': 'home', '寵物生活': 'pet'
  };

  // 首頁主功能切換：今日好康／特賣消息一次只顯示一區；文章、搜尋、會員走獨立導覽頁
  function setupFeatureTabs(main) {
    if (!main || main.getAttribute('data-cat')) return;
    var switcher = main.querySelector('.feature-switcher');
    if (!switcher) return;

    function parts() {
      return {
        flash: main.querySelector('.flash-sec'),
        catbar: main.querySelector('.cattabs'),
        secs: Array.prototype.slice.call(main.querySelectorAll('section.deal-sec:not(.articles-sec)'))
      };
    }
    function activate(key, scroll) {
      var p = parts();
      if (!p.flash && key === 'flash') key = 'deals';
      Array.prototype.forEach.call(switcher.querySelectorAll('[data-feature-tab]'), function (b) {
        var on = b.getAttribute('data-feature-tab') === key;
        b.classList.toggle('on', on);
        b.setAttribute('aria-selected', on ? 'true' : 'false');
      });
      if (key === 'flash') {
        if (p.flash) p.flash.style.display = '';
        if (p.catbar) p.catbar.style.display = 'none';
        p.secs.forEach(function (sec) { sec.style.display = 'none'; });
      } else {
        if (p.flash) p.flash.style.display = 'none';
        if (p.catbar) p.catbar.style.display = '';
        var activeBtn = p.catbar ? p.catbar.querySelector('button.on') : null;
        var activeId = activeBtn ? activeBtn.getAttribute('data-tab') : null;
        p.secs.forEach(function (sec, i) {
          sec.style.display = activeId ? (sec.id === activeId ? '' : 'none') : (i === 0 ? '' : 'none');
        });
      }
      try { sessionStorage.setItem('hk_feature', key); } catch (e) {}
      if (scroll) switcher.scrollIntoView({ block: 'start' });
    }
    if (!switcher._hkFeatureBound) {
      switcher._hkFeatureBound = true;
      switcher.addEventListener('click', function (e) {
        var b = e.target.closest ? e.target.closest('[data-feature-tab]') : null;
        if (b) activate(b.getAttribute('data-feature-tab'), true);
      });
    }
    var flashBtn = switcher.querySelector('[data-feature-tab="flash"]');
    if (flashBtn && !parts().flash) flashBtn.hidden = true;
    var saved = null;
    try { saved = sessionStorage.getItem('hk_feature'); } catch (e) {}
    activate(saved === 'flash' ? 'flash' : 'deals', false);
  }

  // 分類頁分頁導覽：每頁 12 則，不再把 20–30 張卡片一次拉到底
  function setupPagination(main) {
    if (!main || !main.getAttribute('data-cat')) return;
    Array.prototype.forEach.call(main.querySelectorAll('section.deal-sec'), function (sec) {
      var old = sec.querySelector('.pager');
      if (old) old.remove();
      var cards = Array.prototype.slice.call(sec.querySelectorAll(':scope > .card'));
      if (cards.length <= 12) {
        cards.forEach(function (card) { card.style.display = ''; });
        return;
      }
      var pageSize = 12;
      var page = 1;
      var pages = Math.ceil(cards.length / pageSize);
      var pager = document.createElement('div');
      pager.className = 'pager';
      sec.appendChild(pager);
      function draw() {
        cards.forEach(function (card, i) {
          card.style.display = i >= (page - 1) * pageSize && i < page * pageSize ? '' : 'none';
        });
        var nums = [];
        for (var n = 1; n <= pages; n++) {
          if (pages <= 7 || n === 1 || n === pages || Math.abs(n - page) <= 1) nums.push(n);
          else if (nums[nums.length - 1] !== '…') nums.push('…');
        }
        pager.innerHTML = '<button type="button" data-act="prev"' + (page === 1 ? ' disabled' : '') + '>← 上一頁</button>'
          + nums.map(function (n) {
              return n === '…'
                ? '<span class="pager-info">…</span>'
                : '<button type="button" data-page="' + n + '"' + (n === page ? ' class="on"' : '') + '>' + n + '</button>';
            }).join('')
          + '<span class="pager-info">' + page + ' / ' + pages + ' 頁・共 ' + cards.length + ' 則</span>'
          + '<button type="button" data-act="next"' + (page === pages ? ' disabled' : '') + '>下一頁 →</button>';
      }
      pager.addEventListener('click', function (e) {
        var b = e.target.closest ? e.target.closest('button') : null;
        if (!b || b.disabled) return;
        if (b.getAttribute('data-act') === 'prev') page--;
        else if (b.getAttribute('data-act') === 'next') page++;
        else if (b.getAttribute('data-page')) page = Number(b.getAttribute('data-page'));
        draw();
        sec.scrollIntoView({ block: 'start' });
      });
      draw();
    });
  }

  // 首頁分類頁籤切換（使用者定調：不要一頁長捲，用導航切轉）
  function setupTabs(main) {
    if (!main || main.getAttribute('data-cat')) return;
    var secs = Array.prototype.slice.call(main.querySelectorAll('section.deal-sec:not(.articles-sec)'));
    if (secs.length < 2) return;
    var old = main.querySelector('.cattabs');
    if (old) old.remove();
    var bar = document.createElement('div');
    bar.className = 'cattabs';
    var saved = null;
    try { saved = sessionStorage.getItem('hk_tab'); } catch (e) {}
    var hasSaved = false;
    secs.forEach(function (sec, i) {
      if (!sec.id) sec.id = 'sec-' + i;
      var h2 = sec.querySelector('h2');
      var label = sec.getAttribute('aria-label') || (h2 ? h2.textContent.replace(/[0-9]+\s*則/g, '').trim() : ('分類' + (i + 1)));
      var b = document.createElement('button');
      b.textContent = label;
      b.setAttribute('data-tab', sec.id);
      b.addEventListener('click', function () { activate(sec.id, true); });
      bar.appendChild(b);
      if (saved === sec.id) hasSaved = true;
    });
    function activate(key, scroll) {
      secs.forEach(function (sec) { sec.style.display = sec.id === key ? '' : 'none'; });
      Array.prototype.forEach.call(bar.querySelectorAll('button'), function (b) {
        b.classList.toggle('on', b.getAttribute('data-tab') === key);
      });
      try { sessionStorage.setItem('hk_tab', key); } catch (e) {}
      if (scroll) bar.scrollIntoView({ block: 'start' });
    }
    secs[0].parentNode.insertBefore(bar, secs[0]);
    activate(hasSaved ? saved : secs[0].id, false);
  }
  function activateTabById(id) {
    var bar = document.querySelector('.cattabs');
    if (!bar) return false;
    var b = bar.querySelector('button[data-tab="' + id + '"]');
    if (b) { b.click(); return true; }
    return false;
  }

  document.addEventListener('DOMContentLoaded', function () {
    var main0 = document.querySelector('main.content');
    if (main0) {
      setupTabs(main0);
      setupFeatureTabs(main0);
      setupPagination(main0);
    }
    Array.prototype.forEach.call(document.querySelectorAll('.floornav a[href^="#floor-"]'), function (a) {
      a.addEventListener('click', function (e) {
        var dealsBtn = document.querySelector('[data-feature-tab="deals"]');
        if (dealsBtn) dealsBtn.click();
        if (activateTabById(a.getAttribute('href').slice(1))) e.preventDefault();
      });
    });
    // 等 supabase script 載入後再跑
    var tries = 0;
    (function wait() {
      if (window.supabase || tries++ > 20) refresh();
      else setTimeout(wait, 250);
    })();
  });
})();
