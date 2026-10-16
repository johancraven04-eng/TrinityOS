# TrinityOS: build from an Android tablet

You do not need a Linux/Windows computer for the intended cloud-build workflow, and you do not need a Raspberry Pi Pico.

1. In your browser, sign in to GitHub and create a repository named `TrinityOS`.
2. Upload all files from this project folder. If using the web uploader, include hidden paths such as `.github/workflows/build-image.yml`.
3. Commit the upload to the `main` branch.
4. Open **Actions** and select **Build TrinityOS for Raspberry Pi 5**.
5. Tap **Run workflow** and confirm.
6. Wait for the job. If it fails, open the job logs and share the first red error section so we can fix the actual problem.
7. If successful, download the `TrinityOS-Pi5-image` artifact.

## What can be tested without Pi hardware?

- Edit and run the Kivy app in Pydroid 3, where compatible.
- Review the cloud build logs.
- Inspect the image's build artifacts and source configuration.

## What cannot be confirmed without a Raspberry Pi 5?

Actual boot, HDMI/display behavior, touchscreen/keyboard, sound, Wi-Fi, performance, and whether the desktop launches the app correctly. The first image is a preview until physically tested.
