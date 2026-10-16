#!/bin/bash -e
# pi-gen runs this script on the build host. ROOTFS_DIR is the target image root.
install -d "${ROOTFS_DIR}/opt/trinityos"
install -m 0644 "${STAGE_DIR}/01-install-trinity/files/TrinityOS.py" "${ROOTFS_DIR}/opt/trinityos/TrinityOS.py"
install -d "${ROOTFS_DIR}/home/trinity/.config/labwc"
cat > "${ROOTFS_DIR}/home/trinity/.config/labwc/autostart" <<'AUTOSTART'
#!/bin/sh
# Start the TrinityOS Kivy interface in the logged-in desktop session.
python3 /opt/trinityos/TrinityOS.py &
AUTOSTART
chmod 0755 "${ROOTFS_DIR}/home/trinity/.config/labwc/autostart"
if [ -x "${ROOTFS_DIR}/usr/sbin/chroot" ] && [ -e "${ROOTFS_DIR}/etc/passwd" ]; then
    chroot "${ROOTFS_DIR}" /bin/sh -c 'id trinity >/dev/null 2>&1 && chown -R trinity:trinity /home/trinity/.config || true'
fi
install -d "${ROOTFS_DIR}/opt/trinityos"
cat > "${ROOTFS_DIR}/opt/trinityos/BUILD-STATUS.txt" <<'STATUS'
TrinityOS Raspberry Pi 5 preview build.
This image has not been validated on Raspberry Pi 5 hardware.
The Kivy application and desktop autostart require first-boot testing.
crossGPT currently uses the functionality present in the included TrinityOS source.
STATUS
