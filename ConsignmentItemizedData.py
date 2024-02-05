# Empowers the end user to make choices between performing document conversion and optical character recognition (OCR)

import os
import cv2
import shutil
from datetime import datetime
import pytesseract
import numpy as np
from paddleocr import PaddleOCR

# from Detect import Detect
# from OpticalCharacterRecognition import OCR

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class CID:
    images_path = None
    dataset_path = None
    output_folder_path = []

    def __init__(self):
        self.images_path = None
        self.dataset_path = None
        self.output_folder_path.clear()

    def runner(self):
        pass

    '''
    '--oem 3' uses default LSTM OCR engine mode.
    '--psm 4' represents the Page Segmentation Mode and 4 assumes a single column of text.
    '''

    def identifyHospital(self, raw_text):
        pass
        text = pytesseract.image_to_string(img, config=r'--oem 3 --psm 4 -l eng')

    def setFolderPath(self, hosp_code, file_name):
        path = f"output/{hosp_code}_{file_name}_{str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))}"

        CID.createFolder(path)

        self.folder_path = r'/Images/' + Path(dir).stem + '_' + str(
            datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
        self.folder_path = os.getcwd() + self.folder_path
        os.makedirs(self.folder_path)

        parse_url = urlparse(self.url)
        path = r'Screenshots/' + parse_url.netloc + '_' + str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S')) + '/'
        self.file_name = path + parse_url.netloc
        os.makedirs(path)

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

    # for img in images:
    #     text = pytesseract.image_to_string(img, config=r'--oem 3 --psm 4 -l eng')
    #     print(text)
    #     print('')
    #
    # paddle = PaddleOCR(use_angle_cls=True, lang='en')
    # result = paddle.ocr(np.array(img), cls=True)
    # # Extract information from the result
    # text = ''
    # for line in result:
    #     if line is None:
    #         continue
    #     else:
    #         for word_info in line:
    #             text += word_info[1][0] + ' '
    #
    # print(f'text: /n{text}')


if __name__ == '__main__':
    cid = CID()
    cid.runner()
