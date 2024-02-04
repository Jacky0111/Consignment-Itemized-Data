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

    # def __init__(self, images):

        # for img in images:
        #     text = pytesseract.image_to_string(img, config=r'--oem 3 --psm 4 -l eng')
        #     print(text)
        #     print('')

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


