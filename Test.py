import os
from pathlib import Path
from OpticalCharacterRecognition import OCR


class micro:
    result_directories = []

    def __init__(self):
        self.result_directories = []
        # self.path = path

    '''
    Recursively traverse through the directory and its subdirectories, checking if they contain both 'labels' and 'Row' 
    folders but not 'itemized_data.xlsx' or 'itemized_data.csv'. If found, add the directory path to the result list.
    '''
    def checkFolders(self, based_path):
        def _check_directory(dir_path):
            if 'labels' in os.listdir(dir_path) and 'Row' in os.listdir(dir_path):
                # if not any(filename.startswith('itemized_data') for filename in os.listdir(dir_path)):
                self.result_directories.append(dir_path)

        selected_items = []

        for item in os.listdir(based_path):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                _check_directory(item_path)
                self.checkFolders(item_path)
                selected_items.extend(self.checkFolders(item_path))

        return selected_items


if __name__ == "__main__":
    # Define the path to the directory
    directory = r'D:/Archive/Sample_201-250'

    micro = micro()
    micro.checkFolders(directory)

    for ele in micro.result_directories:
        print(ele)

