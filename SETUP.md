# Hatch — Setup Guide

A complete walkthrough from zero to Hatch opening on every new tab. No experience required.

---

## Step 1 — Install Docker

Docker is the tool that runs Hatch. Think of it as a lightweight box that contains everything Hatch needs to run, without installing anything directly on your computer.

- **Windows / Mac:** Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/). Once installed, open it and leave it running in the background.
- **Linux:** Follow the [official install guide](https://docs.docker.com/engine/install/) for your distro. Then run:
  ```bash
  sudo apt install docker-compose-plugin
  ```

To confirm it's working, open a terminal and run:
```bash
docker --version
docker compose version
```
Both should print a version number. If they do, you're good to go.

> **How to open a terminal:**
> - **Windows:** Press `Win + R`, type `cmd`, press Enter. Or search for "Command Prompt" or "PowerShell" in the Start menu.
> - **Mac:** Press `Cmd + Space`, type `Terminal`, press Enter.
> - **Linux:** `Ctrl + Alt + T` on most distros.

---

## Step 2 — Download Hatch

Run these commands in your terminal to download Hatch and move into its folder:

```bash
git clone https://github.com/Johannes1202/hatch.git
cd hatch
```

> If you don't have `git` installed: [download it here](https://git-scm.com/downloads). On Windows, use the installer. On Mac, it will prompt you to install it automatically. On Linux: `sudo apt install git`.

---

## Step 3 — Set Your Password

Open the `docker-compose.yml` file in a text editor and find this line:

```
- HATCH_PASSWORD=changeme
```

Replace `changeme` with a password you'll remember. Save the file.

> **Windows tip:** Don't use Notepad — it may add `.txt` to the filename without telling you. Use [Notepad++](https://notepad-plus-plus.org/) or [VS Code](https://code.visualstudio.com/) instead.

That's the only thing you need to change. Leave the port as `7575` unless you have a specific reason to change it.

---

## Step 4 — Start Hatch

In your terminal, make sure you're inside the `hatch` folder, then run:

```bash
docker compose up -d --build
```

Docker will build and start Hatch. This takes a minute or two the first time. The `-d` flag means it runs in the background — you can close the terminal and Hatch will keep running.

When it's done, open your browser and go to:

```
http://localhost:7575
```

You should see the Hatch login page. Enter your password and you're in.

> **Something went wrong?** Run `docker compose logs` to see what happened.

---

## Step 5 — Set Hatch as Your New Tab Page

### Google Chrome

Chrome doesn't support custom new tab pages natively, so you need a free extension.

1. Install [New Tab Redirect](https://chromewebstore.google.com/detail/new-tab-redirect/icpgjfneehieebagbmdbhnlpiopdcmna) from the Chrome Web Store
2. Click the extension icon in your toolbar (puzzle piece icon → New Tab Redirect)
3. Set the URL to `http://localhost:7575`
4. Click **Save**

Open a new tab — Hatch should appear.

---

### Mozilla Firefox

1. Install [New Tab Override](https://addons.mozilla.org/en-US/firefox/addon/new-tab-override/) from Firefox Add-ons
2. After installing, the extension settings will open automatically
3. Set the URL to `http://localhost:7575`
4. Click **Save**

Open a new tab — Hatch should appear.

---

### Microsoft Edge

Edge has this built in — no extension needed.

1. Go to `edge://settings/newTabPage` in your address bar
2. Under **Customize your new tab page**, select **Custom**
3. Enter `http://localhost:7575`

Open a new tab — Hatch should appear.

---

## Accessing Hatch from Other Devices

Hatch runs on one machine, but you can reach it from other devices on the same network.

**Find the IP address of the machine running Hatch:**
- **Windows:** Open Command Prompt and run `ipconfig`. Look for **IPv4 Address** — something like `192.168.1.100`.
- **Mac:** System Settings → Network → select your connection → IP address.
- **Linux:** Run `ip addr` and look for `inet` followed by an address like `192.168.1.100`.

Then on any other device on your network, open a browser and go to:
```
http://192.168.1.100:7575
```
Replace `192.168.1.100` with the IP you found.

---

**Accessing from anywhere — Tailscale:**

[Tailscale](https://tailscale.com) creates a private network between your devices. Install it on both machines, then use your Tailscale IP instead of the local IP:
```
http://100.x.x.x:7575
```

---

**Accessing from anywhere — Cloudflare Tunnel:**

[Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) lets you reach Hatch via a public URL without opening ports on your router. Point your tunnel at the IP of the machine running Hatch:
```
http://192.168.1.100:7575
```
If `cloudflared` is running on the same machine as Hatch, you can use `localhost:7575` instead.

> Hatch is optimised for desktop browsers. It works on mobile but the experience is best on a larger screen.

---

## Stopping and Starting Hatch

```bash
# Stop Hatch
docker compose down

# Start Hatch again
docker compose up -d

# Check if it's running
docker compose ps

# View logs if something goes wrong
docker compose logs
```

---

## Updating Hatch

```bash
git pull
docker compose up -d --build
```

Your data — shortcuts, notes, and settings — is stored separately and will not be affected by updates.
