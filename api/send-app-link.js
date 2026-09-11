// "Text me the app link" / "Email me the app link" on the checkout success
// screen — proxies to Admin-Backend's internal endpoint so the internal key
// never reaches the browser. See checkout.html's co-applink block and
// Admin-Backend's WebsiteCreditsService.sendAppLink.
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PHONE_RE = /^\+[1-9]\d{7,14}$/;

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const { email, channel, phone } = req.body || {};

  if (typeof email !== 'string' || !EMAIL_RE.test(email.trim())) {
    res.status(400).json({ error: 'A valid email is required' });
    return;
  }
  if (channel !== 'sms' && channel !== 'email') {
    res.status(400).json({ error: 'channel must be sms or email' });
    return;
  }
  if (channel === 'sms' && (typeof phone !== 'string' || !PHONE_RE.test(phone.trim()))) {
    res.status(400).json({ error: 'A valid phone number is required, e.g. +15551234567' });
    return;
  }

  try {
    const backendRes = await fetch(
      'https://api.sidekixhq.com/internal/website-credits/send-app-link',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-internal-key': process.env.WEBSITE_INTERNAL_KEY || '',
          'x-device-agent': 'web',
        },
        body: JSON.stringify({
          email: email.trim(),
          channel,
          phone: channel === 'sms' ? phone.trim() : undefined,
        }),
      },
    );

    if (!backendRes.ok) {
      const body = await backendRes.json().catch(() => ({}));
      if (backendRes.status === 404) {
        res.status(404).json({ error: "We couldn't find a purchase for that email yet." });
        return;
      }
      console.error('SideKix [send-app-link] Admin-Backend responded', backendRes.status, body);
      res.status(502).json({ error: "Couldn't send that. Try again." });
      return;
    }

    res.status(200).json({ sent: true });
  } catch (err) {
    console.error('SideKix [send-app-link] failed:', err);
    res.status(500).json({ error: "Couldn't send that. Try again." });
  }
};
