import os
import shutil

# Define the parent folder path
parent_folder_path = "D:/Archive\\Sample_451-500"

# Get the list of folders in the parent folder
parent_folders = os.listdir(parent_folder_path)

# Define the main archive folder path
archive_path = "D:/Archive"

# Get the list of subfolders in the main archive folder
subfolders = [f.path for f in os.scandir(archive_path) if f.is_dir() and f.path != parent_folder_path]

# Iterate over subfolders
for subfolder_path in subfolders:
    # Get the list of folders in the current subfolder
    subfolder_folders = os.listdir(subfolder_path)

    # Check for similar folder names
    similar_folders = set(parent_folders) & set(subfolder_folders)

    # Print out the similar folder names
    if similar_folders:
        print(f"Similar folder(s) found in subfolder: {subfolder_path}")
        for folder in similar_folders:
            print(folder)
            # Remove the folder from "Sample_301-351"
            folder_path = os.path.join(parent_folder_path, folder)
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
                print(f"Folder '{folder}' removed from '{parent_folder_path}'")
    else:
        print(f"No similar folders found in subfolder: {subfolder_path}")
