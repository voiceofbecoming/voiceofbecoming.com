const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");
const SITE = path.join(__dirname, "..", "site");
const pages = ["index.html","about.html","authority/index.html","newsletter.html"];
const redirects = ["blog.html","calendar.html","freebies.html","letter/index.html"];
const posts = fs.readdirSync(path.join(SITE,"blog")).filter(f=>f.endsWith(".html")).map(f=>"blog/"+f);
const all = pages.concat(posts);
const read = p => fs.readFileSync(path.join(SITE,p),"utf8");

test("all six pages and at least one article exist", () => {
  for (const p of pages) assert.ok(fs.existsSync(path.join(SITE,p)), p);
  assert.ok(posts.length >= 1);
});
test("each page has title, viewport, nav and full footer", () => {
  for (const p of all) {
    const h = read(p);
    assert.match(h, /<title>[^<]{5,}<\/title>/, p);
    assert.match(h, /name="viewport" content="width=device-width/, p);
    for (const s of ["instagram.com/thediaryoffathima","instagram.com/thevoiceofbecomingstudio","linkedin.com/in/fathimasamreen","youtube.com/@thevoiceofbecomingstudio","mailto:fathima@voiceofbecoming.com","The Voice of Becoming Studio. All rights reserved"]) assert.ok(h.includes(s), p+" missing "+s);
  }
});
test("local asset references resolve", () => {
  for (const p of all) {
    const h = read(p); const dir = path.dirname(path.join(SITE,p));
    for (const m of h.matchAll(/(?:src|href)="([^"#:]+?)"/g)) {
      const ref = m[1]; if (ref.startsWith("mailto")) continue;
      assert.ok(fs.existsSync(path.join(dir, ref.split("?")[0])), p+" -> "+ref);
    }
  }
  const css = fs.readFileSync(path.join(SITE,"assets/styles.css"),"utf8");
  for (const m of css.matchAll(/url\((fonts\/[^)]+)\)/g)) assert.ok(fs.existsSync(path.join(SITE,"assets",m[1])), m[1]);
});
test("copy rules: no prices, no em dashes, no placeholders, no named confidential client", () => {
  for (const p of all) {
    const h = read(p);
    const text = h.replace(/<script[\s\S]*?<\/script>/g,"").replace(/<[^>]+>/g," ");
    assert.ok(!/[\u2014]/.test(text), p+" has an em dash");
    assert.ok(!/(₹|€|INR|USD|\$(?!700\b)\s?\d|\bprice\b)/i.test(text), p+" mentions a price other than the $700 retainer");
    assert.ok(!/(lorem|ipsum|TODO|TBD|\[insert)/i.test(text), p+" has a placeholder");
    if (p === "index.html" || p === "authority/index.html") assert.ok(/Parvez Siraj/.test(h) && /parvez\.jpg/.test(h), p+" lacks Parvez name and photo");
    assert.ok(!/topmate\.io\/fathima_samreen\/(2368492)/.test(h), p+" links the old teardown");
    assert.ok(!/topmate\.io/.test(h), p+" links Topmate");
    assert.ok(!/clarity call/i.test(h), p+" offers a clarity call");
    assert.ok(!/memoir/i.test(text), p+" says memoir");
  }
});
test("core content", () => {
  const home = read("index.html");
  assert.ok(home.includes("Muslim women executives"));
  assert.ok(read("about.html").includes("SIWAA") && read("about.html").includes("What's Your Aukaath?"));
  for (const r of redirects) assert.ok(read(r).includes("location.replace"), r+" redirects");
  assert.ok(read("authority/index.html").includes("Visibility Retainer") && read("authority/index.html").includes("Complete Authority") && read("authority/index.html").includes("Why are you applying"));
  assert.ok(read("authority/index.html").includes("formsubmit.co/236e3bcab1127516384d8fdd66449ff6"));
  assert.ok(read("index.html").includes("Muslim women leaders: "));
});
