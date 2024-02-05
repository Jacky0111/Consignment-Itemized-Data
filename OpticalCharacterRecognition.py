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

    '''
    '--oem 3' uses default LSTM OCR engine mode.
    '--psm 4' represents the Page Segmentation Mode and 4 assumes a single column of text.
    '''
    def runner(self):
        # Loop through all images
        for idx, file in enumerate(os.listdir(self.images_path)):
            # Construct the full path of the current image file
            img_path = os.path.join(self.images_path, file)
            img = cv2.imread(img_path)

            # Process the image using the imageToData method
            temp_df = self.imageToData(img)
            temp_df = temp_df.sort_values(by='left', ascending=True)

            # Additional step to check whether the header is correct detected
            if idx == 0:
                temp_df = self.checkHospital(temp_df)

            # Concatenate the data to the final DataFrame
            self.df = pd.concat([self.df, temp_df], ignore_index=True)

            # Draw bounding boxes on the image
            self.drawBoundingBox(img, temp_df)
            cv2.imwrite(self.images_path + f'/bbox_{file}', img)

            bill_list = self.bill.assignCoordinate(temp_df)

            # Store the bill in tabular format
            tr = TabularRule(bill_list, True if idx == 0 else False)
            tr.runner()
            self.table_data_list.append(tr.row_list)

        # Use list comprehension to create tb_list in a more concise way
        tb_list = [[element.text for element in row] for row in self.table_data_list]
        itemized_data = pd.DataFrame(tb_list[1:], columns=tb_list[0])

        self.saveToExcel(self.df, 'image_to_data')
        self.saveToExcel(itemized_data, 'itemized_data')

    '''
    Saved recognized text to csv file
    @param path
    '''
    def saveToCSV(self, data, name):
        data.to_csv(f'{self.output_path}/{name}.csv', index=False)

    '''
    Saved recognized text to xlsx file
    @param path
    '''
    def saveToExcel(self, data, name):
        data.to_excel(f'{self.output_path}/{name}.xlsx', index=False)

    '''
    Perform image_to_data using PaddleOCR and store the data into DataFrame
    @param img
    @param config
    @return data, df
    '''
    @staticmethod
    def imageToData(img):
        paddle = PaddleOCR(use_angle_cls=True, lang='en')
        result = paddle.ocr(img, cls=True)

        # Extract information from the result
        lines = []
        for line in result:
            if line is None:
                continue
            else:
                for word_info in line:
                    coordinates = word_info[0]
                    x_values, y_values = zip(*coordinates)

                    left, top, right, bottom = min(x_values), min(y_values), max(x_values), max(y_values)
                    width, height = right - left, bottom - top

                    text = word_info[1][0]
                    conf = f"{word_info[1][1]:.4f}"

                    # Write a row to the CSV file
                    lines.append([left, top, width, height, conf, text])

        columns = ['left', 'top', 'width', 'height', 'conf', 'text']
        df = pd.DataFrame(lines, columns=columns)

        return df

    '''
    Draw the bounding box based on the coordinate from pytesseract image to data
    @param img
    @param boxes
    '''

    @staticmethod
    def drawBoundingBox(img, boxes):
        red = (0, 0, 255)
        font = cv2.FONT_HERSHEY_SIMPLEX

        for i, box in boxes.iterrows():
            x, y, w, h = int(box[0]), int(box[1]), int(box[2]), int(box[3])
            cv2.rectangle(img, (x, y), (w + x, h + y), red, 1)
            text = f"{box['text']} {i}"
            cv2.putText(img, text, (x, y), font, 0.5, red, 1)

    '''
    Check whether the confidence scores of the image is high enough in order to determine native and non-native pdf
    @param df
    '''
    @staticmethod
    def checkConfidenceScore(df):
        df_conf = df.loc[(df['conf'] > 0) & (df['conf'] <= 70)]

        try:
            prob = df_conf.shape[0] / df.shape[0]
            print(f'{df_conf.shape[0]} / {df.shape[0]} = {prob}')
            return True if prob > 0.3 else False
        except ZeroDivisionError:
            print(f'{df_conf.shape[0]} / {df.shape[0]} = ALL PASS')

    def checkHospital(self, data):
        if self.code == 'BAGAN':
            return OCR.BAGANAdjustment(data)
        elif self.code == 'GNC':
            return OCR.GNCAdjustment(data)
        elif self.code == 'KPJ':
            return OCR.KPJAdjustment(data)
        elif self.code == 'RSH':
            return OCR.RSHAdjustment(data)

    @staticmethod
    def BAGANAdjustment(data):
        return

    @staticmethod
    def GNCAdjustment(data):
        return

    @staticmethod
    def KPJAdjustment(data):
        first_column = {'left': 0, 'top': data['top'][0], 'width': 0, 'height': 0, 'conf': 0, 'text': 'ITEM'}
        # Insert the new row at the beginning of the DataFrame
        data = pd.concat([pd.DataFrame(first_column, index=[0]), data]).reset_index(drop=True)

        return data

    @staticmethod
    def RSHAdjustment(data):
        return



