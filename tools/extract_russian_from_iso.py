import os
import struct
import hashlib
import shutil

GDFX_OFFSET = 0xFD90000
SECTOR_SIZE = 2048

iso_path = r"C:\Recompiles\ArmyOfTwoFULL\RUS\[X360] Army of Two [PAL-RUS]\Army.of.Two.RUS.PAL.iso"
repo_root = r"C:\Recompiles\ArmyOfTwoRE2008"
assets_dir = os.path.join(repo_root, "assets", "AO2Game")

files_to_extract = [
    {
        "sector": 1442897,
        "size": 1277952,
        "md5": "bead22def2f339acac8ff3c98cb64708",
        "dst": os.path.join(assets_dir, "CookedXenon", "00_fonts.xxx"),
        "toc_entry": r"..\AO2Game\CookedXenon\00_fonts.xxx"
    },
    {
        "sector": 1661292,
        "size": 294912,
        "md5": "d03c8ca1d9430f370ad9129dcb0c27ef",
        "dst": os.path.join(assets_dir, "CookedXenon", "EngineFonts.xxx"),
        "toc_entry": r"..\AO2Game\CookedXenon\EngineFonts.xxx"
    },
    {
        "sector": 1775010,
        "size": 710995,
        "md5": "622b45b4a8152db15086a1a04e5b1f17",
        "dst": os.path.join(assets_dir, "Localization", "Coalesced.int"),
        "toc_entry": r"..\AO2Game\Localization\Coalesced.int"
    }
]

print("Extracting authentic Russian Xbox 360 files from ISO...")
with open(iso_path, "rb") as f:
    for item in files_to_extract:
        f.seek(GDFX_OFFSET + item["sector"] * SECTOR_SIZE)
        data = f.read(item["size"])
        actual_md5 = hashlib.md5(data).hexdigest()
        assert actual_md5 == item["md5"], f"MD5 mismatch for {item['dst']}: expected {item['md5']}, got {actual_md5}"
        
        with open(item["dst"], "wb") as out_fp:
            out_fp.write(data)
        print(f"Extracted: {os.path.basename(item['dst'])} ({len(data)} bytes, MD5: {actual_md5})")

# Update Xbox360TOC.txt
toc_path = os.path.join(assets_dir, "Xbox360TOC.txt")
with open(toc_path, "r", encoding="utf-8", errors="ignore") as fp:
    toc_lines = fp.readlines()

updates_map = {item["toc_entry"]: (item["size"], item["md5"]) for item in files_to_extract}
new_toc_lines = []
updated = 0
for line in toc_lines:
    parts = line.strip().split()
    if len(parts) >= 5:
        p = parts[3]
        if p in updates_map:
            sz, md5 = updates_map[p]
            new_line = f"{sz} {parts[1]} {parts[2]} {p} {md5}\n"
            new_toc_lines.append(new_line)
            updated += 1
            print(f"TOC update: {p} -> {new_line.strip()}")
            continue
    new_toc_lines.append(line)

with open(toc_path, "w", encoding="utf-8") as fp:
    fp.writelines(new_toc_lines)

print(f"Updated {updated} TOC entries successfully!")
