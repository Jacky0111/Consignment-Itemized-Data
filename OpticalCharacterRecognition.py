import os
import cv2
import pandas as pd
from paddleocr import PaddleOCR

from Bill import Bill
from TabularRule import TabularRule


class OCR:
    bill = None
    code = None
    output_path = None  # Current save path
    images_path = None  # Input images path
    is_non_native = False

    counter = 0
    df = pd.DataFrame()
    table_data_list = []
    data_coordinate_list = []

    def __init__(self, code, output_path, images_path):
        self.bill = Bill()
        self.code = code
        self.table_data_list.clear()
        self.output_path = output_path
        self.images_path = images_path
