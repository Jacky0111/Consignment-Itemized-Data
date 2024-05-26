import os
from pathlib import Path
from OpticalCharacterRecognition import OCR


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

    selected_items = []

    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            _check_directory(item_path)
            check_folders(item_path, result_list)
            selected_items.extend(check_folders(item_path, result_list))
    return selected_items


# Define the path to the directory
directory = r'D:\Archive\Sample_351-400'

# Initialize an empty list to store the result
result_directories = []

# Call the function to start checking folders
claim_no = check_folders(directory, result_directories)

# Print the list of directories containing both 'labels' and 'Row' folders, but not containing itemized data files
print("Directories containing both 'labels' and 'Row' folders, but not containing itemized data files:")
for i, directory_path in enumerate(result_directories, start=1):
    print(f"{i}. {directory_path}")

row_folder_list = []
# Phase 2
print("\nPhase 2 - Reading 'Row' images that start with 'row_' and 'labels' files that start with 'row_boxes_'...")
for directory_path in result_directories:
    row_folder = os.path.join(directory_path, 'Row')
    row_folder_list.append(row_folder)
    print(f'row_folder: {row_folder}, {type(row_folder)}')

    labels_folder = os.path.join(directory_path, 'labels')
    if os.path.exists(row_folder):
        print(f"\nReading images from 'Row' folder: {row_folder}:")
        row_images = [filename for filename in os.listdir(row_folder) if filename.startswith('row_') and os.path.isfile(os.path.join(row_folder, filename))]
        # image_files = sorted([f for f in files if f.endswith('.png')], key=natural_sort_key)

        if row_images:
            for i, image in enumerate(row_images, start=1):
                print(f"{i}. {image}")
        else:
            print("No images found starting with 'row_' in the 'Row' folder.")

        bbox_images = [filename for filename in os.listdir(row_folder) if filename.startswith('bbox') and os.path.isfile(os.path.join(row_folder, filename))]
        for bbox in bbox_images:
            if bbox.startswith('bbox'):
                os.remove(os.path.join(row_folder, bbox))
                print(f"Deleted {bbox}")

    else:
        print(f"\n'{row_folder}' does not exist.")

    if os.path.exists(labels_folder):
        print(f"\nReading label files from 'labels' folder: {labels_folder}:")
        label_files = [filename for filename in os.listdir(labels_folder) if filename.startswith('row_boxes_') and os.path.isfile(os.path.join(labels_folder, filename))]
        if label_files:
            for i, label_file in enumerate(label_files, start=1):
                print(f"{i}. {label_file}")
                # Read the content of the label file
                with open(os.path.join(labels_folder, label_file), 'r') as f:
                    content = f.readlines()
                    # Store the content in a variable
                    # The first value of the row is page, the rest is coordinate x y w h
                    label_data = []
                    for j, line in enumerate(content, start=1):
                        values = line.strip().split()
                        label_data.append((j, values[0], [float(val) for val in values[1:]]))
                    # print("Label data:")
                    # for row_num, page, coords in label_data:
                    #     print(f"{row_num}. Page: {page}, Coordinates: {coords}")
        else:
            print("No label files found starting with 'row_boxes_' in the 'labels' folder.")
    else:
        print(f"\n'{labels_folder}' does not exist.")

# Print the total count of selected directories
print("\nTotal directories selected:", len(result_directories))

for result, rf in zip(result_directories, row_folder_list):
    claim_no = Path(result).name
    print(f'result: {result}')
    print(f'claim_no: {claim_no}')
    ocr = OCR(result, rf, [claim_no])
    ocr.runner()
    break




