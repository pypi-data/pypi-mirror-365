import os, shutil, tempfile
from send2trash import send2trash

############################################
# USER TEMPORARY FILES DELETION
############################################

def delete_user_temporary_files(confirm: bool = True, go_into_the_trash: bool = False, debug: bool = True):
    '''Delete user temporary files with confirmation option and option to move to trash instead of permanent deletion.'''
    if confirm:
        print(f"Do you want to delete user temporary files? (y/n)")
        user_input = input().strip().lower()
        if user_input == 'y':
            goOn = True
        else:
            goOn = False
            print(f"Operation cancelled successfully.")
            return None
    else:
        goOn = True
    if goOn:
        for root, dirs, files in os.walk(tempfile.gettempdir()):
            for name in files:
                file_path = os.path.join(root, name)
                try:
                    if go_into_the_trash:
                        send2trash(file_path)
                        if debug:
                            print(f"Moved to trash: {file_path}")
                    else:
                        os.remove(file_path)
                        if debug:
                            print(f"Deleted: {file_path}")
                except PermissionError:
                    pass
                except Exception as e:
                    print(f"Error: {file_path} - {e}")
            for name in dirs:
                dir_path = os.path.join(root, name)
                try:
                    if go_into_the_trash:
                        send2trash(dir_path)
                        if debug:
                            print(f"Moved to trash: {dir_path}")
                    else:
                        shutil.rmtree(dir_path)
                        if debug:
                            print(f"Deleted: {dir_path}")
                except PermissionError:
                    pass
                except Exception as e:
                    print(f"Error: {dir_path} - {e}")
        if debug:
            print(f"User temporary files deletion completed.")

############################################
# SYSTEM TEMPORARY FILES DELETION
############################################

def delete_system_temporary_files(confirm: bool = True, go_into_the_trash: bool = False, debug: bool = True):
    '''Delete system temporary files with confirmation option and option to move to trash instead of permanent deletion.'''
    if confirm:
        print(f"Do you want to delete system temporary files? (y/n)")
        user_input = input().strip().lower()
        if user_input == 'y':
            goOn = True
        else:
            goOn = False
            print(f"Operation cancelled successfully.")
            return None
    else:
        goOn = True
    if goOn:
        for root, dirs, files in os.walk("C:\\Windows\\Temp"):
            for name in files:
                file_path = os.path.join(root, name)
                try:
                    if go_into_the_trash:
                        send2trash(file_path)
                        if debug:
                            print(f"Moved to trash: {file_path}")
                    else:
                        os.remove(file_path)
                        if debug:
                            print(f"Deleted: {file_path}")
                except PermissionError:
                    pass
                except Exception as e:
                    print(f"Error: {file_path} - {e}")
            for name in dirs:
                dir_path = os.path.join(root, name)
                try:
                    if go_into_the_trash:
                        send2trash(dir_path)
                        if debug:
                            print(f"Moved to trash: {dir_path}")
                    else:
                        shutil.rmtree(dir_path)
                        if debug:
                            print(f"Deleted: {dir_path}")
                except PermissionError:
                    pass
                except Exception as e:
                    print(f"Error: {dir_path} - {e}")
        if debug:
            print(f"System temporary files deletion completed.")