'use strict';
var http = require('http');
var fs = require('fs');
var path = require('path');
var os = require('os');
var zlib = require('zlib');
var crypto = require('crypto');
var { DatabaseSync } = require('node:sqlite');

var ROOT = __dirname;
var DATA = path.join(ROOT, 'data');
var FILEDIR = path.join(DATA, 'files');
var PORT = Number(process.env.PORT) || 8787;
var START_PASSWORD = 'Skystone2026';
var MAX_FILE = 15 * 1024 * 1024;
var MAX_BODY = 48 * 1024 * 1024;

fs.mkdirSync(FILEDIR, { recursive: true });

function crc32(buf) {
  var c = ~0;
  for (var i = 0; i < buf.length; i++) {
    c ^= buf[i];
    for (var k = 0; k < 8; k++) c = (c >>> 1) ^ (0xedb88320 & -(c & 1));
  }
  return ~c >>> 0;
}
function pngChunk(type, data) {
  var len = Buffer.alloc(4);
  len.writeUInt32BE(data.length);
  var body = Buffer.concat([Buffer.from(type), data]);
  var crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(body));
  return Buffer.concat([len, body, crc]);
}
function solidPng(size, r, g, b) {
  var raw = Buffer.alloc((size * 4 + 1) * size);
  for (var y = 0; y < size; y++) {
    var o = y * (size * 4 + 1);
    raw[o] = 0;
    for (var x = 0; x < size; x++) {
      var p = o + 1 + x * 4;
      raw[p] = r; raw[p + 1] = g; raw[p + 2] = b; raw[p + 3] = 255;
    }
  }
  var ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(size, 0);
  ihdr.writeUInt32BE(size, 4);
  ihdr[8] = 8; ihdr[9] = 6;
  return Buffer.concat([
    Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]),
    pngChunk('IHDR', ihdr),
    pngChunk('IDAT', zlib.deflateSync(raw)),
    pngChunk('IEND', Buffer.alloc(0))
  ]);
}
[['icon-192.png', 192], ['icon-512.png', 512]].forEach(function (pair) {
  var dest = path.join(ROOT, pair[0]);
  if (!fs.existsSync(dest)) fs.writeFileSync(dest, solidPng(pair[1], 0xe2, 0x1e, 0x23));
});

var db = new DatabaseSync(path.join(DATA, 'people.db'));
db.exec('CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, name TEXT NOT NULL, role TEXT NOT NULL, emp_id TEXT NOT NULL, password_hash TEXT NOT NULL, password_salt TEXT NOT NULL)');
db.exec('CREATE TABLE IF NOT EXISTS sessions (token TEXT PRIMARY KEY, email TEXT NOT NULL, expires INTEGER NOT NULL)');
db.exec('CREATE TABLE IF NOT EXISTS company (id INTEGER PRIMARY KEY CHECK (id = 1), state TEXT NOT NULL, updated_at INTEGER NOT NULL)');

