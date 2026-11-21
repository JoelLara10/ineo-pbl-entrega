const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const path = require('node:path');
const test = require('node:test');
const pm = require('picomatch');
const utils = require('../../vendor/picomatch-guarded/lib/utils');

test('all toolchain consumers resolve to the guarded local parser', () => {
  const metadata = require('../../vendor/picomatch-guarded/package.json');
  assert.equal(metadata.name, '@ineo/picomatch-guarded');
  assert.equal(metadata.upstream, 'picomatch@4.0.7');
  for (const parent of ['vite', 'vitest', 'tinyglobby', 'fdir']) {
    const entry = require.resolve(parent);
    const resolved = require.resolve('picomatch', { paths: [path.dirname(entry)] });
    assert.match(resolved.replaceAll('\\', '/'), /vendor\/picomatch-guarded\/index\.js$/);
  }
});

test('linear backslash removal preserves bracket and escape semantics', () => {
  // Retained only as a bounded compatibility oracle; never match large inputs.
  const original = value => {
    if (value.length > 12) throw new RangeError('Compatibility oracle accepts short fixtures only');
    return value.replace(/(?:\[.*?[^\\]\]|\\(?=.))/g,
      match => match === '\\' ? '' : match);
  };
  const alphabet = ['[', ']', '\\', 'a', '\n', '\r', '\u2028', '\u2029'];
  function compare(value, depth) {
    assert.equal(utils.removeBackslashes(value), original(value), JSON.stringify(value));
    if (depth) for (const char of alphabet) compare(value + char, depth - 1);
  }
  compare('', 5);
});

test('unclosed brackets and escaped brackets complete within a bounded subprocess', () => {
  const source = `const u=require(${JSON.stringify(require.resolve('../../vendor/picomatch-guarded/lib/utils'))});
    for(const value of ['['.repeat(200000), '\\\\['.repeat(100000), '['.repeat(100000)+'a]']) {
      const started=performance.now(); u.removeBackslashes(value);
      if(performance.now()-started>1000) process.exit(2);
    }`;
  const result = spawnSync(process.execPath, ['-e', source], { timeout: 4000, encoding: 'utf8' });
  assert.equal(result.error, undefined);
  assert.equal(result.status, 0, result.stderr);
});

test('ordinary project globs and literal extglobs retain their behavior', () => {
  assert(pm.isMatch('src/pages/Login.jsx', '**/*.{js,jsx}'));
  assert(pm.isMatch('src/tests/a.test.jsx', '**/*.test.{js,jsx}'));
  assert(!pm.isMatch('src/file.css', '**/*.test.{js,jsx}'));
  assert(pm.isMatch('testtest', '+(test|spec)'));
});

for (const pattern of ['+(*)', '+(*a)', '*(*a)', '+(?*a)', '+(*?a)', '*(*|a)']) {
  test(`reject repeated wildcard extglob ${pattern} in a bounded subprocess`, () => {
    const code = `const pm=require(${JSON.stringify(require.resolve('picomatch'))});
      const pattern=${JSON.stringify(pattern)};
      const started=performance.now();
      for(let i=0;i<20;i++) {
        pm.isMatch('a'.repeat(5000)+'!',pattern);
        pm.isMatch('a'.repeat(5000)+'!',pattern,{maxExtglobRecursion:false});
      }
      if(performance.now()-started>1000) process.exit(2);
      if(pm.isMatch('aaaa',pattern)) process.exit(3);`;
    const result = spawnSync(process.execPath, ['-e', code], { timeout: 3000, encoding: 'utf8' });
    assert.equal(result.error, undefined);
    assert.equal(result.status, 0, result.stderr);
  });
}
