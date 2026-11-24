/* 离线授权验证：设备码 → 激活码（HMAC-SHA256），无网络校验 */
(function () {
  'use strict';
  var SECRET = 'KY-2026-SC-7f3a9e2c41b8d605a4e7c1f9b3d82a6e5c0f7b1d';
  var LS_SEED = 'kaoyan_device_seed_v1';
  var LS_LIC = 'kaoyan_license_v1';
  var B32 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';

  function rotr(x, n) { return ((x >>> n) | (x << (32 - n))) >>> 0; }

  function sha256bytes(bytes) {
    var K = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
      0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
      0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
      0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
      0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
      0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
      0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
      0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2];
    var H = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19];
    var l = bytes.length, bl = l * 8;
    var padLen = (((l + 9) + 63) >> 6) << 6;
    var m = new Uint8Array(padLen);
    m.set(bytes); m[l] = 0x80;
    var dv = new DataView(m.buffer);
    dv.setUint32(padLen - 4, bl >>> 0);
    dv.setUint32(padLen - 8, Math.floor(bl / 4294967296));
    var w = new Uint32Array(64), i, j, a, b, c, d, e, f, g, h, s0, s1, S0, S1, ch, maj, t1, t2;
    for (i = 0; i < padLen; i += 64) {
      for (j = 0; j < 16; j++) w[j] = dv.getUint32(i + j * 4);
      for (j = 16; j < 64; j++) {
        s0 = (rotr(w[j - 15], 7) ^ rotr(w[j - 15], 18) ^ (w[j - 15] >>> 3)) >>> 0;
        s1 = (rotr(w[j - 2], 17) ^ rotr(w[j - 2], 19) ^ (w[j - 2] >>> 10)) >>> 0;
        w[j] = (w[j - 16] + s0 + w[j - 7] + s1) >>> 0;
      }
      a = H[0]; b = H[1]; c = H[2]; d = H[3]; e = H[4]; f = H[5]; g = H[6]; h = H[7];
      for (j = 0; j < 64; j++) {
        S1 = (rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25)) >>> 0;
        ch = ((e & f) ^ (~e & g)) >>> 0;
        t1 = (h + S1 + ch + K[j] + w[j]) >>> 0;
        S0 = (rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22)) >>> 0;
        maj = ((a & b) ^ (a & c) ^ (b & c)) >>> 0;
        t2 = (S0 + maj) >>> 0;
        h = g; g = f; f = e; e = (d + t1) >>> 0;
        d = c; c = b; b = a; a = (t1 + t2) >>> 0;
      }
      H[0] = (H[0] + a) >>> 0; H[1] = (H[1] + b) >>> 0; H[2] = (H[2] + c) >>> 0; H[3] = (H[3] + d) >>> 0;
      H[4] = (H[4] + e) >>> 0; H[5] = (H[5] + f) >>> 0; H[6] = (H[6] + g) >>> 0; H[7] = (H[7] + h) >>> 0;
    }
    var out = new Uint8Array(32), o = 0;
    for (i = 0; i < 8; i++) { out[o++] = (H[i] >>> 24) & 255; out[o++] = (H[i] >>> 16) & 255; out[o++] = (H[i] >>> 8) & 255; out[o++] = H[i] & 255; }
    return out;
  }

  function hmacBytes(key, msg) {
    var B = 64, k = key, i;
    if (k.length > B) k = sha256bytes(k);
    var kp = new Uint8Array(B); kp.set(k);
    var ip = new Uint8Array(B + msg.length), op = new Uint8Array(B + 32);
    for (i = 0; i < B; i++) { ip[i] = kp[i] ^ 0x36; op[i] = kp[i] ^ 0x5c; }
    ip.set(msg, B);
    var inner = sha256bytes(ip);
    op.set(inner, B);
    return sha256bytes(op);
  }

  function enc(s) { return new TextEncoder().encode(s); }

  function b32(bytes) {
    var bits = 0, val = 0, out = '', i;
    for (i = 0; i < bytes.length; i++) {
      val = (val << 8) | bytes[i]; bits += 8;
      while (bits >= 5) { out += B32[(val >>> (bits - 5)) & 31]; bits -= 5; }
    }
    if (bits > 0) out += B32[(val << (5 - bits)) & 31];
    return out;
  }

  function randHex(n) {
    var a = new Uint8Array(n);
    try { (window.crypto || window.msCrypto).getRandomValues(a); }
    catch (e) { for (var i = 0; i < n; i++) a[i] = Math.floor(Math.random() * 256); }
    return Array.prototype.map.call(a, function (x) { return ('0' + x.toString(16)).slice(-2); }).join('');
  }

  function db() { try { return window.localStorage; } catch (e) { return null; } }

  function deviceCode() {
    var s = db(), seed = s && s.getItem(LS_SEED);
    if (!seed) { seed = randHex(16); if (s) s.setItem(LS_SEED, seed); }
    var raw = b32(sha256bytes(enc(seed))).slice(0, 20);
    return raw.replace(/(.{4})/g, '$1-').replace(/-$/, '');
  }
  function expected(code) {
    var raw = b32(hmacBytes(enc(SECRET), enc(norm(code)))).slice(0, 20);
    return raw.replace(/(.{4})/g, '$1-').replace(/-$/, '');
  }
  function norm(s) { return (s || '').toUpperCase().replace(/[^A-Z2-7]/g, ''); }
  function verified() {
    try {
      var s = db(); if (!s) return false;
      var lic = JSON.parse(s.getItem(LS_LIC) || 'null');
      if (!lic || !lic.dc || !lic.code) return false;
      if (lic.dc !== deviceCode()) return false;
      return norm(lic.code) === norm(expected(lic.dc));
    } catch (e) { return false; }
  }

  var STYLE = '' +
    '.kygate{position:fixed;inset:0;z-index:99999;display:flex;align-items:center;justify-content:center;' +
    'padding:22px;background:radial-gradient(120% 80% at 50% 0%,#1b2033 0%,#0b0c12 60%);' +
    'font-family:-apple-system,"PingFang SC","MiSans","Microsoft YaHei",sans-serif;color:#eceef6;' +
    'padding-top:calc(22px + env(safe-area-inset-top,0px));padding-bottom:calc(22px + env(safe-area-inset-bottom,0px))}' +
    '.kygate *{box-sizing:border-box}' +
    '.kybox{width:100%;max-width:420px;background:linear-gradient(180deg,#161a2b,#12141f);' +
    'border:1px solid #2a2f47;border-radius:22px;padding:26px 22px 22px;box-shadow:0 24px 60px rgba(0,0,0,.5)}' +
    '.kyicon{width:56px;height:56px;border-radius:18px;margin:0 auto 14px;display:flex;align-items:center;' +
    'justify-content:center;background:linear-gradient(135deg,#ff7a59,#ff9d6b);box-shadow:0 8px 24px rgba(255,122,89,.35)}' +
    '.kytitle{text-align:center;font-size:19px;font-weight:700;letter-spacing:.5px}' +
    '.kysub{text-align:center;font-size:12.5px;color:#8b90a8;line-height:1.7;margin-top:8px}' +
    '.kystep{margin-top:18px;font-size:12px;color:#8b90a8;letter-spacing:.5px}' +
    '.kycode{margin-top:8px;display:flex;gap:8px;align-items:center}' +
    '.kycode code{flex:1;display:block;padding:13px 12px;border-radius:12px;background:#0e1018;' +
    'border:1px dashed #3a4160;color:#4fd1c5;font-size:15px;letter-spacing:1.5px;text-align:center;' +
    'font-family:ui-monospace,Menlo,Consolas,monospace;word-break:break-all}' +
    '.kycopy{flex:0 0 auto;padding:11px 14px;border-radius:12px;border:1px solid #2a2f47;background:#1d2135;' +
    'color:#eceef6;font-size:12.5px;font-family:inherit}' +
    '.kyinp{width:100%;margin-top:8px;padding:14px 12px;border-radius:12px;background:#0e1018;' +
    'border:1px solid #2a2f47;color:#eceef6;font-size:16px;letter-spacing:2px;text-align:center;' +
    'font-family:ui-monospace,Menlo,Consolas,monospace;outline:none}' +
    '.kyinp:focus{border-color:#4fd1c5}' +
    '.kybtn{width:100%;margin-top:14px;padding:14px;border:none;border-radius:13px;font-size:15px;' +
    'font-weight:700;color:#fff;font-family:inherit;background:linear-gradient(135deg,#ff7a59,#ff9d6b);' +
    'box-shadow:0 8px 22px rgba(255,122,89,.28)}' +
    '.kybtn:active{transform:scale(.99)}' +
    '.kyerr{margin-top:10px;font-size:12.5px;color:#f87171;text-align:center;min-height:16px}' +
    '.kyfoot{margin-top:16px;font-size:11px;color:#5f647d;text-align:center;line-height:1.7}' +
    '@keyframes kyout{to{opacity:0;transform:scale(1.02)}}' +
    '.kygate.out{animation:kyout .28s forwards}';

  function build() {
    if (!document.body) return;
    if (verified()) return;
    var st = document.createElement('style'); st.textContent = STYLE; document.head.appendChild(st);
    var g = document.createElement('div');
    g.className = 'kygate';
    g.innerHTML =
      '<div class="kybox">' +
        '<div class="kyicon"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6z"/><path d="M9 12l2 2 4-4"/></svg></div>' +
        '<div class="kytitle">授权验证</div>' +
        '<div class="kysub">本应用已绑定设备授权<br>首次使用需输入一次性验证码</div>' +
        '<div class="kystep">① 复制设备码</div>' +
        '<div class="kycode"><code id="kyDev"></code><button class="kycopy" id="kyCopy">复制</button></div>' +
        '<div class="kystep">② 输入激活码</div>' +
        '<input class="kyinp" id="kyInp" placeholder="XXXX-XXXX-XXXX-XXXX-XXXX" autocomplete="off" spellcheck="false">' +
        '<button class="kybtn" id="kyOk">验证并进入</button>' +
        '<div class="kyerr" id="kyErr"></div>' +
        '<div class="kyfoot">验证码与设备码绑定，仅本设备可用<br>验证通过后不再弹出</div>' +
      '</div>';
    document.body.appendChild(g);
    document.body.style.overflow = 'hidden';
    var dc = deviceCode();
    g.querySelector('#kyDev').textContent = dc;
    g.querySelector('#kyCopy').onclick = function () {
      var btn = this;
      function done() { btn.textContent = '已复制'; setTimeout(function () { btn.textContent = '复制'; }, 1500); }
      try {
        if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(dc).then(done); return; }
      } catch (e) {}
      var ta = document.createElement('textarea'); ta.value = dc; document.body.appendChild(ta);
      ta.select();
      try { document.execCommand('copy'); done(); } catch (e) { alert('请长按设备码手动复制'); }
      document.body.removeChild(ta);
    };
    var inp = g.querySelector('#kyInp'), err = g.querySelector('#kyErr');
    inp.addEventListener('input', function () {
      var v = inp.value.toUpperCase().replace(/[^A-Z2-7]/g, '');
      inp.value = v.replace(/(.{4})/g, '$1-').replace(/-$/, '');
    });
    function submit() {
      var v = inp.value;
      if (norm(v).length !== 20) { err.textContent = '激活码格式不正确'; return; }
      if (norm(v) === norm(expected(dc))) {
        try { db().setItem(LS_LIC, JSON.stringify({ dc: dc, code: v, ts: Date.now() })); } catch (e) {}
        g.classList.add('out');
        document.body.style.overflow = '';
        setTimeout(function () { if (g.parentNode) g.parentNode.removeChild(g); }, 300);
      } else {
        err.textContent = '激活码无效，请核对后重试';
      }
    }
    g.querySelector('#kyOk').onclick = submit;
    inp.addEventListener('keydown', function (e) { if (e.key === 'Enter') submit(); });
  }

  window.KaoYanAuth = { verified: verified, deviceCode: deviceCode };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', build);
  else build();
})();
