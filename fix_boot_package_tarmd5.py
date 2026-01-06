#!/usr/bin/env python3
import os
import sys
import hashlib
import tarfile
import shutil

INPUT = 'recovery.img'
BACKUP = 'recovery.img.bak'
FIXED = 'recovery_fixed.img'
OUT_TAR_MD5 = 'recovery_a.tar.md5'

SIGNERVER2_MAGIC = b'SignerVer02'
SIGNERVER2_SIZE = 512

def die(msg):
    print('Error:', msg); sys.exit(1)

if not os.path.isfile(INPUT):
    die(f"Input not found: {INPUT}")

# Backup
shutil.copyfile(INPUT, BACKUP)
print(f"Backup created: {BACKUP}")

# Read, locate, overwrite SignerVer02 region
data = bytearray(open(INPUT, 'rb').read())
idx = data.find(SIGNERVER2_MAGIC)
if idx == -1:
    die("SignerVer02 magic not found in image")

# Ensure we have space for full region
if idx + SIGNERVER2_SIZE > len(data):
    die("Image too small to contain full SignerVer02 region at found offset")

# Overwrite: write magic then zero the rest of the 512-byte region
data[idx:idx + len(SIGNERVER2_MAGIC)] = SIGNERVER2_MAGIC
data[idx + len(SIGNERVER2_MAGIC): idx + SIGNERVER2_SIZE] = b'\x00' * (SIGNERVER2_SIZE - len(SIGNERVER2_MAGIC))

with open(FIXED, 'wb') as f:
    f.write(data)
print(f"Wrote fixed image: {FIXED}")

# Create tar (without .md5 extension first)
tmp_tar = OUT_TAR_MD5
if tmp_tar.endswith('.md5'):
    tmp_tar = tmp_tar[:-4]

# Use a temporary dir to place recovery.img inside tar
tmp_dir = os.path.join('.', 'temp_recovery_one_shot')
os.makedirs(tmp_dir, exist_ok=True)
try:
    recover_inside = os.path.join(tmp_dir, 'recovery.img')
    with open(FIXED, 'rb') as src, open(recover_inside, 'wb') as dst:
        dst.write(src.read())

    with tarfile.open(tmp_tar, 'w') as tar:
        tar.add(recover_inside, arcname='recovery.img')

    # Compute MD5 of the tar
    md5 = hashlib.md5()
    with open(tmp_tar, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            md5.update(chunk)
    md5_hex = md5.hexdigest()

    final_name = tmp_tar + '.md5'
    os.rename(tmp_tar, final_name)
    with open(final_name + '.txt', 'w') as f:
        f.write(md5_hex)

    print(f"Created Odin-compatible file: {final_name}")
    print(f"MD5: {md5_hex}")

finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)
