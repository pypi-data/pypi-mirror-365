# CLEANMYPC

**CleanMyPC** is a Python library that helps you clean cache, temporary files, and junk from your PC, freeing up space and improving performance.

## Features

- Delete user and system temporary files  
- Clean user cache  
- Option to move files to trash instead of permanent deletion  
- Confirmation prompt before deleting (optional)  
- Prints deleted files and freed space (debug mode)  
- Confirmation and debug are enabled in default
- Move file to trash instead of permanent deletion isn't enabled in default

## Installation

```bash
pip install cleanmypc
```

## Usage

```python
import cleanmypc

# Delete all temporary files
cleanmypc.delete_all_temporary_files()

# Delete user cache and temporary files
cleanmypc.delete_all()

# Delete user temporary files
cleanmypc.temp.delete_user_temporary_files()

# Delete system temporary files
cleanmypc.temp.delete_system_temporary_files()

# Delete cache files
cleanmypc.cache.delete_user_cache()
```

## License
MIT License — see the LICENSE file.

Contributions are welcome! Open an issue or a pull request on GitHub.

