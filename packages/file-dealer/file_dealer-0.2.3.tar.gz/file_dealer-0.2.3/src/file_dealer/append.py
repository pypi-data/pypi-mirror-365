
import shutil
def append_data():
    """
    Appends user-input data to a specified file.

    Prompts the user to enter a file path and appends lines of text to the file.
    The user can keep entering data, and typing 'exit' will stop the loop.

    Args:
    file_name (str): The name of the file to append data to.

    Returns:
    None: Only returns if an error occurs during file access.
    """
    file_name = input("Enter file location to append data: ").strip()
    try:
        with open(file_name, 'a', encoding='utf-8') as f:
            data = input(
                    "Enter the data you want to append (or type 'exit' to finish): ")
            f.write('\n' + data)
            while True:
                data = input()
                if data.lower() == 'exit':
                    break
                f.write('\n' + data)

            print("✅ Data appended successfully.")
    except FileNotFoundError:
        print("❌ File not found. Please check the file path and try again.")
        return None
    except OSError as e:
        print(f"❌ An error occurred: {e}")
        return None


folders = ['dist', 'build', 'your_package_name.egg-info']

for folder in folders:
    try:
        shutil.rmtree(folder)
        print(f"Deleted {folder}")
    except FileNotFoundError:
        print(f"{folder} not found, skipping")
