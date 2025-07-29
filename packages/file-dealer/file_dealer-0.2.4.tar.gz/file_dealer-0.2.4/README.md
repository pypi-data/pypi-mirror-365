# file_dealer

**file_dealer** is a simple Python package that makes it easier to work with files — read, write, append, and delete — using interactive, beginner-friendly commands.

## ✨ Features

- 📖 Read the full content of any file
- 🖊 Write new data to a file (creates the file if it doesn't exist)
- ➕ Append new data to an existing file
- ❌ Delete files easily

## 📦 Installation

```bash
pip install file_dealer
```


After installing it, you can freely use it's functions such as:
- append_data()
- write_data()
- delete_data()
- get_data()
- read data()

# Example

from file_dealer import append_data, write_data, delete_data, get_data

(Using any of these functions will make the user to first input a path where to realise the action.)

write_data()

## Terminal:
Enter file location: <\my path>

Enter the data you want to write: <(the data i want to write)>

✅ File written successfully.

(If any errors occur, the program won't realize the action and, instead, it will print out the error.)

