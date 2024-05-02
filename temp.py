import os

# Define the directory path
directory = r'C:\Users\ChiaChungLim\PycharmProjects\Consignment-Itemized-Data\Run Data'

# Iterate over all folders in the directory
for folder_name in os.listdir(directory):
    folder_path = os.path.join(directory, folder_name)

    # Check if the item in the directory is a folder
    if os.path.isdir(folder_path):
        # Check if the length of the folder name is 14
        if len(folder_name) == 14:
            # Skip this folder
            continue

        # Rename the folder
        new_folder_name = folder_name[:14]  # Take the first 14 characters
        new_folder_path = os.path.join(directory, new_folder_name)

        try:
            os.rename(folder_path, new_folder_path)
            print(f"Renamed '{folder_name}' to '{new_folder_name}'")
        except OSError as e:
            print(f"Error renaming '{folder_name}': {e}")
