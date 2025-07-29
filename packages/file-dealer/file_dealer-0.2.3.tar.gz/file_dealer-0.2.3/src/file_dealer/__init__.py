
"""
file_dealer package

Provides helper functions to read, write, append, and delete files easily.
"""

from .reader import read_data, get_data
from .writer import write_data
from .deleter import delete_data
from .append import append_data
import shutil

folders = ['dist', 'build', 'your_package_name.egg-info']

for folder in folders:
    try:
        shutil.rmtree(folder)
        print(f"Deleted {folder}")
    except FileNotFoundError:
        print(f"{folder} not found, skipping")
