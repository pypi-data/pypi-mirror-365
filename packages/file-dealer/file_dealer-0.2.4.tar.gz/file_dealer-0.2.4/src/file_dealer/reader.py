

def get_data():
    """
    Reads the content of a specified file and returns it.

    Prompts the user to enter the file path. If the file exists and is not empty,
    its contents are printed and returned. If the file is empty or an error occurs,
    an appropriate message is displayed.

    Args:
        file_name (str): The path to the file to be read (entered by the user).

    Returns:
        str or None: The file content if successful; None if the file is empty or an error occurs.
    """
    file_name = input("Enter file location: ").strip()
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            data = f.read()
            if not data:
                print("❌ The file is empty.")
                return None
            print("📝 Your data is:")
            print(data)
            print("✅ Data read successfully.")
            print("📌 Your data was saved in the variable 'data'.")
            return data
    except FileNotFoundError:
        print("❌ File not found. Please check the file path and try again.")
        return None
    except OSError as e:
        print(f"❌ An error occurred: {e}")
        return None


def read_data():
    """
    Reads and displays the content of a specified file.

    Prompts the user to enter the file path. If the file exists, its contents are printed.
    If the file does not exist or an error occurs, an appropriate message is displayed.

    Args:
        file_name (str): The path to the file to be read (entered by the user).

    Returns:
        None: The function only prints output and returns None in case of error.
    """
    file_name = input("Enter file location: ").strip()
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            data = f.read()
            print("📝 Your data is:")
            print(data)
            print("✅ File read successfully.")
    except FileNotFoundError:
        print("❌ File not found. Please check the file path and try again.")
        return None
    except OSError as e:
        print(f"❌ An error occurred: {e}")
        return None


