
def write_data():
    """
    Writes user-input data to a specified file, replacing any existing content.

    Prompts the user to enter the file path and the data they want to write.
    If the file exists, its content will be overwritten. If an error occurs, an appropriate message is shown.

    Args:
        file_name (str): The path to the file to write to (entered by the user).

    Returns:
        None: The function only prints output and returns None in case of an error.
    """
    file_name = input("Enter file location: ").strip()
    try:
        with open(file_name, 'w', encoding='utf-8') as f:
            data = input("Enter the data you want to write: ")
            f.write(data)
            print("✅ File written successfully.")
    except FileNotFoundError:
        print("❌ File not found. Please check the file path and try again.")
        return None
    except OSError as e:
        print(f"❌ An error occurred: {e}")
        return None