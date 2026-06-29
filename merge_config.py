#!/usr/bin/env python3
"""
Merge package selections from config.seed into OpenWrt .config.
Skips target/architecture options already set by the workflow.
"""
import re, os

# Determine paths - script runs from openwrt/ or repo root?
script_dir = os.path.dirname(os.path.abspath(__file__))  # repo root

# Read the config.seed from repo root
with open(os.path.join(script_dir, "config.seed")) as f:
    seed_lines = f.readlines()

# Read the current .config
config_path = os.path.join(script_dir, "openwrt/.config")
with open(config_path) as f:
    config_lines = f.readlines()

# Extract CONFIG_PACKAGE_* lines from config.seed
# (skip architecture/target/image options, those are set by the workflow)
package_lines = []
target_keys = {
    "CONFIG_TARGET_", "CONFIG_EXTERNAL_TOOLCHAIN", "CONFIG_GRUB_",
    "CONFIG_VMDK_", "CONFIG_VDI_", "CONFIG_VHDX_", "CONFIG_ISO_",
    "CONFIG_TARGET_ROOTFS_", "CONFIG_TARGET_IMAGES_", "CONFIG_TARGET_MULTI_",
    "CONFIG_TARGET_KERNEL_",
}

for line in seed_lines:
    line = line.strip()
    # Skip comments, empty lines, and target/image configs
    if not line or line.startswith("#"):
        continue
    if "is not set" in line:
        continue
    
    # Only take CONFIG_PACKAGE_* lines
    if line.startswith("CONFIG_PACKAGE_"):
        package_lines.append(line)
    # Also take other non-target configs
    elif line.startswith("CONFIG_") and not any(line.startswith(k) for k in target_keys):
        package_lines.append(line)

# Build a dict of existing config from .config
existing = {}
for line in config_lines:
    line = line.strip()
    if line.startswith("CONFIG_") and ("=y" in line or "=m" in line):
        key = line.split("=")[0]
        existing[key] = line

# Apply our selections (overwriting existing values)
added = 0
overwritten = 0
for line in package_lines:
    key = line.split("=")[0]
    if key in existing:
        if existing[key] != line:
            # Update in place
            overwritten += 1
    else:
        added += 1

# Write merged config
existing_set = set(existing.keys())
keys_seen = set()

with open(os.path.join(script_dir, "openwrt/.config"), "w") as f:
    for line in config_lines:
        stripped = line.strip()
        if stripped.startswith("CONFIG_") and ("=y" in line or "=m" in line or "=n" in line):
            key = stripped.split("=")[0]
            if key in keys_seen:
                continue  # Remove duplicates
            keys_seen.add(key)
        
        # Check if this line should be replaced
        skip = False
        for pl in package_lines:
            pk = pl.split("=")[0]
            if stripped.startswith(pk) and stripped != pl:
                skip = True
                break
        if skip:
            continue
        
        f.write(line)
    
    # Append new lines that don't exist yet
    f.write("\n# === Custom package selections ===\n")
    for line in package_lines:
        key = line.split("=")[0]
        if key not in existing_set or existing[key] != line:
            f.write(line + "\n")

print(f"Merged: {added} new, {overwritten} overwritten")
