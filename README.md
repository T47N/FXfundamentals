# Forex Fundamentals — daily companion app

A small offline Android app version of the daily fundamentals + technicals
playbook: a morning checklist with a streak counter, a tappable per-currency
bias scorecard (bullish / neutral / bearish), a freeform notes journal, and
a quick-reference guide tab. Everything is stored locally on your device —
no internet connection or account needed.

## A quick note on compiling

I can't compile the actual `.apk` file for you directly in this chat — building
for Android requires downloading the Android SDK/NDK from Google's servers,
which this sandbox doesn't have network access to. But I've done everything
else: the app is written, tested (verified the UI builds and the logic runs
correctly), and packaged with a config that builds itself automatically.
You have two ways to turn it into an installable APK — pick whichever is
easier for you.

---

## Option A — Build in the cloud with GitHub Actions (recommended, no setup on your end)

This is the easiest path since it needs no Linux machine, no SDK install —
GitHub's servers do the work for free.

1. Create a free GitHub account if you don't have one, and create a new
   **public or private repository** (e.g. `forex-fundamentals-app`).
2. Upload all the files in this folder to that repository, keeping the
   folder structure exactly as-is (including the hidden `.github/workflows/build.yml`
   file — make sure your upload method doesn't skip dotfiles).
3. Once pushed, go to the **Actions** tab of your repo. A workflow called
   "Build Android APK" will start automatically (it also runs on any future
   push, or you can trigger it manually with "Run workflow").
4. Wait for it to finish — the first build downloads the Android toolchain,
   so it typically takes 15–25 minutes. Later builds are faster.
5. When it's green, click into the completed run and download the
   **forex-fundamentals-apk** artifact — it's a zip containing your `.apk` file.

## Option B — Build locally with Buildozer (Linux or WSL2 only — buildozer does not run on Windows or macOS directly, and not on the phone itself)

1. On a Linux machine or Windows Subsystem for Linux (WSL2):
   ```
   sudo apt update && sudo apt install -y python3-pip build-essential git \
       ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
       libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev
   pip3 install --user buildozer cython
   ```
2. From inside this project folder, run:
   ```
   buildozer -v android debug
   ```
3. The first run downloads the Android SDK/NDK automatically (can take a
   while) and produces the APK in `bin/forexfundamentals-1.0-arm64-v8a_armeabi-v7a-debug.apk`.

---

## Installing the APK on your Galaxy S22 Ultra

1. Transfer the `.apk` file to your phone (email it to yourself, use a USB
   cable, or upload to Google Drive/Samsung Cloud and download it on-device).
2. Tap the file on your phone. If it's your first time installing an app
   outside the Play Store, Android will prompt you to allow installs from
   that source (Settings → Apps → Special access → Install unknown apps →
   enable it for whichever app you used, e.g. Chrome or Files).
3. Tap **Install**. Once done, open "Forex Fundamentals" from your app drawer.

## Testing the app on your computer first (optional but recommended)

Before compiling, you can run it directly on a desktop with Python installed,
to confirm the behavior you want before packaging:
```
pip install kivy
python main.py
```
This opens the same app in a desktop window — same checklist, bias tracker,
and notes tab you'll get on the phone.

## Files in this project

- `main.py` — the full app source code
- `buildozer.spec` — Android build configuration (app name, permissions, etc.)
- `.github/workflows/build.yml` — the automated cloud-build workflow
- `README.md` — this file
