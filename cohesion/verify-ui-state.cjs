'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '..');
const sources = Object.fromEntries(['ui', 'app', 'study'].map(name => [name, fs.readFileSync(path.join(root, 'soldershape/web', name + '.js'), 'utf8')]));
const key = name => 'soldershape.ui.v1.' + name;
const footprint = { name: 'Boundary-test pad', sha256: 'a'.repeat(64), pads: [{ index: 0, identifier: 'A1', supported: true, shape: 'circle', size_mm: [.2, .2], x_mm: 0, y_mm: 0, angle_deg: 0 }] };
const parameters = { upper_diameter_mm: .2, volume_mm3: .0053, offset_mm: .12, surface_tension_n_m: .48, density_g_cm3: 9, standoff_mm: .15, gravity: false };
const newCase = { schema: 'soldershape.case.v1', footprint_text: 'replacement source bytes', pad_index: 0, parameters, baseline: null };
const jointDraft = text => ({ fields: Object.fromEntries(Object.entries({ ...parameters, normal_load_uN: 4, load_mode: 'gap' }).filter(([name]) => name !== 'gravity').map(([name, value]) => [name, String(value)])), footprintText: text, padIndex: 0, gravity: false, baseline: null, origin: null });
const studyDraft = () => ({ fields: { upper_diameter_mm: '0.2', volume_mm3: '0.0053', normal_load_uN: '4', offset_mm: '0.12', surface_tension_n_m: '0.48', density_g_cm3: '9' }, sources: { reference: { text: 'reference source bytes', padIndex: 0 }, candidate: { text: 'candidate source bytes', padIndex: 0 } }, gravity: false, twoPad: false });
function deferred() { let resolve, reject; const promise = new Promise((yes, no) => { resolve = yes; reject = no; }); return { promise, resolve, reject }; }
async function settle() { for (let n = 0; n < 4; n++) await new Promise(resolve => setImmediate(resolve)); }

