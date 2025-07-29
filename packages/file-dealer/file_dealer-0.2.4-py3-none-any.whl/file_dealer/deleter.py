
import os

def delete_data():
    """
    Deletes a specified file from the file system.

    Prompts the user to enter the path of a file to delete. If the file exists, it will be removed.
    If the file does not exist or an error occurs, an appropriate error message is displayed.

    Args:
        file_name (str): The full path to the file that should be deleted (entered by the user).

    Returns:
        None: Only returns if an error occurs during deletion.
    """
    file_name = input("Enter file location you want to delete: ").strip()
    try:
        os.remove(file_name)
        print("✅ Data was deleted successfully.")
    except FileNotFoundError:
        print("❌ File not found. Please check the file path and try again.")
        return None
    except OSError as e:
        print(f"❌ An error occurred: {e}")
        return None