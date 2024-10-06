import os
import sys
import shutil
import subprocess
import winreg
import ctypes
from pathlib import Path

def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def clean_temp_files():
    """Clean temporary files in Windows."""
    temp_dirs = [
        os.getenv('TEMP'),
        os.getenv('TMP'),
        os.path.join(os.getenv('SYSTEMROOT'), 'Temp'),
    ]

    for temp_dir in temp_dirs:
        print(f"\nCleaning temporary files in: {temp_dir}")
        try:
            for root, dirs, files in os.walk(temp_dir):
                for f in files:
                    try:
                        os.unlink(os.path.join(root, f))
                        print(f"Deleted file: {os.path.join(root, f)}")
                    except Exception as e:
                        print(f"Unable to delete file {os.path.join(root, f)}: {e}")
                for d in dirs:
                    try:
                        shutil.rmtree(os.path.join(root, d), ignore_errors=True)
                        print(f"Deleted directory: {os.path.join(root, d)}")
                    except Exception as e:
                        print(f"Unable to delete directory {os.path.join(root, d)}: {e}")
        except Exception as e:
            print(f"Error cleaning {temp_dir}: {e}")
    print("\nTemporary files cleaned.")

def empty_recycle_bin():
    """Empty the Recycle Bin."""
    print("\nEmptying the Recycle Bin...")
    try:
        SHEmptyRecycleBin = ctypes.windll.shell32.SHEmptyRecycleBinW
        SHERB_NOCONFIRMATION = 0x00000001
        SHERB_NOPROGRESSUI = 0x00000002
        SHERB_NOSOUND = 0x00000004
        result = SHEmptyRecycleBin(None, None, SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND)
        if result == 0:
            print("Recycle Bin emptied successfully.")
        else:
            print(f"Failed to empty Recycle Bin. Error code: {result}")
    except Exception as e:
        print(f"Error emptying Recycle Bin: {e}")

def disable_startup_programs():
    """Disable startup programs by removing their entries from the registry."""
    print("\nDisabling startup programs...")
    startup_key_paths = [
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        r"Software\Microsoft\Windows\CurrentVersion\RunOnce",
    ]

    for root_name, root in [('HKEY_CURRENT_USER', winreg.HKEY_CURRENT_USER), ('HKEY_LOCAL_MACHINE', winreg.HKEY_LOCAL_MACHINE)]:
        for sub_key in startup_key_paths:
            try:
                key = winreg.OpenKey(root, sub_key, 0, winreg.KEY_ALL_ACCESS)
                values = []
                i = 0
                while True:
                    try:
                        value = winreg.EnumValue(key, i)
                        values.append((value[0], value[1]))
                        i += 1
                    except OSError:
                        break
                if values:
                    print(f"\nStartup items in {root_name}\\{sub_key}:")
                    for idx, (name, path) in enumerate(values):
                        print(f"{idx+1}. {name} - {path}")
                    disable = input("Do you want to disable these startup programs? (y/n): ").lower()
                    if disable == 'y':
                        for name, _ in values:
                            try:
                                winreg.DeleteValue(key, name)
                                print(f"Disabled {name}")
                            except Exception as e:
                                print(f"Error disabling {name}: {e}")
                winreg.CloseKey(key)
            except Exception as e:
                print(f"Error accessing registry key {sub_key}: {e}")
    print("\nStartup programs disabled.")

def adjust_performance_settings():
    """Adjust Windows performance settings."""
    while True:
        print("\nAdjust Performance Settings:")
        print("1. Adjust visual effects for best performance")
        print("2. Set power plan to High Performance")
        print("3. Back to main menu")
        choice = input("Enter your choice: ")
        if choice == '1':
            adjust_visual_effects()
        elif choice == '2':
            set_power_plan()
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")

def adjust_visual_effects():
    """Adjust visual effects for best performance."""
    print("\nAdjusting visual effects for best performance...")
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "VisualFXSetting", 0, winreg.REG_DWORD, 2)
        winreg.CloseKey(key)
        print("Visual effects adjusted for best performance.")
        print("You may need to log off and log back in for changes to take effect.")
    except Exception as e:
        print(f"Error adjusting visual effects: {e}")

def set_power_plan():
    """Set power plan to High Performance."""
    print("\nSetting power plan to High Performance...")
    try:
        subprocess.run(['powercfg', '/setactive', '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'], check=True)
        print("Power plan set to High Performance.")
    except subprocess.CalledProcessError as e:
        print(f"Error setting power plan: {e}")

def main_menu():
    while True:
        print("\n=== Windows System Maintenance Tool ===")
        print("1. Clean Temporary Files")
        print("2. Empty Recycle Bin")
        print("3. Disable Startup Programs")
        print("4. Adjust Performance Settings")
        print("5. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            clean_temp_files()
        elif choice == '2':
            empty_recycle_bin()
        elif choice == '3':
            disable_startup_programs()
        elif choice == '4':
            adjust_performance_settings()
        elif choice == '5':
            print("\nExiting...")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

def main():
    if not is_admin():
        print("This script needs to be run as administrator.")
        try:
            script = sys.argv[0]
            params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
        except Exception as e:
            print(f"Failed to elevate privileges: {e}")
            input("Press Enter to exit...")
        sys.exit()
    main_menu()

if __name__ == "__main__":
    main()
