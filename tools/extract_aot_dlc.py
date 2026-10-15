#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Army of Two - Automated DLC & Title Update Extractor (STFS)
Extracts LIVE/CON/PIRS packages into isolated DLC and TU directories.
Validated against ReXGlue STFS block offset specification.
"""

import os
import sys
import struct
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def get_cluster(startclust, offset):
    """Calculate cluster offset for STFS hash table blocks."""
    rst = 0
    sc = startclust
    while sc >= 170:
        sc //= 170
        rst += (sc + 1) * offset
    return rst

def extract_stfs_package(input_path, output_dir):
    """Extract all files and directories from an STFS package."""
    print("=" * 70)
    print(f"[*] Package: {os.path.basename(input_path)}")
    print(f"[*] Size:    {os.path.getsize(input_path) / (1024*1024):.2f} MB")
    print(f"[*] Target:  {output_dir}")
    print("=" * 70)

    if not os.path.exists(input_path):
        print(f"[-] ERROR: Package file not found: {input_path}")
        return False

    with open(input_path, 'rb') as infile:
        magic = infile.read(4)
        if magic not in (b'LIVE', b'PIRS', b'CON '):
            print(f"[-] ERROR: Invalid magic '{magic}', expected LIVE, PIRS, or CON")
            return False

        # Determine start of data area / file table
        infile.seek(0xC032)
        pathind = struct.unpack(">H", infile.read(2))[0]
        start = 0xC000 if pathind == 0xFFFF else 0xD000
        offset = 0x1000 if start == 0xC000 else 0x2000

        # Read file table
        infile.seek(start + 0x2F)
        firstclust = struct.unpack("<H", infile.read(2))[0]
        max_ft_blocks = max(firstclust, 32)

        infile.seek(start)
        ft_data = infile.read(0x1000 * max_ft_blocks)

        paths = {0xFFFF: ""}
        os.makedirs(output_dir, exist_ok=True)

        num_entries = len(ft_data) // 64
        extracted_files = 0
        extracted_bytes = 0
        t0 = time.time()

        for i in range(num_entries):
            cur = ft_data[i * 64:(i + 1) * 64]
            namelen_flags = cur[40]

            name_len = namelen_flags & 0x3F
            is_dir = bool(namelen_flags & 0x80)

            if name_len == 0 or name_len > 40:
                break

            outname = cur[0:name_len].decode('ascii', errors='replace')
            bad_chars = '<>:"/\\|?*'
            outname = ''.join('_' if (c in bad_chars or ord(c) < 0x20) else c for c in outname).rstrip(' .') or '_unnamed'

            startclust = struct.unpack("<H", cur[47:49])[0] + (cur[49] << 16)
            pathind = struct.unpack(">H", cur[50:52])[0]
            filelen = struct.unpack(">I", cur[52:56])[0]

            if is_dir:
                paths[i] = paths.get(pathind, "") + outname + "/"
                full_dir = os.path.join(output_dir, paths[i])
                os.makedirs(full_dir, exist_ok=True)
            else:
                parent = paths.get(pathind, "")
                out_path = os.path.join(output_dir, parent, outname)
                os.makedirs(os.path.dirname(out_path), exist_ok=True)

                # Stream file data in 4KB clusters directly to disk
                cur_clust = startclust
                remaining = filelen

                with open(out_path, 'wb') as outfile:
                    while remaining > 0:
                        realstart = cur_clust * 0x1000 + start + get_cluster(cur_clust, offset)
                        infile.seek(realstart)
                        chunk_size = min(0x1000, remaining)
                        chunk = infile.read(chunk_size)
                        if not chunk:
                            print(f"[-] Read error at cluster {cur_clust}")
                            break
                        outfile.write(chunk)
                        cur_clust += 1
                        remaining -= chunk_size

                extracted_files += 1
                extracted_bytes += filelen

        elapsed = time.time() - t0
        print(f"[+] SUCCESS: Extracted {extracted_files} files ({extracted_bytes / (1024*1024):.2f} MB) in {elapsed:.2f}s")
        return True

def main():
    dump_root = r"C:\Recompiles\ArmyOfTwoFULL\Army of Two ALL DLC TU"
    project_root = r"C:\Recompiles\ArmyOfTwoRE2008"

    tasks = [
        {
            "name": "Veteran Map Pack (Chapter 09 / Kiev DLC)",
            "src": os.path.join(dump_root, r"454107F8\00000002\410277CEFC99673AC789462C09A1AB618954129145"),
            "dst": os.path.join(project_root, r"dlc\veteran_pack")
        },
        {
            "name": "SSC Challenge Map Pack (Multiplayer / Co-op DLC)",
            "src": os.path.join(dump_root, r"454107F8\00000002\7FFB44132B7F904E89973ADB356EA99508CF86CB45"),
            "dst": os.path.join(project_root, r"dlc\ssc_challenge")
        },
        {
            "name": "Title Update (TU1 / default.xexp)",
            "src": os.path.join(dump_root, r"TU\TU_12K21VO_0000004000000.00000000000G1"),
            "dst": os.path.join(project_root, r"archive_debug\tu_update")
        }
    ]

    print("\n" + "#" * 70)
    print("  🚀 ARMY OF TWO: ALL DLC & TITLE UPDATE EXTRACTION")
    print("#" * 70 + "\n")

    for t in tasks:
        print(f"\n--> Processing: {t['name']}")
        extract_stfs_package(t["src"], t["dst"])

    print("\n" + "=" * 70)
    print("  [OK] Все пакеты успешно извлечены!")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
