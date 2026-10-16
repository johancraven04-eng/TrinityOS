# TrinityOS for Raspberry Pi 5

**A cloud-built Raspberry Pi OS-based prototype for TrinityOS.** This project can be edited from an Android tablet; GitHub Actions performs the Linux image build.

## What's included

- `app/TrinityOS.py`: the existing Kivy OS-style app, renamed from DropletOS to TrinityOS.
- The built-in assistant has been renamed to **crossGPT**.
- `stage-trinity/`: a custom `pi-gen` stage that installs the app and sets up a desktop-session autostart entry.
- `.github/workflows/build-image.yml`: a manually triggered GitHub Actions cloud build.

## Build from an Android tablet

1. Create a GitHub repository named `TrinityOS`.
2. Upload the contents of this folder to the repository's `main` branch. Make sure the `.github/workflows/build-image.yml` file is included.
3. Open the repository's **Actions** tab.
4. Select **Build TrinityOS for Raspberry Pi 5**.
5. Choose **Run workflow**.
6. If the run succeeds, open the run and download the artifact named `TrinityOS-Pi5-image`.

## Important status note

This is a **build starter, not a tested release**. A successful cloud build does not prove that it boots or that the display, touch, audio, networking, and all apps work on a physical Raspberry Pi 5. Since no Pi 5 is available for testing yet, label any resulting image as a preview. The workflow itself may need maintenance if the upstream build action or Raspberry Pi OS build dependencies change.

No Raspberry Pi Pico is required. Do not add passwords or API keys to this repository.
