import os
import re
import cv2
import pandas as pd
from fuzzywuzzy import fuzz
from paddleocr import PaddleOCR

from Bill import Bill
from TabularRule import TabularRule


class OCR:
    bill = None
    output_path = None  # Current save path
    images_path = None  # Input images path

    counter = 0
    df = pd.DataFrame()

    cols = []
    table_data_list = []

    def __init__(self, output_path, images_path):
        self.bill = Bill()
        self.table_data_list.clear()
        self.output_path = output_path
        self.images_path = images_path

    '''
    '--oem 3' uses default LSTM OCR engine mode.
    '--psm 4' represents the Page Segmentation Mode and 4 assumes a single column of text.
    '''
    def runner(self):
        t1 = 0
        t2 = 0
        t3 = 0

        # Loop through all images
        for idx, file in enumerate(os.listdir(self.images_path)):
            # Construct the full path of the current image file
            img_path = os.path.join(self.images_path, file)
            print(f'img_path: {img_path}')
            img = cv2.imread(img_path)

            # Process the image using the imageToData method
            temp_df = self.imageToData(img)
            temp_df = temp_df.sort_values(by='left', ascending=True)

            # Additional step to check whether the header is correct detected
            if idx == 0:
                t1 = temp_df
                print(t1)
                print('t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1')
                continue
            elif idx == 1:
                t2 = temp_df.iloc[:3]
                t2 = pd.concat([t2.iloc[:1], t2]).reset_index(drop=True)

                # Amend the 'width' column of the second row and assign the same value to the first row's 'width' column
                t2.loc[1, 'width'] /= 2
                t2.loc[0, 'width'] = t2.loc[1, 'width']
                t2.loc[1, 'left'] = t2.loc[1, 'width'] + 41

                print(t2)
                print('t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2')

                t3 = pd.concat([t2, t1]).reset_index(drop=True)
                print(t3)
                print('t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3')

                cols_name, temp_df = self.checkHospital(t3.iloc[:, :-1])
            else:
                print(f'temp_df (Before): {temp_df}')
                # Apply the function to each text in the DataFrame
                temp_df['most_similar_header'], temp_df['similarity_score'] = zip(
                    *temp_df['text'].apply(OCR.find_most_similar_header_and_similarity, header_name=cols_name))

                print(f'temp_df (Middle): {temp_df}')

                # Filter rows with similarity score less than 50
                temp_df = temp_df[temp_df['similarity_score'] < 50]

                print(f'temp_df (After): {temp_df}')

                # # Apply the function to each row in the DataFrame
                # temp_df['similarity_ratio'] = temp_df.apply(
                #     lambda row: OCR.check_similarity(row['text'], row['most_similar_header'] or ''), axis=1)
                #
                # temp_df = temp_df[temp_df['similarity_ratio'] > 0]

                # Concatenate the data to the final DataFrame
                self.df = pd.concat([self.df, temp_df], ignore_index=True)


            # Draw bounding boxes on the image
            self.drawBoundingBox(img, temp_df)
            cv2.imwrite(self.images_path + f'/bbox_{file}', img)

            bill_list = self.bill.assignCoordinate(temp_df)
            for bill in bill_list:
                print(f'bill_list: {bill}')

            # Store the bill in tabular format
            tr = TabularRule(bill_list, True if idx == 0 else False)
            tr.runner()
            self.table_data_list.append(tr.row_list)

        # Use list comprehension to create tb_list in a more concise way
        tb_list = [[element.text for element in row] for row in self.table_data_list]

        self.cols.append(tb_list[0])

        # Define a regular expression pattern to match the date in the format DD/MM/YYYY
        date_pattern = r'\b\d{2}/\d{2}/\d{4}\b'
        # Iterate over each sublist in the 2D input list
        for sublist in tb_list:
            try:
                # Extract the sentence from the second element of the sublist
                sentence = sublist[1]
            except IndexError:
                continue

            # Use findall to extract all occurrences of the date pattern from the sentence
            dates = re.findall(date_pattern, sentence)
            # If dates are found, take the first one and remove it from the sentence
            if dates:
                date = dates[0]
                # Remove the date from the sentence
                sentence = re.sub(date_pattern, '', sentence)

                # Add the date to the sublist
                del sublist[1]
                sublist.insert(1, date)
                sublist.insert(1, sentence)
                # Print the sublist elements separated by commas

        print()
        print(f'tb_list: {tb_list}')

        itemized_data = pd.DataFrame(tb_list[1:], columns=self.cols[0])

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
        # paddle = PaddleOCR(use_angle_cls=True, lang='en')
        paddle = PaddleOCR(det_algorithm='DB', det_db_box_thresh=0.3, det_db_unclip_ratio=2.0)
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

    # Function to calculate Levenshtein distance
    @staticmethod
    def levenshtein_distance(s1, s2):
        if len(s1) > len(s2):
            s1, s2 = s2, s1

        distances = range(len(s1) + 1)
        for i2, c2 in enumerate(s2):
            distances_ = [i2 + 1]
            for i1, c1 in enumerate(s1):
                if c1 == c2:
                    distances_.append(distances[i1])
                else:
                    distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
            distances = distances_
        return distances[-1]

    # Function to check similarity using Levenshtein distance
    @staticmethod
    def check_similarity(text, header):
        # Calculate Levenshtein distance between lowercase versions of text and header
        distance = OCR.levenshtein_distance(text.lower(), header.lower())
        # Calculate similarity score as a ratio of distance to maximum length
        similarity_ratio = 1 - (distance / max(len(text), len(header)))
        return similarity_ratio

    # Function to find the most similar header and calculate similarity score using fuzzy matching
    @staticmethod
    def find_most_similar_header_and_similarity(text, header_name):
        max_similarity = 0
        most_similar_header = None
        for header in header_name:
            similarity = fuzz.ratio(text.lower(), header.lower())
            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_header = header
        return most_similar_header, max_similarity

    def checkHospital(self, data):
        # if self.code == 'BAGAN':
        #     return OCR.BAGANAdjustment(data)
        # elif self.code == 'GNC':
        #     return OCR.GNCAdjustment(data)
        # elif self.code == 'KPJ':
        #     return OCR.KPJAdjustment(data)
        # elif self.code == 'RSH':
        #     return OCR.RSHAdjustment(data)

        return OCR.KPJAdjustment(data)

    @staticmethod
    def BAGANAdjustment(data):
        return

    @staticmethod
    def GNCAdjustment(data):
        return

    @staticmethod
    def KPJAdjustment(data):
        header_name = ['Price Code', 'Description', 'Trans Date', 'Qty', 'Amount (RM)', 'GST Amount (RM)', 'Payable Amt (RM)']

        # Insert the new row at the beginning of the DataFrame
        text_col = pd.DataFrame(header_name, columns=['text'])

        data = pd.concat([data, text_col], axis=1)

        print(data)
        print('1111111111111111111111111111111111111111111111111111111')

        return header_name, data

    @staticmethod
    def RSHAdjustment(data):
        return



