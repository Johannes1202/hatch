# Hatch — Setup Guide

A complete walkthrough from zero to Hatch opening on every new tab.

---

## Step 1 — Install Docker

If you don't have Docker installed:

- **Windows / Mac:** Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Linux:** Follow the [official install guide](https://docs.docker.com/engine/install/) for your distro, then install Docker Compose:
  ```bash
  sudo apt install docker-compose-plugin
  ```

Verify it works:
```bash
docker --version
docker compose version
```

---

## Step 2 — Get the Compose File

Create a folder for Hatch anywhere on your machine:

```bash
mkdir hatch && cd hatch
```

Create a file called `docker-compose.yml` and paste this into it:

```yaml
services:
  hatch:
    image: ghcr.io/johannes1202/hatch:latest
    restart: unless-stopped
    ports:
      - "7575:8000"        # change 7575 to your preferred port
    volumes:
      - hatch_data:/data
    environment:
      - HATCH_PASSWORD=changeme  # change this to a secure password

volumes:
  hatch_data:
```

---

## Step 3 — Configure It

Open `docker-compose.yml` in any text editor and make two changes:

1. **Set a password** — replace `changeme` with something you'll remember
2. **Set a port** — replace `7575` with any port you prefer (anything above 1024 that isn't already in use)

Save the file.

---

## Step 4 — Start Hatch

In the same folder, run:

```bash
docker compose up -d
```

Docker will pull the image and start the container. This only takes a minute.

Open your browser and go to:

```
http://localhost:7575
```

Replace `7575` with whatever port you chose. You should see the Hatch login page. Enter your password and you're in.

---

## Step 5 — Set Hatch as Your New Tab Page

### Google Chrome

Chrome doesn't support custom new tab pages natively, so you need a free extension.

1. Install [New Tab Redirect](https://chromewebstore.google.com/detail/new-tab-redirect/icpgjfneehieebagbmdbhnlpiopdcmna) from the Chrome Web Store
2. Click the extension icon in your toolbar
3. Set the URL to `http://localhost:7575`
4. Click **Save**

Open a new tab — Hatch should appear.

---

### Mozilla Firefox

Firefox also requires an extension.

1. Install [New Tab Override](https://addons.mozilla.org/en-US/firefox/addon/new-tab-override/) from Firefox Add-ons
2. After installing, the extension settings will open automatically
3. Set the URL to `http://localhost:7575`
4. Click **Save**

Open a new tab — Hatch should appear.

---

### Microsoft Edge

Edge has a built-in setting for this.

1. Open Edge and go to `edge://settings/newTabPage`
2. Under **Customize your new tab page**, select **Custom**
3. Enter `http://localhost:7575`
4. Open a new tab — Hatch should appear

---

## Accessing Hatch from Other Devices

If you want to access Hatch from your phone or another computer, you have two options:

**On your local network:**
Replace `localhost` with the IP address of the machine running Hatch:
```
http://192.168.1.100:7575
```

**From anywhere (Tailscale):**
If you use [Tailscale](https://tailscale.com), use your machine's Tailscale IP:
```
http://100.x.x.x:7575
```

**From anywhere (Cloudflare Tunnel):**
If you use [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/), point your tunnel at `localhost:7575` and access Hatch via your tunnel URL from any device, anywhere.

---

## Stopping and Starting Hatch

```bash
# Stop
docker compose down

# Start again
docker compose up -d

# View logs
docker compose logs -f
```

---

## Updating Hatch

```bash
docker compose pull
docker compose up -d
```

Your data (shortcuts, notes, settings) is stored in a Docker volume and will not be affected by updates.
