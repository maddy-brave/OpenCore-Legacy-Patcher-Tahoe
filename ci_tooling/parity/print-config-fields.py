"""Print the load-bearing fields of a built OpenCore config.plist.

Usage: python3 print-config-fields.py <path-to-OpenCore-Build>
Pure plistlib, no OCLP imports, so it runs on any Python 3.9+ host.
"""
import plistlib
import sys
from pathlib import Path

APPLE_NVRAM = "7C436110-AB2A-4BBB-A880-FE41995C9F82"
OCLP_NVRAM = "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102"


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    root = Path(sys.argv[1])
    with (root / "EFI/OC/config.plist").open("rb") as fh:
        cfg = plistlib.load(fh)

    rev = cfg.get("#Revision", {})
    for key in ("Build-Version", "Build-Type", "OpenCore-Version", "Original-Model"):
        print(f"{key:<20}: {rev.get(key)}")
    print()

    print("Kernel:Add enabled kexts (BundlePath, MinKernel, MaxKernel):")
    for kext in cfg["Kernel"]["Add"]:
        if kext.get("Enabled"):
            print(f"  {kext['BundlePath']:<44} min={kext.get('MinKernel') or '-':<9} max={kext.get('MaxKernel') or '-'}")
    print()

    print("UEFI:Drivers enabled:")
    for drv in cfg["UEFI"]["Drivers"]:
        if drv.get("Enabled"):
            print(f"  {drv['Path']}  args={drv.get('Arguments', '')!r}")
    print("UEFI:APFS EnableJumpstart:", cfg["UEFI"]["APFS"].get("EnableJumpstart"))
    print("ACPI:Add enabled:", [a["Path"] for a in cfg["ACPI"]["Add"] if a.get("Enabled")])
    print()

    apple = cfg["NVRAM"]["Add"].get(APPLE_NVRAM, {})
    oclp = cfg["NVRAM"]["Add"].get(OCLP_NVRAM, {})
    csr = apple.get("csr-active-config")
    print("boot-args          :", apple.get("boot-args"))
    print("csr-active-config  :", csr.hex() if isinstance(csr, bytes) else csr)
    print("OCLP-Version       :", oclp.get("OCLP-Version"))
    print("OCLP-Model         :", oclp.get("OCLP-Model"))
    print("OCLP-Settings      :", oclp.get("OCLP-Settings"))
    print()

    pinfo = cfg["PlatformInfo"]
    print("PlatformInfo Automatic:", pinfo.get("Automatic"), " UpdateSMBIOS:", pinfo.get("UpdateSMBIOS"))
    print("Generic SystemProductName:", pinfo.get("Generic", {}).get("SystemProductName"))
    print("SMBIOS BoardProduct :", pinfo.get("SMBIOS", {}).get("BoardProduct"))
    print("DataHub BoardProduct:", pinfo.get("DataHub", {}).get("BoardProduct"))
    print()

    sec = cfg["Misc"]["Security"]
    boot = cfg["Misc"]["Boot"]
    print("Misc:Security SecureBootModel:", sec.get("SecureBootModel"), " ScanPolicy:", sec.get("ScanPolicy"), " Vault:", sec.get("Vault"))
    print("Misc:Boot PickerMode:", boot.get("PickerMode"), " ShowPicker:", boot.get("ShowPicker"), " Timeout:", boot.get("Timeout"))
    print("Misc:BlessOverride:", cfg["Misc"].get("BlessOverride"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
