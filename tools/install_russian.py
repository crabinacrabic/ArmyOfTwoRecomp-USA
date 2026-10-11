"""
Army of Two (2008) - Russian Localization Installer (RUSBOX / Golden Ant)
Installs Russian fonts and subtitles, updates Xbox360TOC.txt.
"""

import os
import shutil
import hashlib

def calculate_md5(filepath):
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    assets_dir = os.path.join(repo_root, "assets", "AO2Game")
    rus_source_dir = r"C:\Recompiles\Ao2_NikolayGorb\translation\russian_ps3"
    
    files_to_install = [
        {
            "src": os.path.join(rus_source_dir, "Coalesced.int"),
            "dst": os.path.join(assets_dir, "Localization", "Coalesced.int"),
            "toc_path": r"..\AO2Game\Localization\Coalesced.int"
        },
        {
            "src": os.path.join(rus_source_dir, "00_fonts.xxx"),
            "dst": os.path.join(assets_dir, "CookedXenon", "00_fonts.xxx"),
            "toc_path": r"..\AO2Game\CookedXenon\00_fonts.xxx"
        },
        {
            "src": os.path.join(rus_source_dir, "EngineFonts.xxx"),
            "dst": os.path.join(assets_dir, "CookedXenon", "EngineFonts.xxx"),
            "toc_path": r"..\AO2Game\CookedXenon\EngineFonts.xxx"
        }
    ]
    
    # 1. Backup and copy
    updates_map = {}
    for item in files_to_install:
        src = item["src"]
        dst = item["dst"]
        bak = dst + ".eng_bak"
        
        if not os.path.exists(src):
            raise FileNotFoundError(f"Source file not found: {src}")
            
        if not os.path.exists(bak) and os.path.exists(dst):
            print(f"Creating backup: {dst} -> {bak}")
            shutil.copy2(dst, bak)
            
        print(f"Installing {os.path.basename(src)} -> {dst}")
        shutil.copy2(src, dst)
        
        size = os.path.getsize(dst)
        md5 = calculate_md5(dst)
        updates_map[item["toc_path"]] = (size, md5)
        print(f"  Size: {size} bytes, MD5: {md5}")
        
    # 2. Update Xbox360TOC.txt
    toc_path = os.path.join(assets_dir, "Xbox360TOC.txt")
    toc_bak = toc_path + ".before_rus_bak"
    if not os.path.exists(toc_bak):
        print(f"Backing up TOC: {toc_path} -> {toc_bak}")
        shutil.copy2(toc_path, toc_bak)
        
    with open(toc_path, 'r', encoding='utf-8', errors='ignore') as f:
        toc_lines = f.readlines()
        
    updated_count = 0
    new_toc_lines = []
    for line in toc_lines:
        parts = line.strip().split()
        if len(parts) >= 5:
            # Format: size 0 0 path md5
            entry_path = parts[3]
            if entry_path in updates_map:
                new_size, new_md5 = updates_map[entry_path]
                new_line = f"{new_size} {parts[1]} {parts[2]} {entry_path} {new_md5}\n"
                new_toc_lines.append(new_line)
                updated_count += 1
                print(f"Updated TOC line for {entry_path}: old={line.strip()} -> new={new_line.strip()}")
                continue
        new_toc_lines.append(line)
        
    with open(toc_path, 'w', encoding='utf-8') as f:
        f.writelines(new_toc_lines)
        
    print(f"\nSuccessfully installed Russian localization! Updated {updated_count} TOC entries.")

if __name__ == "__main__":
    main()
