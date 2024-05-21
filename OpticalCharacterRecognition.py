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
    claim_no = None
    output_path = None  # Current save path
    images_path = None  # Input images path

    df = pd.DataFrame()

    cols = []
    table_data_list = []

    def __init__(self, output_path, images_path, claim_no):
        self.bill = Bill()
        self.table_data_list.clear()
        self.claim_no = claim_no
        self.output_path = output_path
        self.images_path = images_path

        # print(f'self.output_path: {self.output_path}')

    '''
    '--oem 3' uses default LSTM OCR engine mode.
    '--psm 4' represents the Page Segmentation Mode and 4 assumes a single column of text.
    '''

    def runner(self):
        print(f'self.images_path: {self.images_path}')
        print(f'self.claim_no: {self.claim_no}')
        print()
        print()
        t1 = 0
        t2 = 0
        t3 = 0
        status = True
        cols_name = None
        img_file_list = []

        for img_file in os.listdir(self.images_path):
            if not img_file.startswith('._'):
                img_file_list.append(img_file)

        img_file_list = sorted(img_file_list, key=OCR.extract_numbers)

        # Loop through all images
        for idx, file in enumerate(img_file_list):
            print(idx + 1, file)
            # Construct the full path of the current image file
            img_path = os.path.join(self.images_path, file)
            print(f'file: {file}')
            print(f'self.images_path: {self.images_path}')
            print(f'img_path: {img_path}')
            img = cv2.imread(img_path)
            print(f'img_path: {type(img_path)}')

            # Process the image using the imageToData method
            temp_df = self.imageToData(img)
            temp_df = temp_df.sort_values(by='left', ascending=True)

            # Additional step to check whether the header is correct detected
            if idx == 0:
                status = False
                if temp_df.empty:
                    continue

                t1 = temp_df[-3:]
                print(t1)
                print('t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1t1')
                continue

            elif idx == 1:
                t2 = temp_df.iloc[:3]
                t2 = pd.concat([t2.iloc[:1], t2]).reset_index(drop=True)
                print(t2)

                # Amend the 'width' column of the second row and assign the same value to the first row's 'width' column
                t2.loc[1, 'width'] /= 2
                t2.loc[0, 'width'] = t2.loc[1, 'width']
                t2.loc[0, 'left'] = 0
                t2.loc[1, 'left'] = t2.loc[1, 'width'] + 41

                print(t2)
                print('t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2t2')

                t3 = pd.concat([t2, t1]).reset_index(drop=True)
                print(t3)
                print('t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3')

                if t3.shape[0] != 7:
                    t2.loc[4, 'left'] = 0
                    t3.loc[4, 'width'] /= 3

                    # Calculate new row data
                    x1 = t3.loc[4, 'left'] + t3.loc[4, 'width'] + 41
                    w1 = t3.loc[4, 'width'] * 2 - 41

                    new_row_data = {'left': x1, 'top': t3.loc[4, 'top'], 'width': w1,
                                    'height': t3.loc[4, 'height'], 'conf': t3.loc[4, 'conf'], 'text': ''}
                    new_row_df = pd.DataFrame(new_row_data, index=[0])

                    # Get the index where you want to insert the row
                    insert_index = len(t3) - 1

                    # Split the DataFrame into two parts: before and after the insert index
                    t3_before = t3.iloc[:insert_index]
                    t3_after = t3.iloc[insert_index:]

                    # Concatenate the two parts along with the new row
                    t3 = pd.concat([t3_before, new_row_df, t3_after], ignore_index=True)

                    print(t3)
                    print('t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3t3')

                cols_name, temp_df = self.checkHospital(t3.iloc[:, :-1])
            else:
                try:
                    # Apply the function to each text in the DataFrame
                    temp_df['most_similar_header'], temp_df['similarity_score'] = zip(
                        *temp_df['text'].apply(OCR.find_most_similar_header_and_similarity, header_name=cols_name))
                except ValueError:
                    continue

                # Filter rows with similarity score less than 50
                temp_df = temp_df[temp_df['similarity_score'] <= 50]

                # Concatenate the data to the final DataFrame
                self.df = pd.concat([self.df, temp_df], ignore_index=True)

            # Draw bounding boxes on the image
            self.drawBoundingBox(img, temp_df)
            cv2.imwrite(self.images_path + f'/bbox_{file}', img)

            bill_list = self.bill.assignCoordinate(temp_df)
            for bill in bill_list:
                print(f'{idx}. bill_list: {bill}')

            # Store the bill in tabular format
            tr = TabularRule(bill_list, True if idx == 1 else False)
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
        print(f'tb_list: \t{tb_list}')

        print(f'self.cols[0]: {self.cols[0]}')

        try:
            itemized_data = pd.DataFrame(tb_list[1:], columns=self.cols[0])
        except ValueError as e:
            print(f"ValueError occurred: {e}")
            numbers = re.findall(r'\d+', str(e))
            print(f'numbers: {numbers}')

            if numbers[0] > numbers[1]:
                print(f'numbers[0] > numbers[1]: {numbers[0] > numbers[1]}')
                num_columns_in_data = len(tb_list[0])
                print(f'num_columns: {num_columns_in_data}')
                max_columns = len(tb_list[1])
                print(f'max_columns_in_data: {max_columns}')
                # If the number of columns in headers is less than the number of columns in any data row, add None or ''
                print(f'Before: {tb_list[1]}')
                tb_list[1].extend([None] * (num_columns_in_data - max_columns))

            elif numbers[0] < numbers[1]:
                print(f'numbers[1] > numbers[0]: {numbers[1] > numbers[0]}')
                num_columns = len(tb_list[0])
                print(f'num_columns: {num_columns}')
                max_columns_in_data = max(len(row) for row in tb_list[1:])
                print(f'max_columns_in_data: {max_columns_in_data}')
                # If the number of columns in headers is less than the number of columns in any data row, add None or ''
                print(f'Before: {tb_list[0]}')
                tb_list[0].extend([None] * (max_columns_in_data - num_columns))

        # Print adjusted columns to check
        print("Adjusted Columns:", tb_list[0])
        # Convert data to DataFrame
        itemized_data = pd.DataFrame(tb_list[1:], columns=tb_list[0])
        itemized_data.insert(0, 'ClaimNo', self.claim_no * len(itemized_data))
        print(f'self.claim_no: {self.claim_no}')

        df_temp = pd.read_excel(r'claim_data.xlsx')
        # Get the PolicyNo from the matching row
        # Find the row where ClaimNo is equal to 'ALMCIP02180441'
        matching_row = df_temp[df_temp['ClaimNo'] == self.claim_no[0]]
        # Get the PolicyNo from the matching row
        policy_number = matching_row['PolicyNo'].iloc[0] if not matching_row.empty else None
        print(f'Type: {type(policy_number)}')

        self.saveToExcel(self.df, 'image_to_data')

        itemized_data.insert(0, 'PolicyNo', policy_number)

        # self.saveToExcel(itemized_data, 'itemized_data')

        self.saveToCSV(itemized_data, 'itemized_data')

    '''
    Saved recognized text to csv file
    @param path
    '''

    def saveToCSV(self, data, name):
        print(f'{self.output_path}/{name}.csv')
        data.to_csv(f'{self.output_path}/{name}.csv', index=False)

    '''
    Saved recognized text to xlsx file
    @param path
    '''

    def saveToExcel(self, data, name):
        print(f'{self.output_path}/{name}.xlsx')
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
        header_name = ['Price Code',
                       'Description',
                       'Trans Date',
                       'Qty',
                       'Amount (RM)',
                       'GST/Tax Amount (RM)',
                       'Payable Amt (RM)']

        # Insert the new row at the beginning of the DataFrame
        text_col = pd.DataFrame(header_name, columns=['text'])

        data = pd.concat([data, text_col], axis=1)
        print(data)

        return header_name, data

    @staticmethod
    def RSHAdjustment(data):
        return

    @staticmethod
    # Function to extract numbers and convert to a tuple of integers for sorting
    def extract_numbers(s):
        match = re.search(r'row_(\d+)_(\d+).png', s)
        if match:
            return int(match.group(1)), int(match.group(2))
        return 0, 0  # Default value in case of no match
