// The page a shared SideKix post opens to: /p/:id (vercel.json rewrite).
// Server-rendered so link previews (iMessage, Slack, social) get the post's
// own title, text and picture. Reads Admin-Backend's public
// GET posts/:id/preview — username, first 200 characters, first picture,
// poll totals only — and shows "This post is no longer available" when that
// 404s. Decided 2026-10-15: a preview page plus a join prompt.
const API = process.env.SIDEKIX_API_BASE || 'https://api.sidekixhq.com';
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

const escape = (value) =>
  String(value ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);

const safeImage = (url) => {
  try {
    const parsed = new URL(url);
    return parsed.protocol === 'https:' ? parsed.toString() : null;
  } catch {
    return null;
  }
};

async function fetchPreview(id) {
  const res = await fetch(`${API}/posts/${id}/preview`, {
    headers: { 'x-device-agent': 'web', Accept: 'application/json' },
  });
  if (res.status === 404 || res.status === 400) return null;
  if (!res.ok) throw new Error(`preview ${res.status}`);
  const body = await res.json();
  return body && body.data && body.data.id ? body.data : body;
}

function page({ title, description, image, body, status }) {
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1" name="viewport"/>
<title>${escape(title)}</title>
<meta content="noindex, follow" name="robots"/>
<meta property="og:site_name" content="SideKix"/>
<meta property="og:title" content="${escape(title)}"/>
<meta property="og:description" content="${escape(description)}"/>
${image ? `<meta property="og:image" content="${escape(image)}"/>\n<meta name="twitter:card" content="summary_large_image"/>` : '<meta name="twitter:card" content="summary"/>'}
<link href="/assets/fonts.css" rel="stylesheet"/>
<style>
:root{--ink:#060502;--gold:#D4A856;--gold-mid:#A1853E;--grey:#9B958B;--line:#1E1C18;--cream:#FFEBB9;
  --display:'Cormorant Garamond',Georgia,serif;--body:'Poppins',system-ui,sans-serif;--util:'Space Grotesk',ui-monospace,monospace}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{background:var(--ink);color:var(--grey);font-family:var(--body);font-size:16px;line-height:1.6;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:32px}
.card{max-width:460px;width:100%;background:#0f0d09;border:1px solid var(--line);border-radius:14px;padding:32px 28px}
.eyebrow{font-family:var(--util);font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:var(--gold-mid)}
.author{color:var(--cream);font-weight:500;margin:10px 0 8px}
.excerpt{color:#e6e1d6;font-size:15px;line-height:1.65;white-space:pre-wrap;word-wrap:break-word}
.media{margin-top:16px;width:100%;border-radius:12px;display:block;max-height:360px;object-fit:cover}
.poll{margin-top:14px;padding:12px 14px;border-radius:10px;border:1px solid rgba(212,168,86,.25);font-size:13.5px;color:var(--grey)}
h1{font-family:var(--display);font-weight:600;color:var(--cream);font-size:26px;margin:10px 0 10px;line-height:1.15}
.cta{display:block;margin-top:22px;padding:13px 18px;border-radius:999px;background:var(--gold);color:var(--ink);text-align:center;font-weight:600;text-decoration:none}
.cta.secondary{margin-top:10px;background:transparent;color:var(--gold);border:1px solid rgba(212,168,86,.45)}
.join{margin-top:20px;font-size:13.5px;text-align:center}
</style>
</head>
<body>
<main class="card"${status === 404 ? ' aria-labelledby="gone"' : ''}>
${body}
</main>
</body>
</html>`;
}

module.exports = async (req, res) => {
  const id = String((req.query && req.query.id) || '').replace(/\/+$/, '');
  if (!UUID_RE.test(id)) {
    res.status(404).setHeader('Content-Type', 'text/html; charset=utf-8');
    res.send(gone());
    return;
  }

  let preview;
  try {
    preview = await fetchPreview(id);
  } catch {
    res.status(502).setHeader('Content-Type', 'text/html; charset=utf-8');
    res.send(page({
      title: 'SideKix',
      description: 'Something went wrong loading this post.',
      body: '<p class="eyebrow">SideKix Community</p><h1>We couldn’t load this post</h1><p>Please try again in a moment.</p><a class="cta" href="/get-app.html">Get the SideKix app</a>',
    }));
    return;
  }

  if (!preview) {
    res.status(404).setHeader('Content-Type', 'text/html; charset=utf-8');
    res.send(gone());
    return;
  }

  const who = preview.username ? `@${preview.username}` : 'A SideKix member';
  const excerpt = `${preview.excerpt || ''}${preview.truncated ? '…' : ''}`;
  const image = preview.imageUrl ? safeImage(preview.imageUrl) : null;
  const pollLine = preview.poll
    ? `<div class="poll">Poll · ${preview.poll.optionCount} options · ${preview.poll.totalVotes} ${preview.poll.totalVotes === 1 ? 'vote' : 'votes'}${preview.poll.isClosed ? ' · ended' : ''}</div>`
    : '';
  const title = preview.type === 'poll' ? `${who} asked on SideKix` : `${who} on SideKix`;

  res.status(200);
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.setHeader('Cache-Control', 'public, max-age=60, s-maxage=300');
  res.send(page({
    title,
    description: excerpt.slice(0, 200) || 'See this post in the SideKix Community.',
    image,
    body: `<p class="eyebrow">SideKix Community</p>
<p class="author">${escape(who)}</p>
<p class="excerpt">${escape(excerpt)}</p>
${image ? `<img class="media" src="${escape(image)}" alt="" loading="lazy"/>` : ''}
${pollLine}
<a class="cta" href="sidekix://community/post/${escape(id)}">Open in SideKix</a>
<a class="cta secondary" href="/get-app.html">Get the app</a>
<p class="join">Join SideKix to read the whole conversation${preview.type === 'poll' ? ' and vote' : ''}.</p>`,
  }));
};

function gone() {
  return page({
    title: 'This post is no longer available · SideKix',
    description: 'This post is no longer available.',
    status: 404,
    body: '<p class="eyebrow">SideKix Community</p><h1 id="gone">This post is no longer available</h1><p>It may have been removed by its author or by our team.</p><a class="cta" href="/get-app.html">Get the SideKix app</a>',
  });
}

module.exports.escape = escape;
