import os
import shutil
import platform
from pathlib import Path
from send2trash import send2trash

############################################
# USER CACHE FILES DELETION
############################################


def sizeof_fmt(num, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Y{suffix}"

def delete_user_cache(confirm:bool = True, go_into_the_trash:bool = False, debug:bool = True):
    system = platform.system()
    paths_to_clean = []

    home = Path.home()

    if system == 'Windows':
        local_app_data = os.getenv('LOCALAPPDATA')
        if local_app_data:
            paths_to_clean.append(Path(local_app_data) / 'Temp')
            paths_to_clean.append(Path(local_app_data) / 'Microsoft' / 'Windows' / 'INetCache')
            paths_to_clean.append(Path(local_app_data) / 'Cache')
    elif system == 'Darwin':  # macOS
        paths_to_clean.append(home / 'Library' / 'Caches')
        paths_to_clean.append(home / 'Library' / 'Logs')
    else:  # Linux and others
        paths_to_clean.append(home / '.cache')
        paths_to_clean.append(home / '.local' / 'share' / 'Trash')

    if confirm:
        print("Do you want to delete user cache files from these locations?")
        for p in paths_to_clean:
            print(f" - {p}")
        user_input = input("(y/n): ").strip().lower()
        if user_input != 'y':
            print("Operation cancelled.")
            return

    total_freed = 0

    for cache_path in paths_to_clean:
        if cache_path.exists():
            if debug:
                print(f"Cleaning cache in: {cache_path}")
            try:
                for item in cache_path.iterdir():
                    try:
                        size = item.stat().st_size
                        if go_into_the_trash:
                            send2trash(str(item))
                            if debug:
                                print(f"Moved to trash: {item} ({sizeof_fmt(size)})")
                        else:
                            if item.is_dir():
                                shutil.rmtree(item)
                                if debug:
                                    print(f"Deleted directory: {item} ({sizeof_fmt(size)})")
                            else:
                                item.unlink()
                                if debug:
                                    print(f"Deleted file: {item} ({sizeof_fmt(size)})")
                        total_freed += size
                    except Exception as e:
                        print(f"Error deleting {item}: {e}")
            except Exception as e:
                print(f"Error accessing {cache_path}: {e}")
        else:
            if debug:
                print(f"Cache path does not exist: {cache_path}")

    if debug:
        if total_freed > 0:
            print(f"User cache files deletion completed.")
            print(f"Total space freed: {sizeof_fmt(total_freed)}")
        else:
            print("No cache files were deleted.")


delete_user_cache()