function runtime(page = 'app', options = {}) {
  const nodes = new Map(), selectors = new Map(), store = new Map(), navigations = [], requests = [];
  const context2d = new Proxy({}, { get: (_target, name) => name === 'measureText' ? () => ({ width: 0 }) : () => {} });
  class Element {
    constructor(tag = 'div') { this.tagName = tag.toUpperCase(); this.children = []; this.events = new Map(); this.hidden = false; this.inert = false; this.disabled = false; this.value = ''; this.checked = false; this.dataset = {}; this.classList = { add() {}, remove() {}, toggle() {} }; }
    set id(value) { this._id = value; nodes.set(value, this); }
    get id() { return this._id; }
    get valueAsNumber() { return this.value === '' ? NaN : Number(this.value); }
    get validity() { return { valid: true }; }
    get lastElementChild() { return this.children.at(-1); }
    setAttribute(name, value) { this[name] = value; }
    append(...children) { this.children.push(...children); for (const child of children) if (child && typeof child === 'object') child.parent = this; }
    prepend(...children) { this.children.unshift(...children); for (const child of children) if (child && typeof child === 'object') child.parent = this; }
    replaceChildren(...children) { this.children = []; this.append(...children); }
    replaceWith(node) { if (this.parent) { const i = this.parent.children.indexOf(this); this.parent.children.splice(i, 1, node); node.parent = this.parent; } }
    remove() { if (this.parent) this.parent.children = this.parent.children.filter(child => child !== this); if (this.id) nodes.delete(this.id); }
    after(node) { this.parent.append(node); }
    addEventListener(name, handler) { if (!this.events.has(name)) this.events.set(name, []); this.events.get(name).push(handler); }
    async emit(name, event = {}) { for (const handler of this.events.get(name) || []) await handler({ preventDefault() {}, target: this, currentTarget: this, ...event }); }
    querySelector(selector) { if (!this.queries) this.queries = new Map(); if (!this.queries.has(selector)) this.queries.set(selector, new Element()); return this.queries.get(selector); }
    querySelectorAll() { return []; }
    reportValidity() { return true; }
    checkValidity() { return true; }
    getBoundingClientRect() { return { width: 300, height: 200, top: 0, left: 0 }; }
    getContext() { return context2d; }
    scrollIntoView() {}
    click() {}
  }
  const body = new Element('body'), main = new Element('main'); body.append(main);
  selectors.set('main', main);
  for (const selector of ['.setup-column', '.case-bar', '.file-bar']) { const node = new Element(); selectors.set(selector, node); main.append(node); }
  const html = fs.readFileSync(path.join(root, 'soldershape/web', page === 'app' ? 'index.html' : 'study.html'), 'utf8');
  for (const match of html.matchAll(/\bid="([^"]+)"/g)) { const node = new Element(); node.id = match[1]; main.append(node); }
  const document = { body, getElementById: id => nodes.get(id) || null, createElement: tag => new Element(tag), createTextNode: text => ({ textContent: text }), querySelector: selector => selector === 'body > header' ? null : selectors.get(selector) || (selector === '.workspace-purpose' ? main.children.find(child => child.className === 'workspace-purpose') : null) };
  const storage = {
    getItem(name) { if (options.unavailable) throw new Error('SecurityError'); return store.get(name) || null; },
    removeItem(name) { if (options.unavailable) throw new Error('SecurityError'); store.delete(name); },
    setItem(name, value) { if (options.unavailable) throw new Error('SecurityError'); const size = [...store].reduce((sum, [other, data]) => sum + (other === name ? 0 : Buffer.byteLength(data)), Buffer.byteLength(value)); if (size > (options.quota || Infinity)) throw new Error('QuotaExceededError'); store.set(name, value); },
  };
  let respond = async (url, body) => url === '/api/bootstrap' ? { token: 'test-token', engine: { ready: true, version: 'boundary-test' }, example: {} } : url === '/api/import' ? { footprint } : url === '/api/case' ? { case: body, footprint } : Promise.reject(new Error('Unexpected endpoint ' + url));
  const window = { addEventListener() {}, devicePixelRatio: 1 };
  const context = vm.createContext({ document, window, sessionStorage: storage, TextEncoder, URLSearchParams, Blob, URL, console, atob, setTimeout, clearTimeout, ResizeObserver: class { observe() {} }, requestAnimationFrame() {}, location: { pathname: page === 'app' ? '/' : '/study', search: '', assign: url => navigations.push(url), reload() {} }, history: { replaceState() {} }, fetch: async (url, init) => { const body = init?.body ? JSON.parse(init.body) : undefined; requests.push({ url, body }); const data = await respond(url, body); return { ok: true, json: async () => data }; } });
  vm.runInContext(sources.ui, context, { filename: 'ui.js' });
  context.SolderShapeUI = window.SolderShapeUI;
  return { nodes, selectors, store, requests, navigations, ui: window.SolderShapeUI, context, eval: code => vm.runInContext(code, context), respond: fn => { respond = fn; }, run: () => vm.runInContext(sources[page], context, { filename: page + '.js' }), locked: () => page === 'app' ? selectors.get('.setup-column').inert && selectors.get('.case-bar').inert : nodes.get('study-form').inert && selectors.get('.file-bar').inert };
}

const checks = [];
async function check(name, run) { try { await run(); checks.push({ name, status: 'pass' }); } catch (error) { checks.push({ name, status: 'fail', error: error.stack }); } }
async function quotaOffer() {
  const h = runtime('app', { quota: 5 * 1024 * 1024 });
  assert.equal(h.ui.saveDraft('joint', jointDraft('j'.repeat(2_000_000))), true);
  assert.equal(h.ui.saveDraft('study', { text: 's'.repeat(1_500_000) }), true);
  h.run(); await settle();
  const before = h.store.get(key('joint'));
  const file = h.nodes.get('case-file'); file.files = [{ size: 1000, text: async () => JSON.stringify(newCase) }];
  await file.emit('change');
  assert.equal(h.store.get(key('joint')), before);
  assert.equal(h.store.has(key('joint-backup')), false);
  assert.equal(h.eval('state.footprintText.length'), 2_000_000);
  assert.equal(h.nodes.get('replace-draft-button').hidden, false);
  assert.equal(h.nodes.get('replacement-note').hidden, false);
  assert.equal(h.locked(), false);
  return h;
}

