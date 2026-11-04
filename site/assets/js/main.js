/* Sakīna – interactions, Three.js background, live Arabic loader */
(function () {
  'use strict';
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var body = document.body;
  var calm = false;
  try { calm = localStorage.getItem('sakina-calm') === '1'; } catch (e) {}
  if (calm) { reduce = true; body.classList.add('calm'); }
  var calmBtn = document.querySelector('.calm-btn');
  if (calmBtn) {
    calmBtn.setAttribute('aria-pressed', calm ? 'true' : 'false');
    calmBtn.textContent = calm ? 'Calm mode: on' : 'Calm mode';
    calmBtn.addEventListener('click', function () {
      try { localStorage.setItem('sakina-calm', calm ? '0' : '1'); } catch (e) {}
      window.location.reload();
    });
  }
  var toastEl = document.getElementById('toast'), toastT;
  function toast(msg) {
    if (!toastEl) return; toastEl.textContent = msg; toastEl.classList.add('show');
    clearTimeout(toastT); toastT = setTimeout(function () { toastEl.classList.remove('show'); }, 4200);
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('.report'); if (!b) return;
    var msg = 'Sakina – possible mistake. Page: ' + b.dataset.page + ' | Reference: ' + b.dataset.ref + ' | What looks wrong: ';
    var done = function () { toast('Copied a note about ' + b.dataset.ref + '. Paste it into a message to the site owner and add what looks wrong.'); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(msg).then(done, function () { toast(msg); });
    else toast(msg);
  });
  /* reviewer checklist */
  var rvs = document.querySelectorAll('input.rv');
  if (rvs.length) {
    var saved = {}; try { saved = JSON.parse(localStorage.getItem('sakina-rev') || '{}'); } catch (e) {}
    var cnt = document.getElementById('rvc');
    var upd = function () { var n = 0; rvs.forEach(function (c) { if (c.checked) n++; }); if (cnt) cnt.textContent = n + ' of ' + rvs.length + ' reviewed in this browser'; };
    rvs.forEach(function (c) {
      c.checked = !!saved[c.dataset.k];
      c.addEventListener('change', function () { saved[c.dataset.k] = c.checked; try { localStorage.setItem('sakina-rev', JSON.stringify(saved)); } catch (e) {} upd(); });
    });
    upd();
  }
  var hue = parseFloat(body.dataset.hue || '45');
  body.style.setProperty('--h', hue);

  /* ---------- page enter / leave ---------- */
  requestAnimationFrame(function () { body.classList.add('ready'); });
  window.addEventListener('pageshow', function (e) { if (e.persisted) { body.classList.remove('leaving'); body.classList.add('ready'); } });
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a || reduce) return;
    var href = a.getAttribute('href');
    if (!href || a.target === '_blank' || href.charAt(0) === '#' || /^(https?:|mailto:|tel:)/.test(href)) return;
    if (e.metaKey || e.ctrlKey || e.shiftKey) return;
    e.preventDefault(); body.classList.add('leaving');
    setTimeout(function () { window.location.href = href; }, 220);
  });

  /* ---------- split headline into words ---------- */
  document.querySelectorAll('.split').forEach(function (h) {
    var words = h.textContent.trim().split(/\s+/);
    h.setAttribute('aria-label', h.textContent.trim());
    h.innerHTML = words.map(function (w, i) {
      return '<span class="w" aria-hidden="true"><span style="--i:' + i + '">' + w.replace(/&/g, '&amp;') + '</span></span>';
    }).join(' ');
  });

  /* ---------- reveal on scroll ---------- */
  var revealEls = [].slice.call(document.querySelectorAll('.reveal'));
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { threshold: 0.08, rootMargin: '0px 0px -6% 0px' });
    revealEls.forEach(function (el) {
      var sib = el.parentElement ? [].indexOf.call(el.parentElement.children, el) : 0;
      el.style.setProperty('--d', (sib % 3) * 90 + 'ms');
      io.observe(el);
    });
  } else { revealEls.forEach(function (el) { el.classList.add('in'); }); }

  /* ---------- reading progress + glow follow ---------- */
  var bar = document.querySelector('.progress i');
  var glow = document.querySelector('.glow');
  var scrollY = 0, maxScroll = 1;
  function onScroll() {
    scrollY = window.pageYOffset;
    maxScroll = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
    if (bar) bar.style.transform = 'scaleX(' + Math.min(1, scrollY / maxScroll) + ')';
  }
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();
  var mouse = { x: 0, y: 0 };
  window.addEventListener('pointermove', function (e) {
    mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
    mouse.y = (e.clientY / window.innerHeight) * 2 - 1;
    if (glow && e.pointerType === 'mouse') glow.style.transform = 'translate3d(' + e.clientX + 'px,' + e.clientY + 'px,0)';
  }, { passive: true });

  /* ---------- 3D card tilt ---------- */
  if (window.matchMedia('(hover:hover) and (pointer:fine)').matches && !reduce) {
    document.querySelectorAll('.tilt').forEach(function (el) {
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
        el.style.setProperty('--mx', (x * 100) + '%'); el.style.setProperty('--my', (y * 100) + '%');
        el.style.transform = 'perspective(900px) rotateX(' + ((0.5 - y) * 5) + 'deg) rotateY(' + ((x - 0.5) * 6) + 'deg) translateZ(0)';
      });
      el.addEventListener('pointerleave', function () { el.style.transform = ''; });
    });
  }

  /* ---------- live Arabic from the Qur'an API (Uthmani script) ---------- */
  var CK = 'sakina-ar-v1', cache = {};
  try { cache = JSON.parse(localStorage.getItem(CK) || '{}'); } catch (e) { cache = {}; }
  function saveCache() { try { localStorage.setItem(CK, JSON.stringify(cache)); } catch (e) {} }
  function norm(s) { return s.replace(/[ً-ٰٟۖ-ۭـ]/g, '').replace(/ٱ/g, 'ا'); }
  function stripBasmala(t) {
    var parts = t.split(/\s+/);
    if (parts.length > 4 && norm(parts.slice(0, 4).join(' ')) === norm('بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ')) return parts.slice(4).join(' ');
    return t;
  }
  function getAyah(key) {
    if (cache[key]) return Promise.resolve(cache[key]);
    return fetch('https://api.alquran.cloud/v1/ayah/' + key + '/quran-uthmani')
      .then(function (r) { if (!r.ok) throw new Error('http ' + r.status); return r.json(); })
      .then(function (j) {
        var d = j.data, t = d.text;
        if (d.numberInSurah === 1 && d.surah.number !== 1) t = stripBasmala(t);
        cache[key] = t; saveCache(); return t;
      });
  }
  var AR_NUM = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];
  function arNum(n) { return String(n).split('').map(function (d) { return AR_NUM[+d]; }).join(''); }
  function loadArabic(el, keys) {
    return Promise.all(keys.map(getAyah)).then(function (texts) {
      el.innerHTML = texts.map(function (t, i) {
        var n = keys[i].split(':')[1];
        return t + ' <span class="ayah-no">۝' + arNum(n) + '</span>';
      }).join(' ');
      el.classList.add('loaded');
    }).catch(function () {
      var ref = keys[0] + (keys.length > 1 ? '–' + keys[keys.length - 1].split(':')[1] : '');
      var k = keys[0].split(':');
      el.classList.add('failed');
      el.innerHTML = 'Arabic text loads when you are online. <a href="https://quran.com/' + k[0] + '/' + k[1] + '" target="_blank" rel="noopener">Read ' + ref + ' on Quran.com ↗</a>';
    });
  }
  document.querySelectorAll('.ar[data-ayahs]').forEach(function (el) {
    var keys = el.dataset.ayahs.split(',').filter(Boolean);
    if (keys.length) loadArabic(el, keys);
  });

  /* ---------- verse of the moment (home) ---------- */
  var vomData = document.getElementById('vom-data');
  if (vomData) {
    var items = [].slice.call(vomData.children), idx = Math.floor(Math.random() * items.length);
    var ar = document.getElementById('vom-ar'), en = document.getElementById('vom-en'), link = document.getElementById('vom-link');
    [ar, en, link.parentNode].forEach(function (n) { n.classList.add('swap'); });
    var showVerse = function () {
      var it = items[idx], ref = it.dataset.ref, s = ref.split(':');
      en.textContent = it.dataset.en;
      link.textContent = 'Qur’an ' + ref.replace('-', '–') + ' ↗';
      link.href = 'https://quran.com/' + s[0] + '/' + s[1];
      ar.style.display = it.dataset.arabic === '1' ? '' : 'none';
      ar.classList.remove('failed', 'loaded'); ar.innerHTML = '';
      if (it.dataset.arabic === '1') loadArabic(ar, it.dataset.ayahs.split(','));
      [ar, en, link.parentNode].forEach(function (n) { n.classList.remove('out'); });
    };
    showVerse();
    document.getElementById('vom-next').addEventListener('click', function () {
      [ar, en, link.parentNode].forEach(function (n) { n.classList.add('out'); });
      setTimeout(function () { idx = (idx + 1) % items.length; showVerse(); }, 420);
    });
  }

  /* ---------- breathing guide ---------- */
  var breath = document.querySelector('.breath');
  if (breath) {
    var cue = breath.querySelector('.cue'), running = false, timer = null;
    var step = function () {
      if (!running) return;
      breath.classList.remove('out'); breath.classList.add('in'); cue.textContent = 'Breathe in…';
      timer = setTimeout(function () {
        if (!running) return;
        breath.classList.remove('in'); breath.classList.add('out'); cue.textContent = 'Slowly out…';
        timer = setTimeout(step, 6000);
      }, 4000);
    };
    breath.addEventListener('click', function () {
      running = !running; clearTimeout(timer);
      if (running) step(); else { breath.classList.remove('in', 'out'); cue.textContent = 'Tap to begin'; }
    });
  }

  /* ---------- Three.js background ---------- */
  function initScene() {
    if (typeof THREE === 'undefined') return;
    var canvas = document.getElementById('bg'), renderer;
    try { renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true, powerPreference: 'low-power' }); }
    catch (e) { return; }
    var lowPower = window.innerWidth < 700;
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, lowPower ? 1.5 : 2));
    renderer.setClearColor(0x060914, 1);
    var scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x060914, 0.012);
    var camera = new THREE.PerspectiveCamera(58, 1, 0.1, 400);
    camera.position.set(0, 0, 34);

    var theme = new THREE.Color().setHSL(hue / 360, 0.78, 0.68);
    var gold = new THREE.Color(0xecd28f);

    function glowTex(inner) {
      var c = document.createElement('canvas'); c.width = c.height = 128;
      var g = c.getContext('2d'), grd = g.createRadialGradient(64, 64, 0, 64, 64, 64);
      grd.addColorStop(0, inner || 'rgba(255,255,255,1)'); grd.addColorStop(0.25, 'rgba(255,255,255,.55)'); grd.addColorStop(1, 'rgba(255,255,255,0)');
      g.fillStyle = grd; g.fillRect(0, 0, 128, 128);
      return new THREE.CanvasTexture(c);
    }
    var dot = glowTex();

    /* stars */
    var N = lowPower ? 900 : 2200, pos = new Float32Array(N * 3), col = new Float32Array(N * 3), seed = new Float32Array(N);
    for (var i = 0; i < N; i++) {
      var r = 25 + Math.random() * 120, th = Math.random() * Math.PI * 2, ph = Math.acos(2 * Math.random() - 1);
      pos[i * 3] = r * Math.sin(ph) * Math.cos(th); pos[i * 3 + 1] = r * Math.sin(ph) * Math.sin(th) * 0.7; pos[i * 3 + 2] = r * Math.cos(ph) - 20;
      var m = Math.random(), c = new THREE.Color().copy(m < 0.55 ? new THREE.Color(0xffffff) : (m < 0.8 ? theme : gold)).multiplyScalar(0.5 + Math.random() * 0.7);
      col[i * 3] = c.r; col[i * 3 + 1] = c.g; col[i * 3 + 2] = c.b; seed[i] = Math.random() * 6.28;
    }
    var sg = new THREE.BufferGeometry();
    sg.setAttribute('position', new THREE.BufferAttribute(pos, 3)); sg.setAttribute('color', new THREE.BufferAttribute(col, 3));
    var stars = new THREE.Points(sg, new THREE.PointsMaterial({ size: lowPower ? 1.3 : 1.05, map: dot, vertexColors: true, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, opacity: 0.95 }));
    scene.add(stars);

    /* eight-pointed star (khātam) emblem */
    function starShape(R, ratio) {
      var s = new THREE.Shape(), pts = 16, rr = R * ratio;
      for (var k = 0; k < pts; k++) {
        var a = (k / pts) * Math.PI * 2 - Math.PI / 2, rad = k % 2 === 0 ? R : rr;
        var x = Math.cos(a) * rad, y = Math.sin(a) * rad;
        if (k === 0) s.moveTo(x, y); else s.lineTo(x, y);
      }
      s.closePath(); return s;
    }
    var emblem = new THREE.Group();
    var R = 9, ratio = 0.7654;
    var geo = new THREE.ExtrudeGeometry(starShape(R, ratio), { depth: 1.4, bevelEnabled: false });
    geo.translate(0, 0, -0.7);
    var edges = new THREE.LineSegments(new THREE.EdgesGeometry(geo), new THREE.LineBasicMaterial({ color: theme, transparent: true, opacity: 0.9, blending: THREE.AdditiveBlending }));
    var fill = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: theme, transparent: true, opacity: 0.07, depthWrite: false, side: THREE.DoubleSide }));
    emblem.add(fill, edges);
    var inner = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.ExtrudeGeometry(starShape(R * 0.62, ratio), { depth: 0.6, bevelEnabled: false })), new THREE.LineBasicMaterial({ color: gold, transparent: true, opacity: 0.75, blending: THREE.AdditiveBlending }));
    inner.rotation.z = Math.PI / 8; emblem.add(inner);
    var core = new THREE.Sprite(new THREE.SpriteMaterial({ map: dot, color: theme, transparent: true, opacity: 0.85, blending: THREE.AdditiveBlending, depthWrite: false }));
    core.scale.set(7, 7, 1); emblem.add(core);
    /* orbit ring of particles */
    var RN = 160, rp = new Float32Array(RN * 3);
    for (var j = 0; j < RN; j++) { var a2 = (j / RN) * Math.PI * 2; rp[j * 3] = Math.cos(a2) * 15; rp[j * 3 + 1] = Math.sin(a2) * 15; rp[j * 3 + 2] = (Math.random() - 0.5) * 1.2; }
    var rg = new THREE.BufferGeometry(); rg.setAttribute('position', new THREE.BufferAttribute(rp, 3));
    var ring = new THREE.Points(rg, new THREE.PointsMaterial({ size: 0.9, map: dot, color: gold, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, opacity: 0.8 }));
    emblem.add(ring);
    scene.add(emblem);

    /* soft aurora sprites */
    var auroras = [];
    [[-30, 14, -60, 0], [34, -16, -70, 40], [0, 30, -90, -40]].forEach(function (p) {
      var s = new THREE.Sprite(new THREE.SpriteMaterial({ map: dot, color: new THREE.Color().setHSL(((hue + p[3] + 360) % 360) / 360, 0.7, 0.45), transparent: true, opacity: 0.18, depthWrite: false, blending: THREE.AdditiveBlending }));
      s.position.set(p[0], p[1], p[2]); s.scale.set(90, 90, 1); scene.add(s); auroras.push(s);
    });

    /* shooting star */
    var shoot = new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0, 0, 0), new THREE.Vector3(-6, 3, 0)]),
      new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0, blending: THREE.AdditiveBlending }));
    scene.add(shoot); var shootT = -1, nextShoot = 3;

    var isHome = !!document.querySelector('.home-hero');
    function layout() {
      var w = window.innerWidth, h = window.innerHeight;
      renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
      var wide = w > 980;
      emblem.position.set(wide ? 17 : 0, wide ? 3 : 9, wide ? -4 : -22);
      var sc = wide ? (isHome ? 1.15 : 0.95) : 0.8; emblem.scale.setScalar(sc);
    }
    layout(); window.addEventListener('resize', layout);

    var t0 = performance.now(), running = true, camX = 0, camY = 0;
    function frame(now) {
      var t = (now - t0) / 1000;
      camX += (mouse.x * 2.6 - camX) * 0.04; camY += (-mouse.y * 1.6 - camY) * 0.04;
      var sp = scrollY / maxScroll;
      camera.position.x = camX; camera.position.y = camY - sp * 10;
      camera.lookAt(0, -sp * 10, 0);
      stars.rotation.y = t * 0.012 + sp * 0.5; stars.rotation.x = Math.sin(t * 0.05) * 0.05;
      emblem.rotation.z = t * 0.07 + sp * 1.6; emblem.rotation.y = Math.sin(t * 0.25) * 0.35 + mouse.x * 0.25; emblem.rotation.x = Math.cos(t * 0.2) * 0.2 - mouse.y * 0.2;
      inner.rotation.z = Math.PI / 8 - t * 0.14; ring.rotation.z = t * 0.12;
      emblem.position.y += (Math.sin(t * 0.6) * 0.012);
      core.material.opacity = 0.65 + Math.sin(t * 1.4) * 0.2;
      for (var q = 0; q < auroras.length; q++) { auroras[q].position.x += Math.sin(t * 0.1 + q) * 0.01; auroras[q].material.opacity = 0.14 + Math.sin(t * 0.3 + q * 2) * 0.05; }
      /* twinkle */
      stars.material.opacity = 0.85 + Math.sin(t * 0.8) * 0.1;
      /* shooting star */
      if (shootT < 0 && t > nextShoot) { shootT = 0; shoot.position.set(-30 + Math.random() * 40, 18 + Math.random() * 8, -20); }
      if (shootT >= 0) { shootT += 0.016; shoot.position.x += 1.1; shoot.position.y -= 0.55; shoot.material.opacity = Math.max(0, Math.sin(Math.min(1, shootT / 0.9) * Math.PI)) * 0.9; if (shootT > 0.9) { shootT = -1; nextShoot = t + 5 + Math.random() * 7; shoot.material.opacity = 0; } }
      renderer.render(scene, camera);
    }
    if (reduce) { frame(performance.now()); return; }
    (function loop(now) { if (running) frame(now || performance.now()); requestAnimationFrame(loop); })();
    document.addEventListener('visibilitychange', function () { running = !document.hidden; });
  }

  /* ---------- tap counters (tasbih) ---------- */
  document.querySelectorAll('.tasbihs').forEach(function (box) {
    var btns = [].slice.call(box.querySelectorAll('.tasbih'));
    btns.forEach(function (b) {
      var n = 0, target = +b.dataset.target, out = b.querySelector('.tn');
      b._reset = function () { n = 0; out.textContent = target ? '0 / ' + target : '0'; b.classList.remove('done'); };
      b.addEventListener('click', function () {
        if (target && n >= target) return;
        n++; out.textContent = target ? n + ' / ' + target : String(n);
        b.classList.remove('pop'); void b.offsetWidth; b.classList.add('pop');
        if (navigator.vibrate) { try { navigator.vibrate(target && n === target ? 60 : 8); } catch (e) {} }
        if (target && n >= target) { b.classList.add('done'); out.textContent = '✓ ' + target; }
      });
    });
    box.querySelector('.tasbih-reset').addEventListener('click', function () { btns.forEach(function (b) { b._reset(); }); });
  });

  /* ---------- prayer times (AlAdhan API) ---------- */
  var PT = 'sakina-pt';
  function ptGet() { try { return JSON.parse(localStorage.getItem(PT) || 'null'); } catch (e) { return null; } }
  function ptSet(v) { try { localStorage.setItem(PT, JSON.stringify(v)); } catch (e) {} }
  var NAMES = [['Fajr', 'Fajr'], ['Sunrise', 'Sunrise'], ['Dhuhr', 'Dhuhr'], ['Asr', 'Asr'], ['Maghrib', 'Maghrib'], ['Isha', 'Isha']];
  var AR_NAMES = { Fajr: 'الفجر', Sunrise: 'الشروق', Dhuhr: 'الظهر', Asr: 'العصر', Maghrib: 'المغرب', Isha: 'العشاء' };
  function ptUrl(st) {
    var q = [];
    if (st.method && st.method !== 'auto') q.push('method=' + encodeURIComponent(st.method));
    if (st.school) q.push('school=' + encodeURIComponent(st.school));
    var extra = q.length ? '&' + q.join('&') : '';
    if (st.lat != null) return 'https://api.aladhan.com/v1/timings?latitude=' + st.lat + '&longitude=' + st.lon + extra;
    return 'https://api.aladhan.com/v1/timingsByCity?city=' + encodeURIComponent(st.city) + '&country=' + encodeURIComponent(st.country) + extra;
  }
  function hm(t) { var m = /(\d{1,2}):(\d{2})/.exec(t || ''); return m ? [+m[1], +m[2]] : null; }
  function show(t, h12) {
    var x = hm(t); if (!x) return '–';
    if (!h12) return (x[0] < 10 ? '0' : '') + x[0] + ':' + (x[1] < 10 ? '0' : '') + x[1];
    var ap = x[0] >= 12 ? 'PM' : 'AM', h = x[0] % 12 || 12; return h + ':' + (x[1] < 10 ? '0' : '') + x[1] + ' ' + ap;
  }
  function nowSecs(tz) {
    try {
      var o = {}; new Intl.DateTimeFormat('en-GB', { timeZone: tz, hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }).formatToParts(new Date()).forEach(function (p) { o[p.type] = p.value; });
      return (+o.hour % 24) * 3600 + (+o.minute) * 60 + (+o.second);
    } catch (e) { var d = new Date(); return d.getHours() * 3600 + d.getMinutes() * 60 + d.getSeconds(); }
  }
  function nextPrayer(timings, tz) {
    var now = nowSecs(tz), list = ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha'], best = null;
    for (var i = 0; i < list.length; i++) {
      var x = hm(timings[list[i]]); if (!x) continue; var t = x[0] * 3600 + x[1] * 60;
      if (t > now) { best = { name: list[i], in: t - now }; break; }
    }
    if (!best) { var f = hm(timings.Fajr); best = { name: 'Fajr', in: (24 * 3600 - now) + f[0] * 3600 + f[1] * 60, tomorrow: true }; }
    return best;
  }
  function dur(sec) {
    var h = Math.floor(sec / 3600), m = Math.floor((sec % 3600) / 60), s = sec % 60;
    return (h ? h + 'h ' : '') + m + 'm' + (h ? '' : ' ' + (s < 10 ? '0' : '') + s + 's');
  }
  function fetchTimes(st) {
    return fetch(ptUrl(st)).then(function (r) { if (!r.ok) throw new Error('http ' + r.status); return r.json(); }).then(function (j) {
      if (!j || !j.data || !j.data.timings) throw new Error('bad');
      var d = j.data, out = { timings: d.timings, tz: d.meta && d.meta.timezone, hijri: d.date && d.date.hijri, greg: d.date && d.date.readable, method: d.meta && d.meta.method && d.meta.method.name, day: new Date().toDateString() };
      try { localStorage.setItem(PT + '-cache', JSON.stringify({ key: ptUrl(st), out: out })); } catch (e) {}
      return out;
    }).catch(function (err) {
      try { var c = JSON.parse(localStorage.getItem(PT + '-cache') || 'null'); if (c && c.key === ptUrl(st) && c.out.day === new Date().toDateString()) { c.out.cached = true; return c.out; } } catch (e) {}
      throw err;
    });
  }

  var ptApp = document.getElementById('pt-app'), ptMini = document.getElementById('pt-mini-body');
  if (ptApp) {
    var f = { country: document.getElementById('pt-country'), city: document.getElementById('pt-city'), method: document.getElementById('pt-method'), school: document.getElementById('pt-school') };
    var status = document.getElementById('pt-status'), grid = document.getElementById('pt-grid'), nextBox = document.getElementById('pt-next'), meta = document.getElementById('pt-meta');
    var h12 = true, data = null, tick = null, saved = ptGet() || {};
    if (saved.h12 === false) h12 = false;
    if (saved.country) f.country.value = saved.country; if (saved.city) f.city.value = saved.city;
    if (saved.method) f.method.value = saved.method; if (saved.school) f.school.value = saved.school;
    var render = function () {
      if (!data) return;
      grid.innerHTML = NAMES.map(function (n) {
        return '<div class="pt-card" data-n="' + n[0] + '"><span class="pn">' + n[1] + '</span><span class="pa" lang="ar">' + AR_NAMES[n[0]] + '</span><span class="pv">' + show(data.timings[n[0]], h12) + '</span></div>';
      }).join('');
      var loc = saved.lat != null ? 'your location' : [saved.city, saved.country].filter(Boolean).join(', ');
      meta.textContent = [loc, data.tz ? 'Time zone: ' + data.tz : '', data.method ? 'Method: ' + data.method : '', data.hijri ? data.hijri.day + ' ' + data.hijri.month.en + ' ' + data.hijri.year + ' AH' : '', data.cached ? '(saved copy, you are offline)' : ''].filter(Boolean).join(' · ');
      update();
    };
    var update = function () {
      if (!data) return;
      var nx = nextPrayer(data.timings, data.tz);
      nextBox.hidden = false;
      document.getElementById('pt-next-name').textContent = nx.name + (nx.tomorrow ? ' (tomorrow)' : '');
      document.getElementById('pt-next-in').textContent = 'in ' + dur(nx.in);
      grid.querySelectorAll('.pt-card').forEach(function (c) { c.classList.toggle('next', c.dataset.n === nx.name); });
    };
    var go = function (st) {
      status.textContent = 'Loading prayer times…'; nextBox.hidden = true;
      fetchTimes(st).then(function (d) {
        data = d; saved = st; saved.h12 = h12; ptSet(saved); status.textContent = ''; render();
        clearInterval(tick); tick = setInterval(update, 1000);
      }).catch(function () {
        status.innerHTML = 'Couldn’t load the times. Please check the country and city spelling and your connection, then try again. Meanwhile your local masjid timetable is the best guide.';
      });
    };
    document.getElementById('pt-form').addEventListener('submit', function (e) {
      e.preventDefault(); go({ country: f.country.value.trim(), city: f.city.value.trim(), method: f.method.value, school: f.school.value, h12: h12 });
    });
    document.getElementById('pt-geo').addEventListener('click', function () {
      if (!navigator.geolocation) { status.textContent = 'Your browser can’t share its location. Please type your city instead.'; return; }
      status.textContent = 'Asking your browser for your location…';
      navigator.geolocation.getCurrentPosition(function (p) {
        go({ lat: p.coords.latitude.toFixed(4), lon: p.coords.longitude.toFixed(4), method: f.method.value, school: f.school.value, h12: h12 });
      }, function () { status.textContent = 'Location was not shared. Please type your country and city instead.'; }, { timeout: 12000 });
    });
    document.getElementById('pt-12h').addEventListener('click', function () { h12 = !h12; saved.h12 = h12; ptSet(saved); render(); });
    if (saved.city || saved.lat != null) go(saved);
  } else if (ptMini) {
    var sv = ptGet();
    if (sv && (sv.city || sv.lat != null)) {
      ptMini.innerHTML = '<span class="muted">Loading…</span>';
      fetchTimes(sv).then(function (d) {
        var draw = function () {
          var nx = nextPrayer(d.timings, d.tz);
          ptMini.innerHTML = '<div class="pt-next mini"><span class="eyebrow">Next prayer</span><strong>' + nx.name + (nx.tomorrow ? ' (tomorrow)' : '') + ' · ' + show(d.timings[nx.name], sv.h12 !== false) + '</strong><span>in ' + dur(nx.in) + '</span></div> <a class="btn" href="prayer-times.html">All times</a>';
        };
        draw(); setInterval(draw, 1000);
      }).catch(function () { ptMini.innerHTML = '<a class="btn primary" href="prayer-times.html">Open prayer times</a>'; });
    }
  }

  if (!calm) initScene();
})();