function hashPassword(password, salt) {
  salt = salt || crypto.randomBytes(16).toString('hex');
  return { salt: salt, hash: crypto.scryptSync(password, salt, 32).toString('hex') };
}
function passwordOk(password, salt, hash) {
  var got = crypto.scryptSync(String(password), salt, 32);
  var exp = Buffer.from(hash, 'hex');
  return got.length === exp.length && crypto.timingSafeEqual(got, exp);
}
function userCount() { return db.prepare('SELECT COUNT(*) AS n FROM users').get().n; }
function publicUser(row) { return { email: row.email, name: row.name, role: row.role, empId: row.emp_id }; }
function readCookie(req) {
  var raw = req.headers.cookie || '';
  var m = raw.match(/(?:^|;\s*)pos=([^;]+)/);
  return m ? decodeURIComponent(m[1]) : '';
}
function currentUser(req) {
  var token = readCookie(req);
  if (!token) return null;
  var row = db.prepare('SELECT s.email, u.name, u.role, u.emp_id, s.expires FROM sessions s JOIN users u ON u.email = s.email WHERE s.token = ?').get(token);
  if (!row || row.expires < Date.now()) {
    if (token) db.prepare('DELETE FROM sessions WHERE token = ?').run(token);
    return null;
  }
  return publicUser(row);
}
function send(res, code, obj, extra) {
  var body = JSON.stringify(obj);
  var headers = Object.assign({ 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', 'Content-Length': Buffer.byteLength(body) }, extra || {});
  res.writeHead(code, headers);
  res.end(body);
}
function readBody(req) {
  return new Promise(function (resolve, reject) {
    var chunks = [];
    var size = 0;
    req.on('data', function (c) {
      size += c.length;
      if (size > MAX_BODY) { reject(new Error('too-large')); req.destroy(); return; }
      chunks.push(c);
    });
    req.on('end', function () { resolve(Buffer.concat(chunks).toString('utf8')); });
    req.on('error', reject);
  });
}
function setSession(res, email) {
  var token = crypto.randomBytes(32).toString('hex');
  var expires = Date.now() + 14 * 24 * 60 * 60 * 1000;
  db.prepare('INSERT INTO sessions (token, email, expires) VALUES (?, ?, ?)').run(token, email, expires);
  return 'pos=' + token + '; HttpOnly; SameSite=Lax; Path=/; Max-Age=' + (14 * 24 * 60 * 60);
}
var STATIC = {
  '/': 'index.html',
  '/index.html': 'index.html',
  '/manifest.webmanifest': 'manifest.webmanifest',
  '/sw.js': 'sw.js',
  '/icon-192.png': 'icon-192.png',
  '/icon-512.png': 'icon-512.png'
};
var TYPES = { '.html': 'text/html; charset=utf-8', '.webmanifest': 'application/manifest+json', '.js': 'text/javascript; charset=utf-8', '.png': 'image/png' };

var fails = {};
function tooMany(ip) {
  var now = Date.now();
  var row = fails[ip] || { n: 0, at: now };
  if (now - row.at > 10 * 60 * 1000) row = { n: 0, at: now };
  fails[ip] = row;
  return row.n >= 12;
}
function noteFail(ip) {
  var row = fails[ip] || { n: 0, at: Date.now() };
  row.n++;
  fails[ip] = row;
}

var server = http.createServer(function (req, res) {
  var url = new URL(req.url, 'http://127.0.0.1');
  var pathname = decodeURIComponent(url.pathname);

  if (pathname.indexOf('/api/') === 0) {
    handleApi(req, res, pathname).catch(function (err) {
      if (err && err.message === 'too-large') send(res, 413, { ok: false, error: 'That upload is too large.' });
      else { console.error(err); send(res, 500, { ok: false, error: 'Something went wrong on the server.' }); }
    });
    return;
  }

  var file = STATIC[pathname];
  if (!file) { res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' }); res.end('Not found'); return; }
  var abs = path.join(ROOT, file);
  fs.readFile(abs, function (err, buf) {
    if (err) { res.writeHead(404); res.end('Not found'); return; }
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream', 'Cache-Control': file === 'sw.js' ? 'no-cache' : 'no-cache' });
    res.end(buf);
  });
});

async function handleApi(req, res, pathname) {
  if (req.method === 'GET' && pathname === '/api/session') {
    send(res, 200, { ok: true, ready: userCount() > 0, user: currentUser(req) });
    return;
  }
  if (req.method === 'POST' && pathname === '/api/bootstrap') {
    if (userCount() > 0) { send(res, 409, { ok: false, error: 'People OS is already set up.' }); return; }
    var boot = JSON.parse(await readBody(req));
    var accounts = Array.isArray(boot.accounts) ? boot.accounts : [];
    if (!accounts.length || !boot.state) { send(res, 400, { ok: false, error: 'The company record was not included.' }); return; }
    var pw = hashPassword(START_PASSWORD);
    db.exec('BEGIN IMMEDIATE');
    try {
      if (userCount() > 0) { db.exec('ROLLBACK'); send(res, 409, { ok: false, error: 'People OS is already set up.' }); return; }
      var ins = db.prepare('INSERT INTO users (email, name, role, emp_id, password_hash, password_salt) VALUES (?, ?, ?, ?, ?, ?)');
      accounts.forEach(function (a) {
        var email = String(a.email || '').trim().toLowerCase();
        if (!email || !a.role || !a.empId) return;
        ins.run(email, String(a.name || email), String(a.role), String(a.empId), pw.hash, pw.salt);
      });
      if (userCount() === 0) throw new Error('no accounts');
      delete boot.state.role; delete boot.state.signedIn;
      db.prepare('INSERT INTO company (id, state, updated_at) VALUES (1, ?, ?)').run(JSON.stringify(boot.state), Date.now());
      db.exec('COMMIT');
    } catch (e) {
      try { db.exec('ROLLBACK'); } catch (ignore) {}
      throw e;
    }
    send(res, 200, { ok: true });
    return;
  }
  if (req.method === 'POST' && pathname === '/api/login') {
    var ip = req.socket.remoteAddress || '';
    if (tooMany(ip)) { send(res, 429, { ok: false, error: 'Too many attempts. Wait a few minutes and try again.' }); return; }
    var body = JSON.parse(await readBody(req));
    var email = String(body.email || '').trim().toLowerCase();
    var row = db.prepare('SELECT * FROM users WHERE email = ?').get(email);
    if (!row || !passwordOk(body.password || '', row.password_salt, row.password_hash)) {
      noteFail(ip);
      send(res, 401, { ok: false, error: 'That email or password is not recognised.' });
      return;
    }
    var cookie = setSession(res, row.email);
    send(res, 200, { ok: true, user: publicUser(row) }, { 'Set-Cookie': cookie });
    return;
  }
  if (req.method === 'POST' && pathname === '/api/logout') {
    var token = readCookie(req);
    if (token) db.prepare('DELETE FROM sessions WHERE token = ?').run(token);
    send(res, 200, { ok: true }, { 'Set-Cookie': 'pos=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0' });
    return;
  }

  var user = currentUser(req);
  if (!user) { send(res, 401, { ok: false, error: 'Sign in again.' }); return; }

  if (req.method === 'GET' && pathname === '/api/state') {
    var company = db.prepare('SELECT state FROM company WHERE id = 1').get();
    send(res, 200, { ok: true, state: company ? JSON.parse(company.state) : null, user: user });
    return;
  }
  if (req.method === 'PUT' && pathname === '/api/state') {
    var next = JSON.parse(await readBody(req));
    delete next.role; delete next.signedIn;
    db.prepare('INSERT INTO company (id, state, updated_at) VALUES (1, ?, ?) ON CONFLICT(id) DO UPDATE SET state = excluded.state, updated_at = excluded.updated_at').run(JSON.stringify(next), Date.now());
    send(res, 200, { ok: true });
    return;
  }
  if (req.method === 'POST' && pathname === '/api/password') {
    var pwBody = JSON.parse(await readBody(req));
    var me = db.prepare('SELECT * FROM users WHERE email = ?').get(user.email);
    if (!passwordOk(pwBody.current || '', me.password_salt, me.password_hash)) { send(res, 400, { ok: false, error: 'The current password is not correct.' }); return; }
    if (!pwBody.next || String(pwBody.next).length < 8) { send(res, 400, { ok: false, error: 'Use at least 8 characters.' }); return; }
    var nextPw = hashPassword(pwBody.next);
    db.prepare('UPDATE users SET password_hash = ?, password_salt = ? WHERE email = ?').run(nextPw.hash, nextPw.salt, user.email);
    send(res, 200, { ok: true });
    return;
  }
  if (req.method === 'POST' && pathname === '/api/files') {
    var fileBody = JSON.parse(await readBody(req));
    var name = path.basename(String(fileBody.name || 'document'));
    var ext = (name.split('.').pop() || '').toLowerCase();
    if (['pdf', 'doc', 'docx', 'ppt', 'pptx'].indexOf(ext) < 0) { send(res, 400, { ok: false, error: 'Use a PowerPoint, PDF or Word file.' }); return; }
    if (user.role !== 'hr' && user.role !== 'hoh') { send(res, 403, { ok: false, error: 'Only HR can upload a learning document.' }); return; }
    var dataUrl = String(fileBody.data || '');
    var comma = dataUrl.indexOf(',');
    if (comma < 0) { send(res, 400, { ok: false, error: 'The file could not be read.' }); return; }
    var bytes = Buffer.from(dataUrl.slice(comma + 1), 'base64');
    if (bytes.length > MAX_FILE) { send(res, 413, { ok: false, error: 'That file is over 15 MB. Choose a smaller file.' }); return; }
    var id = crypto.randomBytes(12).toString('hex');
    fs.writeFileSync(path.join(FILEDIR, id), bytes);
    db.exec('CREATE TABLE IF NOT EXISTS files (id TEXT PRIMARY KEY, name TEXT NOT NULL, ext TEXT NOT NULL, size INTEGER NOT NULL, by_email TEXT NOT NULL)');
    db.prepare('INSERT INTO files (id, name, ext, size, by_email) VALUES (?, ?, ?, ?, ?)').run(id, name, ext, bytes.length, user.email);
    send(res, 200, { ok: true, url: '/api/files/' + id, size: bytes.length });
    return;
  }
  var fileMatch = pathname.match(/^\/api\/files\/([a-f0-9]{24})$/);
  if (req.method === 'GET' && fileMatch) {
    db.exec('CREATE TABLE IF NOT EXISTS files (id TEXT PRIMARY KEY, name TEXT NOT NULL, ext TEXT NOT NULL, size INTEGER NOT NULL, by_email TEXT NOT NULL)');
    var meta = db.prepare('SELECT * FROM files WHERE id = ?').get(fileMatch[1]);
    var disk = path.join(FILEDIR, fileMatch[1]);
    if (!meta || !fs.existsSync(disk)) { send(res, 404, { ok: false, error: 'That document is no longer available.' }); return; }
    var mime = { pdf: 'application/pdf', doc: 'application/msword', docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', ppt: 'application/vnd.ms-powerpoint', pptx: 'application/vnd.openxmlformats-officedocument.presentationml.presentation' }[meta.ext] || 'application/octet-stream';
    res.writeHead(200, {
      'Content-Type': mime,
      'Content-Length': meta.size,
      'Content-Disposition': 'attachment; filename="' + meta.name.replace(/"/g, '') + '"',
      'Cache-Control': 'private, no-store'
    });
    fs.createReadStream(disk).pipe(res);
    return;
  }
  send(res, 404, { ok: false, error: 'Not found.' });
}

server.listen(PORT, '0.0.0.0', function () {
  var ips = [];
  var nets = os.networkInterfaces();
  Object.keys(nets).forEach(function (name) {
    nets[name].forEach(function (n) { if (n.family === 'IPv4' && !n.internal) ips.push(n.address); });
  });
  console.log('People OS is running at http://127.0.0.1:' + PORT);
  ips.forEach(function (ip) { console.log('On this network: http://' + ip + ':' + PORT); });
});