(async () => {
  await check('normalized handoff round trip and single-use consumption', async () => {
    const h = runtime();
    await h.ui.openCase(newCase, { label: 'Board pad', href: '/board' }, 'test-token');
    assert.deepEqual(h.navigations, ['/?open=case']);
    h.context.location.search = '?open=case';
    const received = await h.ui.receiveCase('test-token');
    assert.equal(received.case.footprint_text, 'replacement source bytes');
    assert.equal(received.origin.href, '/board');
    h.ui.consumeCase();
    assert.equal(h.store.has(key('case')), false);
    await assert.rejects(() => h.ui.receiveCase('test-token'), /missing or expired/);
  });
  await check('late edit rejects handoff before storage or navigation', async () => {
    const h = runtime(), reply = deferred(); let current = true;
    h.respond(() => reply.promise);
    const opening = h.ui.openCase(newCase, { label: 'Board pad', href: '/board' }, 'test-token', () => current);
    current = false; reply.resolve({ case: newCase, footprint });
    await assert.rejects(() => opening, /Inputs changed while opening/);
    assert.equal(h.store.has(key('case')), false); assert.equal(h.navigations.length, 0);
  });
  await check('bounded draft failure preserves old bytes', async () => {
    const h = runtime(); h.ui.saveDraft('joint', jointDraft('keep these bytes'));
    const before = h.store.get(key('joint'));
    assert.equal(h.ui.saveDraft('joint', jointDraft('x'.repeat(4_600_001))), false);
    assert.equal(h.store.get(key('joint')), before);
    assert.match(h.nodes.get('workspace-notice').textContent, /storage is unavailable or full/);
  });
  await check('quota failure offers explicit replacement without altering prior work', async () => {
    const h = await quotaOffer();
    await h.nodes.get('replace-draft-button').emit('click');
    assert.equal(h.eval('state.footprintText'), 'replacement source bytes');
    assert.equal(h.ui.readDraft('joint').inputs.footprintText, 'replacement source bytes');
    assert.equal(h.eval('state.pendingReplacement'), null);
    assert.equal(h.eval('state.response'), null);
    assert.equal(h.nodes.get('replace-draft-button').hidden, true);
    assert.equal(h.locked(), false);
  });
  await check('linked quota replacement consumes the transfer only after explicit acceptance', async () => {
    const h = runtime('app', { quota: 5 * 1024 * 1024 });
    h.ui.saveDraft('joint', jointDraft('j'.repeat(2_000_000)));
    h.ui.saveDraft('study', { text: 's'.repeat(1_500_000) });
    await h.ui.openCase(newCase, { label: 'Board pad', href: '/board' }, 'test-token');
    h.context.location.search = '?open=case'; h.run(); await settle();
    assert.equal(h.eval('state.footprintText.length'), 2_000_000);
    assert.equal(h.nodes.get('replace-draft-button').hidden, false);
    assert.equal(h.store.has(key('case')), true);
    await h.nodes.get('replace-draft-button').emit('click');
    assert.equal(h.eval('state.footprintText'), 'replacement source bytes');
    assert.equal(h.eval('state.origin.href'), '/board');
    assert.equal(h.store.has(key('case')), false);
    assert.equal(h.locked(), false);
  });
  await check('failed explicit replacement preserves the old draft and permits retry', async () => {
    const h = await quotaOffer(), before = h.store.get(key('joint'));
    h.respond(() => Promise.reject(new Error('Injected case-check failure')));
    await h.nodes.get('replace-draft-button').emit('click');
    assert.equal(h.store.get(key('joint')), before);
    assert.equal(h.eval('state.footprintText.length'), 2_000_000);
    assert.equal(h.nodes.get('replace-draft-button').hidden, false);
    assert.equal(h.eval('state.caseAction'), null);
    assert.equal(h.locked(), false);
    assert.match(h.nodes.get('notice').textContent, /Injected case-check failure/);
  });
  await check('editing clears the pending replacement and rejects its late response', async () => {
    const h = await quotaOffer(), reply = deferred();
    h.respond(() => reply.promise);
    const replacing = h.nodes.get('replace-draft-button').emit('click');
    assert.equal(h.locked(), true);
    h.nodes.get('volume_mm3').value = '.0054'; await h.nodes.get('volume_mm3').emit('input');
    reply.resolve({ case: newCase, footprint }); await replacing;
    assert.equal(h.eval('state.footprintText.length'), 2_000_000);
    assert.equal(h.eval('state.pendingReplacement'), null);
    assert.equal(h.nodes.get('replace-draft-button').hidden, true);
    assert.equal(h.locked(), false);
  });
  await check('unavailable storage blocks handoff but permits portable file opening', async () => {
    const h = runtime('app', { unavailable: true });
    assert.equal(h.ui.saveDraft('joint', jointDraft('unsaved')), false);
    assert.equal(h.ui.readDraft('joint'), null);
    await assert.rejects(() => h.ui.openCase(newCase, { label: 'Board', href: '/board' }, 'test-token'), /Could not transfer/);
    assert.equal(h.navigations.length, 0);
    h.run(); await settle();
    const file = h.nodes.get('case-file'); file.files = [{ size: 1000, text: async () => JSON.stringify(newCase) }]; await file.emit('change');
    assert.equal(h.eval('state.footprintText'), 'replacement source bytes');
    assert.equal(h.locked(), false);
    assert.match(h.nodes.get('workspace-notice').textContent, /storage is unavailable or full/);
  });
  for (const page of ['app', 'study']) {
    for (const fail of [false, true]) {
      await check(`${page} startup locks while restoring and unlocks after ${fail ? 'failed' : 'successful'} import`, async () => {
        const h = runtime(page), reply = deferred(), name = page === 'app' ? 'joint' : 'study';
        const saved = page === 'app' ? jointDraft('saved source bytes') : studyDraft();
        h.ui.saveDraft(name, saved); const before = h.store.get(key(name));
        h.respond(url => url === '/api/bootstrap' ? { token: 'test-token', engine: { ready: true, version: 'boundary-test' }, example: {} } : reply.promise);
        h.run(); assert.equal(h.locked(), true); await settle();
        assert.equal(h.locked(), true); assert.equal(h.store.get(key(name)), before);
        if (fail) reply.reject(new Error('Injected source-import failure')); else reply.resolve({ footprint });
        await settle(); assert.equal(h.locked(), false);
        assert.equal(h.eval('state.response'), null);
        if (fail) {
          assert.equal(h.store.get(key(name)), before);
          assert.equal(h.nodes.get(page === 'app' ? 'case-file' : 'study-file').disabled, false);
          assert.match(h.nodes.get('notice').textContent, /Injected source-import failure/);
          assert.doesNotMatch(h.nodes.get('engine-label').textContent, /unavailable/);
        } else {
          assert.equal(h.eval(page === 'app' ? 'state.footprintText' : 'state.reference.text'), page === 'app' ? 'saved source bytes' : 'reference source bytes');
          assert.equal(h.nodes.get('volume_mm3').value, '0.0053');
        }
        if (page === 'study') assert.equal(h.eval('state.phase'), 'idle');
      });
    }
    await check(`${page} startup releases lock after bootstrap failure`, async () => {
      const h = runtime(page), reply = deferred(); h.respond(() => reply.promise); h.run(); assert.equal(h.locked(), true);
      reply.reject(new Error('Injected bootstrap failure')); await settle();
      assert.equal(h.locked(), false); assert.match(h.nodes.get('notice').textContent, /Injected bootstrap failure/);
      assert.equal(h.eval('state.token'), null);
      if (page === 'study') assert.equal(h.eval('state.phase'), 'idle');
    });
  }
  const report = { scope: 'Node VM boundary checks against actual UI scripts with mocked DOM, fetch and browser storage. These are not browser interaction, rendering, native computation or physical-validation proof.', command: 'node cohesion/verify-ui-state.cjs', source_sha256: Object.fromEntries(Object.entries(sources).map(([name, source]) => ['soldershape/web/' + name + '.js', crypto.createHash('sha256').update(source).digest('hex')])), passed: checks.filter(result => result.status === 'pass').length, failed: checks.filter(result => result.status === 'fail').length, checks };
  const outputPath = process.argv[2] ? path.resolve(root, process.argv[2]) : path.join(__dirname, 'state-checks.json');
  fs.writeFileSync(outputPath, JSON.stringify(report, null, 2) + '\n');
  console.log(`${report.passed}/${checks.length} UI boundary checks passed. Mocked runtime only. Results in ${path.relative(root, outputPath)}.`);
  for (const result of checks.filter(result => result.status === 'fail')) console.error(result.name + '\n' + result.error);
  process.exitCode = report.failed ? 1 : 0;
})();
