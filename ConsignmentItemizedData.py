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
    images_path = None
    dataset_path = None
    output_folder_path = None

    def __init__(self):
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
        print(f'self.output_folder_path: {self.output_folder_path}')

        # Navigate to the specified folder path
        os.chdir(self.output_folder_path)

        # Use glob to find all PNG files in the current directory
        img_list = glob.glob('*.png')

        current_directory = os.getcwd()
        os.chdir(os.path.dirname(os.path.dirname(current_directory)))

        for img in img_list:
            Detect.parseOpt(self.output_folder_path, img, 'table.pt', 0.8)



if __name__ == '__main__':
    cid = CID()
    cid.runner()
