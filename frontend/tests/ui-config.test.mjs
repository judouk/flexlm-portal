import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import ts from 'typescript';

// Execute the actual TypeScript loader using the existing compiler dependency.
const source = await readFile(new URL('../src/uiConfig.ts', import.meta.url), 'utf8');
const { outputText } = ts.transpileModule(source, {
  compilerOptions: { target: ts.ScriptTarget.ES2023, module: ts.ModuleKind.ESNext },
});
const { loadUxVersion } = await import(`data:text/javascript;base64,${Buffer.from(outputText).toString('base64')}`);

test('loads deployment selection without cached configuration or authentication', async t => {
  for (const version of [1, 2]) {
    const mock = t.mock.method(globalThis, 'fetch', async (url, options) => {
      assert.equal(url, '/api/ui-config');
      assert.equal(options.cache, 'no-store');
      assert.ok(options.signal instanceof AbortSignal);
      assert.equal(options.headers, undefined);
      return Response.json({ ux_version: version });
    });
    assert.equal(await loadUxVersion('/api'), version);
    mock.mock.restore();
  }
});

test('supports an older backend by selecting the existing interface on 404', async t => {
  t.mock.method(globalThis, 'fetch', async () => new Response('', { status: 404 }));
  assert.equal(await loadUxVersion('/api'), 1);
});

test('configuration errors are surfaced for the retry screen', async t => {
  for (const config of [null, {}, { ux_version: true }, { ux_version: '2' }, { ux_version: 3 }]) {
    const mock = t.mock.method(globalThis, 'fetch', async () => Response.json(config));
    await assert.rejects(loadUxVersion('/api'), /Invalid portal/);
    mock.mock.restore();
  }
});

test('does not silently change interfaces on server or network failure', async t => {
  const mock = t.mock.method(globalThis, 'fetch', async () => new Response('', { status: 503 }));
  await assert.rejects(loadUxVersion('/api'), /Unable to load/);
  mock.mock.restore();
  t.mock.method(globalThis, 'fetch', async () => { throw new TypeError('offline'); });
  await assert.rejects(loadUxVersion('/api'), /offline/);
});
