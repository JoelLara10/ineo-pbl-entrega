const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const path = require('node:path');
const test = require('node:test');
const pm = require('picomatch');

test('all toolchain consumers resolve to the guarded local parser', () => {
  for (const parent of ['vite', 'vitest', 'tinyglobby', 'fdir']) {
    const entry = require.resolve(parent);
    const resolved = require.resolve('picomatch', { paths: [path.dirname(entry)] });
    assert.match(resolved.replaceAll('\\', '/'), /vendor\/picomatch-guarded\/index\.js$/);
  }
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
