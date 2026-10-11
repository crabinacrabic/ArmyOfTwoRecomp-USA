#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Army of Two - DLC Asset Integrator for Unreal Engine 3
Copies extracted DLC assets into the game tree (CookedXenon, Checkpoints, Config)
and registers them in AO2Game/Xbox360TOC.txt.
"""

import os
import sys
import shutil
import hashlib

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def md5_file(filepath):
    h = hashlib.md5()
    with open(filepath, 'rb') as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest().lower()

def main():
    repo_root = r"C:\Recompiles\ArmyOfTwoRE2008"
    dlc_root = os.path.join(repo_root, "dlc")
    assets_root = os.path.join(repo_root, "assets", "AO2Game")

    cooked_dir = os.path.join(assets_root, "CookedXenon")
    checkpoints_dir = os.path.join(assets_root, "Checkpoints")
    config_dir = os.path.join(assets_root, "Config")
    loc_dir = os.path.join(assets_root, "Localization")
    toc_path = os.path.join(assets_root, "Xbox360TOC.txt")
    toc_backup = os.path.join(assets_root, "Xbox360TOC.txt.orig")

    print("=" * 70)
    print("  🚀 ARMY OF TWO: DLC ASSET INTEGRATION INTO UNREAL ENGINE 3")
    print("=" * 70)

    # 1. Backup TOC if not backed up yet
    if not os.path.exists(toc_backup):
        shutil.copyfile(toc_path, toc_backup)
        print(f"[+] Backup created: {toc_backup}")
    else:
        print(f"[*] Original TOC backup already exists: {toc_backup}")

    # Read existing TOC entries to avoid duplicates
    existing_entries = set()
    with open(toc_path, 'r', encoding='ascii', errors='ignore') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 4:
                existing_entries.add(parts[3].lower())

    new_toc_lines = []
    copied_packages = 0
    copied_checkpoints = 0
    copied_configs = 0

    # 2. Integrate Veteran Pack (Chapter 09 / Kiev)
    vet_pack = os.path.join(dlc_root, "veteran_pack")
    if os.path.exists(vet_pack):
        print("\n[*] Processing Veteran Map Pack...")
        for fname in os.listdir(vet_pack):
            src_file = os.path.join(vet_pack, fname)
            if not os.path.isfile(src_file):
                continue

            # Checkpoints (09_00 .. 09_100)
            if fname.startswith("09_") and not fname.endswith(".xxx"):
                dst_file = os.path.join(checkpoints_dir, fname)
                shutil.copy2(src_file, dst_file)
                copied_checkpoints += 1
                rel_path = f"..\\AO2Game\\Checkpoints\\{fname}"
                if rel_path.lower() not in existing_entries:
                    sz = os.path.getsize(dst_file)
                    h = md5_file(dst_file)
                    new_toc_lines.append(f"{sz} 0 0 {rel_path} {h}\n")
                    existing_entries.add(rel_path.lower())

            # Cooked Packages (.xxx)
            elif fname.endswith(".xxx"):
                dst_file = os.path.join(cooked_dir, fname)
                shutil.copy2(src_file, dst_file)
                copied_packages += 1
                rel_path = f"..\\AO2Game\\CookedXenon\\{fname}"
                if rel_path.lower() not in existing_entries:
                    sz = os.path.getsize(dst_file)
                    h = md5_file(dst_file)
                    new_toc_lines.append(f"{sz} 0 0 {rel_path} {h}\n")
                    existing_entries.add(rel_path.lower())

    # 3. Integrate SSC Challenge Pack
    ssc_pack = os.path.join(dlc_root, "ssc_challenge")
    if os.path.exists(ssc_pack):
        print("[*] Processing SSC Challenge Pack...")
        for fname in os.listdir(ssc_pack):
            src_file = os.path.join(ssc_pack, fname)
            if not os.path.isfile(src_file):
                continue

            if fname.endswith(".xxx"):
                dst_file = os.path.join(cooked_dir, fname)
                shutil.copy2(src_file, dst_file)
                copied_packages += 1
                rel_path = f"..\\AO2Game\\CookedXenon\\{fname}"
                if rel_path.lower() not in existing_entries:
                    sz = os.path.getsize(dst_file)
                    h = md5_file(dst_file)
                    new_toc_lines.append(f"{sz} 0 0 {rel_path} {h}\n")
                    existing_entries.add(rel_path.lower())

            elif fname.endswith(".ini"):
                dst_file = os.path.join(config_dir, fname)
                shutil.copy2(src_file, dst_file)
                copied_configs += 1
                rel_path = f"..\\AO2Game\\Config\\{fname}"
                if rel_path.lower() not in existing_entries:
                    sz = os.path.getsize(dst_file)
                    h = md5_file(dst_file)
                    new_toc_lines.append(f"{sz} 0 0 {rel_path} {h}\n")
                    existing_entries.add(rel_path.lower())

            elif fname.endswith(".int"):
                dst_file = os.path.join(loc_dir, fname)
                shutil.copy2(src_file, dst_file)
                copied_configs += 1
                rel_path = f"..\\AO2Game\\Localization\\{fname}"
                if rel_path.lower() not in existing_entries:
                    sz = os.path.getsize(dst_file)
                    h = md5_file(dst_file)
                    new_toc_lines.append(f"{sz} 0 0 {rel_path} {h}\n")
                    existing_entries.add(rel_path.lower())

    # 4. Append new lines to Xbox360TOC.txt
    if new_toc_lines:
        with open(toc_path, 'a', encoding='ascii') as f:
            f.writelines(new_toc_lines)
        print(f"\n[+] Added {len(new_toc_lines)} new entries to Xbox360TOC.txt")
    else:
        print("\n[*] All entries already present in TOC, nothing to append.")

    print(f"[+] Packages copied:    {copied_packages}")
    print(f"[+] Checkpoints copied: {copied_checkpoints}")
    print(f"[+] Configs/Text copied: {copied_configs}")
    print("=" * 70)
    print("  [OK] Интеграция ресурсов завершена успешно!")
    print("=" * 70)

if __name__ == "__main__":
    main()
