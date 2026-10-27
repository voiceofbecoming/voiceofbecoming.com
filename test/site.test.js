const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");
const SITE = path.join(__dirname, "..", "site");
const pages = ["index.html","about.html","blog.html","calendar.html","freebies.html","newsletter.html"];
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
    for (const s of ["instagram.com/thediaryoffathima","instagram.com/thevoiceofbecomingstudio","linkedin.com/in/fathimasamreen","youtube.com/@thevoiceofbecomingstudio","topmate.io/fathima_samreen","mailto:fathima@voiceofbecoming.com","becoming-her-again-4.kit.com/042d6cefac","The Voice of Becoming Studio. All rights reserved"]) assert.ok(h.includes(s), p+" missing "+s);
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
    assert.ok(!/(₹|\$\s?\d|€|INR|USD|\bprice\b)/i.test(text), p+" mentions a price");
    assert.ok(!/(lorem|ipsum|TODO|TBD|\[insert)/i.test(text), p+" has a placeholder");
    assert.ok(!/(Bhavna|Shenomics)/i.test(h), p+" names a confidential client");
    assert.ok(!/memoir/i.test(text), p+" says memoir");
  }
});
test("core content", () => {
  const home = read("index.html");
  assert.ok(home.includes("Muslim women executives"));
  assert.ok(read("about.html").includes("SIWAA") && read("about.html").includes("Executive Presence") && read("about.html").includes("What's Your Aukaath?"));
  assert.ok(read("calendar.html").includes("Upcoming talks will be announced here"));
  assert.ok(read("freebies.html").includes("Articulation"));
});
