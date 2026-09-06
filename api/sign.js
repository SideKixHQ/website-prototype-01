/* POST /api/sign
   The one piece a static site cannot do: keeping a signature.

   WHICH DATABASE
   Vercel KV no longer exists. Vercel retired it and moved existing stores to
   Upstash Redis on the Marketplace in December 2024, so this talks to Upstash
   over its REST API rather than importing @vercel/kv, which would not resolve
   on a new project.

   The Marketplace integration injects the credentials. Which names it uses
   depends on how the store was made, so both are accepted: a store migrated
   from Vercel KV keeps KV_REST_API_*, a new Upstash store gets
   UPSTASH_REDIS_REST_*.

   TO TURN IT ON
     1. Vercel dashboard, this project, Storage, Create Database, Upstash Redis
     2. Connect it to the project
     3. Redeploy

   No package to install: Upstash speaks a plain REST dialect, so this file
   works the moment the store exists and has nothing to keep up to date.

   Until then it is dormant. It answers 503 rather than 500, which reads as
   "signing is not open yet" rather than "broken", and the page still shows
   the names in signatures.json.

   ADDING A SIGNATURE AFTER A PURCHASE
   Call this from the payment webhook with the buyer name rather than from the
   browser, and it lands on the wall without them typing anything.

   WHAT IT STORES
   A name and a date. Nothing else, and no way back to a person beyond what
   they typed. Worth keeping it that way: a public wall of names is personal
   data, and the less of it there is the less there is to look after. */

const KEY = 'declaration:signatures';
const MAX_NAME = 60;

const URL_  = process.env.KV_REST_API_URL   || process.env.UPSTASH_REDIS_REST_URL;
const TOKEN = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;

const STRIP = new RegExp('[' + String.fromCharCode(0) + '-' + String.fromCharCode(31) + '<>]', 'g');

function clean(s, max) {
  return String(s || '').replace(STRIP, '').trim().slice(0, max);
}

async function redis(command) {
  const r = await fetch(URL_, {
    method: 'POST',
    headers: { Authorization: 'Bearer ' + TOKEN, 'Content-Type': 'application/json' },
    body: JSON.stringify(command)
  });
  if (!r.ok) throw new Error('upstash ' + r.status);
  const { result } = await r.json();
  return result;
}

async function read() {
  const raw = await redis(['GET', KEY]);
  if (!raw) return [];
  try {
    const v = typeof raw === 'string' ? JSON.parse(raw) : raw;
    return Array.isArray(v) ? v : [];
  } catch (e) {
    return [];
  }
}

export default async function handler(req, res) {
  if (!URL_ || !TOKEN) {
    return res.status(503).json({ error: 'Signing is not open yet' });
  }

  try {
    if (req.method === 'GET') {
      return res.status(200).json({ signatures: await read() });
    }
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'POST or GET' });
    }

    const name = clean(req.body && req.body.name, MAX_NAME);
    if (name.length < 2) {
      return res.status(400).json({ error: 'A name is needed' });
    }

    const signatures = await read();

    /* the same person signing twice does not need two entries */
    const already = signatures.some(
      s => s && s.name && s.name.toLowerCase() === name.toLowerCase()
    );
    if (!already) {
      signatures.push({ name, at: new Date().toISOString().slice(0, 10) });
      await redis(['SET', KEY, JSON.stringify(signatures)]);
    }

    return res.status(200).json({ signatures });
  } catch (err) {
    console.error('sign:', err);
    return res.status(503).json({ error: 'Signing is not open yet' });
  }
}
