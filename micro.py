import os

def check_folders(directory, result_list):
    """
    Recursively traverse through the directory and its subdirectories,
    checking if they contain both 'labels' and 'Row' folders but not 'itemized_data.xlsx' or 'itemized_data.csv'.
    If found, add the directory path to the result list.
    """
    def _check_directory(directory_path):
        if 'labels' in os.listdir(directory_path) and 'Row' in os.listdir(directory_path):
            if not any(filename.startswith('itemized_data') for filename in os.listdir(directory_path)):
                result_list.append(directory_path)

    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            _check_directory(item_path)
            check_folders(item_path, result_list)

# Define the path to the directory
directory = r'D:\Archive\Sample_51-100'

# Initialize an empty list to store the result
result_directories = []

# Call the function to start checking folders
check_folders(directory, result_directories)

# Print the list of directories containing both 'labels' and 'Row' folders, but not containing itemized data files
print("Directories containing both 'labels' and 'Row' folders, but not containing itemized data files:")
for i, directory_path in enumerate(result_directories, start=1):
    print(f"{i}. {directory_path}")

# Phase 2
print("\nPhase 2 - Reading 'Row' images that start with 'row_'...")
for directory_path in result_directories:
    row_folder = os.path.join(directory_path, 'Row')
    if os.path.exists(row_folder):
        print(f"\nReading images from {row_folder}:")
        row_images = [filename for filename in os.listdir(row_folder) if filename.startswith('row_') and os.path.isfile(os.path.join(row_folder, filename))]
        if row_images:
            for i, image in enumerate(row_images, start=1):
                print(f"{i}. {image}")
        else:
            print("No images found starting with 'row_' in this directory.")
    else:
        print(f"\n'{row_folder}' does not exist.")

# Print the total count of selected directories
print("\nTotal directories selected:", len(result_directories))
