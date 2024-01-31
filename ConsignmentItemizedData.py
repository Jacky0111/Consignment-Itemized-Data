# Empowers the end user to make choices between performing document conversion and optical character recognition (OCR)

import os
import cv2
import shutil
from datetime import datetime
from paddleocr import PaddleOCR

# from Detect import Detect
# from OpticalCharacterRecognition import OCR


class CID:
    def __init__(self, images):
        for img in images:
            paddle = PaddleOCR(use_angle_cls=True, lang='en')
            result = paddle.ocr(img, cls=True)
            print('ssssssssssssssssssssssssssssssssssssssssss')
            # for idx in range(len(result)):
            #     res = result[idx]
            #     for line in res:
            #         print(line)

