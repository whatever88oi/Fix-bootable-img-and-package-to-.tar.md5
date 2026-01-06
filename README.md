
$ python fix_boot_package_tarmd5.py  recovery.img recovery.tar.md5

or

Save and run the following single Python script (one-shot) from the same directory as recovery.img. It will back up recovery.img to recovery.img.bak, overwrite the 512-byte SignerVer02 area (writing the magic then zeroing the remainder), write recovery_fixed.img, and produce recovery_a.tar.md5 (and recovery_a.tar.md5.txt with the MD5).
