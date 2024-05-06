# Empowers the end user to make choices between performing document conversion and optical character recognition (OCR)

import os
import cv2
import glob
import shutil
import pytesseract
import numpy as np
from datetime import datetime
from deskew import determine_skew
from pdf2image import convert_from_path

from skimage.color import rgb2gray
from skimage.transform import rotate

from Detect import Detect
from OpticalCharacterRecognition import OCR

poppler_path = r'C:\Program Files\poppler-23.05.0\Library\bin'
os.environ["PATH"] += os.pathsep + poppler_path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class CID:
    claim_no = None
    images_path = None
    dataset_path = None
    output_folder_path = None

    images_list = []

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
            deskewed_img = CID.deskew(np.array(img))
            page_index = str(idx + 1).zfill(2)
            img_path = os.path.join(self.output_folder_path, f'{pdf_name}_page_{page_index}.png')
            cv2.imwrite(img_path, deskewed_img)

    '''
    Deskews an image and saves it back to the input path.
    @:param input_path (str)
    '''
    @staticmethod
    def deskew(image):
        # Convert the image to grayscale
        grayscale = rgb2gray(image)

        # Determine the skew angle of the image
        angle = determine_skew(grayscale)

        # Rotate the image to correct the skew and scale it back to 8-bit
        rotated = rotate(image, angle, resize=True) * 255
        rotated = rotated.astype(np.uint8)

        return rotated

    def tableDetection(self):
        # Navigate to the specified folder path
        os.chdir(self.output_folder_path)

        # Use glob to find all PNG files in the current directory
        self.images_list = [os.path.splitext(filename)[0] for filename in glob.glob('*.png')]

        # Move up two directories
        os.chdir(os.path.dirname(os.path.dirname(os.getcwd())))

        for img in self.images_list:
            Detect.parseOpt(self.output_folder_path, img, 'table.pt', 0.7)

    def rowDetection(self, claim_no):
        table_boxes_path = f'{self.output_folder_path}/labels/table_boxes.txt'

        try:
            # Read values from the row boxes text file
            with open(table_boxes_path, 'r') as file:
                selected_pages = [int(line.split()[1]) for line in file]
            # print(f'selected_pages: {selected_pages}')


            # Create a list of modified image names
            new_img_list = [img_name + '_crop' for img_name in self.images_list if
                            int(img_name.split('_')[-1]) in selected_pages]
            # print(f'new_img_list: {new_img_list}')

            # Create "Row" folder
            os.makedirs(os.path.join(self.output_folder_path, 'Row'), exist_ok=True)
            row_folder = f'{self.output_folder_path}/Row'

            for page, img in zip(selected_pages, new_img_list):
                print(f'page: {page}')
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

                threshold = 0.003
                merged_values = []

                # Sort based on the third value (y) in ascending order
                values.sort(key=lambda j: j[1], reverse=False)
                print(f'values: {values}')

                prev_y = None
                prev_h = None
                limit = 0.01
                values2 = []
                for index, coordinate in enumerate(values):
                    print(f'coordinate: {coordinate}')
                    x, y, w, h = map(float, coordinate)  # Extract x, y, width, height

                    if index == 0:
                        new_y = y / 10
                        new_item = [x, new_y, w, new_y * 9]
                        values2.append(new_item)

                    values2.append(coordinate)

                    if prev_y is not None:
                        distance = y - (prev_y + prev_h)
                        print(f"Distance from previous rectangle: {distance:.6f}")
                        if distance > limit:
                            new_item = [x, prev_y + prev_h, w, distance]
                            values2.append(new_item)

                    for no, v in enumerate(values2):
                        print(f'{no+1}. {v}')

                    prev_y = y
                    prev_h = h

                # Merge rows if y-coordinate difference is less than or equal to the threshold
                merged_row = values2[0]
                for idx in range(1, len(values2)):
                    current_row = values2[idx]
                    prev_row = merged_row

                    # print(f'{idx-1}. {prev_row}')
                    # print(f'{idx}. {current_row}')
                    # print(f'Diff: {abs(current_row[1] - prev_row[1])}')

                    if abs(current_row[1] - prev_row[1]) <= threshold:
                        # Merge current row with previous row
                        merged_row = [
                            min(prev_row[0], current_row[0]),  # Choose smaller X
                            current_row[1],  # Choose current Y
                            current_row[2],  # Choose current W
                            max(prev_row[3], current_row[3])  # Choose bigger H
                        ]
                    else:
                        # Append merged row to the list and update merged_row
                        merged_values.append(merged_row)
                        merged_row = current_row

                # Append the last merged row
                merged_values.append(merged_row)
                merged_values.sort(key=lambda j: j[1], reverse=False)

                # Save the text file with the sorted values
                with open(f'{row_boxes_path[:-4]}_{page}.txt', 'w') as output_file:
                    for value in merged_values:
                        output_file.write(f'{page} {value[0]} {value[1]} {value[2]} {value[3]}\n')

                # Create "Row" folder
                os.makedirs(os.path.join(self.output_folder_path, 'Row'), exist_ok=True)
                row_folder = f'{self.output_folder_path}/Row'

                # Convert the format to xywh and draw lines on the image
                for idx, value in enumerate(merged_values):
                    print(f'{idx + 1}. {value}')
                    x, y, w, h = value[0], value[1], value[2], value[3]
                    y = int((y + h / 2) * tb_img.shape[0])
                    w = int(w * tb_img.shape[1])
                    h = int(h * tb_img.shape[0])
                    print(f'{idx + 1}. [{x}, {y}, {w}, {h}]')

                    # Draw lines on the image
                    cv2.line(tb_img, (0, y), (tb_img.shape[0] + w, y), (255, 0, 0), 2)
                    cv2.line(tb_img, (0, 0 if y - h < 0 else y - h), (tb_img.shape[0] + w, 0 if y - h < 0 else y - h), (255, 0, 0), 2)

                    # Crop the row based on the coordinates
                    cropped_row = crop_img[0 if y - h < 0 else y - h:y, 0:crop_img.shape[1]]
                    print(f'cropped_row: crop_img[{0 if y - h < 0 else y - h}:{y}, 0:{crop_img.shape[1]}]')

                    # Save the cropped row in the 'Row' folder
                    cropped_path = f'{row_folder}/row_{page}_{str(idx).zfill(3)}.png'
                    cv2.imwrite(cropped_path, cropped_row)
                    check_img = cv2.imread(cropped_path)
                    gray = cv2.cvtColor(check_img, cv2.COLOR_BGR2GRAY)
                    text = pytesseract.image_to_string(gray).strip()
                    if not text:
                        os.remove(cropped_path)

                        print(f'text: {text}, {bool(text)} {cropped_path}')

                        # Save the annotated image
                cv2.imwrite(f'{self.output_folder_path}/{img[:-5]}_row_revised.png', tb_img)

            ocr = OCR(self.output_folder_path, row_folder, claim_no)
            ocr.runner()
        except (FileNotFoundError, TypeError, KeyError, ValueError) as e:
            print(f'Error: {e}')

    def checkRedundantRows(self):
        pass


if __name__ == '__main__':
    cid = CID()
    cid.runner()
