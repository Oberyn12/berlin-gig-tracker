# 🎵 Berlin Gig Tracker

A personal app that surfaces events from your favourite Berlin music venues and delivers a weekly Sunday digest to your Android phone.

**No subscription. No server to manage. All free, forever.**

---

## How it works

1. Every **Sunday at 8am** a bot automatically scrapes your 11 Berlin venues
2. It saves the events to this repository (GitHub Pages serves them for free)
3. You get a **push notification** on your Pixel with the week's event count
4. Tap the notification → open the app → buy tickets

---

## Your venues

| Venue | Type |
|---|---|
| A-trane | Jazz |
| B-Flat | Jazz |
| ZigZag | Jazz |
| Sowieso | Jazz / Experimental |
| Donau115 | Bar |
| Paloma Bar | Electronic |
| Gretchen | Electronic |
| Schokoladen | Live / DIY |
| Neue Zukunft | Live |
| Festsaal Kreuzberg | Live Concerts |
| Huxley Neue Welt | Live Concerts |

---

## One-time setup (5 steps)

### Step 1 — Create a GitHub account

Go to **[github.com/signup](https://github.com/signup)** and create a free account.

---

### Step 2 — Fork this repository

1. Click the **"Use this template"** button at the top of this page (or **Fork** if you cloned it)
2. Name it `berlin-gig-tracker`
3. Make sure it's **Public** (GitHub Pages is free for public repos)
4. Click **"Create repository"**

---

### Step 3 — Enable GitHub Actions + GitHub Pages

In your forked repo:

**Enable Actions:**
- Go to **Settings → Actions → General**
- Select **"Allow all actions and reusable workflows"**
- Click **Save**

**Enable Pages:**
- Go to **Settings → Pages**
- Under "Source" select **"Deploy from a branch"**
- Branch: `main`, folder: `/web`
- Click **Save**
- Wait ~1 minute, then your app will be live at:  
  `https://YOUR-USERNAME.github.io/berlin-gig-tracker/`

**Save your Pages URL:**
- Go to **Settings → Variables → Actions**
- Click **"New repository variable"**
- Name: `PAGES_URL`
- Value: `https://YOUR-USERNAME.github.io/berlin-gig-tracker/`
- Click **Add variable**

---

### Step 4 — Set up push notifications (ntfy)

**On your Pixel:**
1. Install the **[ntfy](https://play.google.com/store/apps/details?id=io.heckel.ntfy)** app (free, ~4MB, open source)
2. Open ntfy → tap **"+"** → Subscribe to topic
3. Enter a topic name — make it **unique and hard to guess**, e.g.:  
   `berlin-gigs-cesare-7291`  
   (anyone who knows your topic can send you notifications, so don't use something obvious)
4. Tap **Subscribe**

**Back on GitHub:**
- Go to **Settings → Secrets → Actions**
- Click **"New repository secret"**
- Name: `NTFY_TOPIC`
- Value: your topic name (e.g. `berlin-gigs-cesare-7291`)
- Click **Add secret**

---

### Step 5 — Add the app to your home screen

1. Open **Chrome** on your Pixel
2. Go to: `https://YOUR-USERNAME.github.io/berlin-gig-tracker/`
3. Tap the **⋮ menu** → **"Add to Home screen"**
4. Tap **Add**

The app now appears on your home screen like a native app. Dark mode, no browser chrome.

---

## Trigger your first scrape now

Don't wait until Sunday — run it manually:

1. Go to your repo → **Actions** tab
2. Click **"Scrape Berlin Events"** in the left sidebar
3. Click **"Run workflow"** → **"Run workflow"** (green button)
4. Wait ~2 minutes
5. Check the app — events should now appear!

---

## What about Donau115 and Huxley Neue Welt?

- **Donau115** — their website loads content via JavaScript, which the bot can't read automatically. Until we find their hidden API, this venue won't appear in the app.
- **Huxley Neue Welt** — their site blocks automated requests. The bot tries Resident Advisor (RA) as a fallback, so major shows may still appear.

Both venues are logged as warnings in the Actions run, but they don't break anything.

---

## Troubleshooting

**No events showing in the app?**
→ Go to Actions and check the latest run for red ✗ errors. Most common cause: a venue changed their website layout.

**Notification not arriving?**
→ Check that `NTFY_TOPIC` is set in Secrets and matches the topic in your ntfy app exactly. Also make sure ntfy has notification permission on your Pixel (Settings → Apps → ntfy → Notifications).

**The scrape ran but events.json is empty?**
→ All scrapers failed. Open the Actions run log to see which venues errored.

---

## Files

```
.github/workflows/scrape.yml   — weekly automation (DO NOT EDIT unless you know YAML)
scraper/                        — Python scraper for each venue
web/index.html                  — the app you see on your phone
web/events.json                 — updated every Sunday automatically
```

---

## Discover more venues

The app includes a **Discover** tab with venues that match your taste:

- **Quasimodo** (Charlottenburg) — legendary jazz club, peer to A-trane
- **Yorckschlösschen** (Kreuzberg) — neighbourhood jazz pub, live music most nights
- **Acud Macht Neu** (Mitte) — experimental music, film, arts
- **Urban Spree** (Friedrichshain) — eclectic: indie, punk, electronic
- **Traumabar und Kino** (Mitte) — tiny bar, cinema, adventurous music

---

## License

MIT — do whatever you want with it.
