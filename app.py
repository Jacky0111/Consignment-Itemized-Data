import os
import sys
import pandas as pd
from PIL import Image
from pathlib import Path

import streamlit as st
from streamlit import runtime
from streamlit.web import cli as stcli
from pdf2image import convert_from_path

from ConsignmentItemizedData import CID

st.set_page_config(layout="wide")
pd.set_option('display.max_columns', None)


class App:
    pdf_files = []
    uploaded_files = []
    previous_files = []

    def __init__(self):
        self.header()
        self.uploadFile()
        self.processor()

    '''
    Set the title and page configuration for wider layout
    '''

    def header(self):
        st.write('# Consignment Itemized Data')

    '''
    Upload pdf file
    '''
    def uploadFile(self):
        current_file_len = 0
        previous_file_len = current_file_len if current_file_len != 0 else 0

        self.uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)
        self.pdf_files = [f.name for f in self.uploaded_files]

        print(f'self.pdf_files: {self.pdf_files}')
        print(f'self.previous_files: {self.previous_files}')

        current_file_len = len(self.uploaded_files)

        # balance = current_file_len - previous_file_len
        # if balance > 0:
        #     extra_files = set(self.uploaded_files) ^ set(self.previous_files)
        #
        #     # # Check for removed files
        #     # if self.uploaded_files is not None and self.previous_files:
        #     #     for fp in extra_files:
        #     #         self.deleteLocalFiles(fp)
        #
        # elif balance < 0:
        #     pass

        previous_file_len = current_file_len
        self.previous_files = self.pdf_files
        print(f'self.previous_files: {self.previous_files}')


    def processor(self):
        if hasattr(self, 'uploaded_files') and self.uploaded_files:
            for file in self.uploaded_files:
                # Save the uploaded PDF file to a temporary location
                pdf_path = f'data/temp/{file.name}'

                try:
                    with open(pdf_path, "wb") as f:
                        f.write(file.read())
                    st.success(f"File '{file.name}' has been successfully uploaded.")

                except (FileNotFoundError, FileExistsError):
                    os.makedirs('data/temp/', exist_ok=True)

    @staticmethod
    def deleteLocalFiles(file):
        local_path = f'data/temp/{file.name}'
        st.write(f'local_path: {local_path}')
        if os.path.exists(local_path):
            os.remove(local_path)
            st.warning(f"File '{file.name}' has been deleted from local storage.")


if __name__ == '__main__':
    if runtime.exists():
        # If the runtime environment exists, create a Deployment object and start the runner
        dep = App()

    else:
        # If the runtime environment doesn't exist, start the Streamlit application
        sys.argv = ['streamlit', 'run', 'app.py']
        sys.exit(stcli.main())

# This code checks for the presence of a specific runtime environment and launches a Streamlit application if the
# environment doesn't exist. The 'runtime' object is used to check for the environment, and the 'exists()' function
# returns True if the environment is present and False otherwise. If the environment exists, a Deployment object is
# created and its 'runner()' method is called. Otherwise, the Streamlit application is started using the 'sys.argv' and
# 'stcli.main()' functions.
