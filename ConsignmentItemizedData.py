# Empowers the end user to make choices between performing document conversion and optical character recognition (OCR)

import os
import re
import cv2
import glob
import shutil
import pytesseract
import numpy as np
from datetime import datetime
from paddleocr import PaddleOCR
from pdf2image import convert_from_path

from Detect import Detect

# from OpticalCharacterRecognition import OCR

poppler_path = r'C:\Program Files\poppler-23.05.0\Library\bin'
os.environ["PATH"] += os.pathsep + poppler_path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class CID:
    images_list = []
    images_path = None
    dataset_path = None
    output_folder_path = None

    def __init__(self):
        self.images_list = []
        self.images_path = None
        self.dataset_path = None
        self.output_folder_path = None

    def runner(self):
        pass

    @staticmethod
    def setFolderPath(file_name):
        path = f"output/{file_name}_{str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))}"
        CID.createFolder(path)
        return path

    '''
    Create a new folder if it does not already exist.
    @param directory: a string representing the path of the directory to be created.
    '''

    @staticmethod
    def createFolder(directory):
        try:
            os.makedirs(directory)
            print(f'{directory} has been made')
        except FileExistsError:
            pass

    '''
    Process the selected files by copying them to the specified destination folder.
    @param files: a list of strings representing the paths of the files to be processed.
    @param destination: a string representing the path of the destination folder.
    '''

    @staticmethod
    def processSelectedFiles(files, destination):
        # Remove existing files in the destination folder
        for existing_file in os.listdir(destination):
            file_path = os.path.join(destination, existing_file)
            if os.path.isfile(file_path):
                os.remove(file_path)  # Remove the existing file

        # Copy the selected files to the destination folder
        for path in files:
            shutil.copy(path, destination)  # Copy the file to the destination folder

    # def identifyHospital(self, folder):

    # # Get a list of all PNG images in the folder
    # all_images = [file for file in os.listdir(folder) if file.endswith('.png')]
    #
    # # Iterate through each PNG image and perform OCR
    # for image_file in all_images:
    #     image_path = os.path.join(folder, image_file)
    #
    #     # Read the image using OpenCV
    #     img = cv2.imread(image_path)
    #
    #     # Perform OCR using pytesseract
    #     text = pytesseract.image_to_string(img, config=r'--oem 3 --psm 4 -l eng')
    #
    #     for keyword, hospital_code in hospital_dict.items():
    #         if re.search(keyword, all_extracted_text, re.IGNORECASE):
    #             return hospital_code
    #
    # return None

    def converter(self, file_path):
        # Split folder and file name
        self.output_folder_path, file_name_with_ext = os.path.split(file_path)
        file_name, ext = os.path.splitext(file_name_with_ext)

        # Convert image
        images = convert_from_path(file_path, dpi=300)

        # Save images to pre-defined location
        self.saveImages(images, file_name)

    '''
    Save converted images to the output folder.
    @param images: A list of images to be saved.
    @param of: A string representing the path to the folder where the images will be saved.
    @param pdf_name: A string representing the name of the original PDF file (without extension).
    '''
    def saveImages(self, images, pdf_name):
        for idx, img in enumerate(images):
            page_index = str(idx + 1).zfill(2)
            img_path = os.path.join(self.output_folder_path, f'{pdf_name}_page_{page_index}.png')
            img.save(img_path, 'PNG')

    def tableDetection(self):
        # Navigate to the specified folder path
        os.chdir(self.output_folder_path)

        # Use glob to find all PNG files in the current directory
        self.images_list = [os.path.splitext(filename)[0] for filename in glob.glob('*.png')]

        # Move up two directories
        os.chdir(os.path.dirname(os.path.dirname(os.getcwd())))

        for img in self.images_list:
            Detect.parseOpt(self.output_folder_path, img, 'table.pt', 0.9)

    def rowDetection(self):
        table_boxes_path = f'{self.output_folder_path}/labels/table_boxes.txt'

        # Read values from the row boxes text file
        with open(table_boxes_path, 'r') as file:
            selected_pages = [int(line.split()[1]) for line in file]

        # Create a list of modified image names
        new_img_list = [img_name + '_crop' for img_name in self.images_list if int(img_name[-1]) in selected_pages]
        print(f'new_img_list: {new_img_list}')

        for img in new_img_list:
            # Utilize the 'parseOpt' method to detect rows using the 'row.pt' file and a threshold of 0.4
            Detect.parseOpt(self.output_folder_path, img, 'row.pt', 0.3)

            # Define paths for the table image and row boxes
            table_img_path = f'{self.output_folder_path}/{img}.png'
            row_boxes_path = f'{self.output_folder_path}/labels/row_boxes.txt'

            # Read the table image
            tb_img = cv2.imread(table_img_path)
            crop_img = tb_img.copy()

            # Read values from the row boxes text file
            with open(row_boxes_path, 'r') as file:
                lines = file.readlines()
                # Remove the first value of the line and convert them to a nested list
                values = [list(map(float, line.strip().split()[1:])) for line in lines]
                # Sort based on the third value (y) in ascending order
                values.sort(key=lambda j: j[1], reverse=False)

            # Update the text file with the sorted values
            with open(row_boxes_path, 'w') as file:
                for value in values:
                    file.write(f'0 {value[0]} {value[1]} {value[2]} {value[3]}\n')

            # Create "Row" folder
            os.makedirs(os.path.join(self.output_folder_path, 'Row'), exist_ok=True)
            row_folder = f'{self.output_folder_path}/Row'

            # Convert the format to xywh and draw lines on the image
            for idx, value in enumerate(values):
                x, y, w, h = value[0], value[1], value[2], value[3]
                y = int((y + h / 2) * tb_img.shape[0])
                w = int(w * tb_img.shape[1])
                h = int(h * tb_img.shape[0])

                # Draw lines on the image
                cv2.line(tb_img, (0, y), (tb_img.shape[0] + w, y), (255, 0, 0), 2)
                cv2.line(tb_img, (0, y - h), (tb_img.shape[0] + w, y - h), (255, 0, 0), 2)

                # Crop the row based on the coordinates
                cropped_row = crop_img[y - h:y, 0:crop_img.shape[1]]

                # Save the cropped row in the 'Row' folder
                cv2.imwrite(f'{row_folder}/row_{str(idx).zfill(3)}.png', cropped_row)

            # Save the annotated image
            cv2.imwrite(f'{self.output_folder_path}/{img[:-5]}_row_revised.png', tb_img)


if __name__ == '__main__':
    cid = CID()
    cid.runner()
