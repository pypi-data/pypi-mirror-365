from . import cache, temp

def delete_all_temporary_files(confirm: bool = True, go_into_the_trash: bool = False, debug: bool = True):
    '''Delete all temporary files including user and system temporary files with confirmation option and option to move to trash instead of permanent deletion.'''
    temp.delete_user_temporary_files(confirm, go_into_the_trash, debug)
    temp.delete_system_temporary_files(confirm, go_into_the_trash, debug)
    if debug:
        print("All temporary files deletion completed.")

def delete_all(confirm: bool = True, go_into_the_trash: bool = False, debug: bool = True):
    '''Delete all user cache and temporary files with confirmation option and option to move to trash instead of permanent deletion.'''
    cache.delete_user_cache(confirm, go_into_the_trash, debug)
    temp.delete_user_temporary_files(confirm, go_into_the_trash, debug)
    if debug:
        print("All user cache and temporary files deletion completed.")

__all__ = [
    "delete_all_temporary_files",
    "delete_all",
    "cache",
    "temp",
]