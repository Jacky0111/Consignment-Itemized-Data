# Empowers the end user to make choices between performing document conversion and optical character recognition (OCR)

import os
import cv2
import shutil
from datetime import datetime

import numpy as np
from paddleocr import PaddleOCR

# from Detect import Detect
# from OpticalCharacterRecognition import OCR


class CID:
    def __init__(self, images):
        for img in images:
            paddle = PaddleOCR(use_angle_cls=True, lang='en')
            result = paddle.ocr(np.array(img), cls=True)
            # Extract information from the result
            text = ''
            for line in result:
                if line is None:
                    continue
                else:
                    for word_info in line:
                        text += word_info[1][0] + ' '

            print(f'text: /n{text}')


