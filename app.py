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
    pdf_path = None
    uploaded_files = None

    def __init__(self):
        App.header()
        self.uploadFile()

    def runner(self):
        if hasattr(self, 'uploaded_files') and self.uploaded_files:
            for file in self.uploaded_files:
                # Save the uploaded PDF file to a temporary location
                self.pdf_path = f'data/temp/{file.name}'

                try:
                    with open(self.pdf_path, "wb") as f:
                        f.write(file.read())
                    st.write('Reading')
                except (FileNotFoundError, FileExistsError):
                    os.makedirs('data/temp/', exist_ok=True)

            # Cleanup: Remove the temporary PDF file
            # os.remove(self.pdf_path)

            #     # Convert PDF to images using pdf2image
            #     images = self.pdf_to_images(pdf_path)
            #
            #     # Cleanup: Remove the temporary PDF file
            #     os.remove(pdf_path)
            #
            # pdf_path = "temp.pdf"
            # with open(pdf_path, "wb") as f:
            #     f.write(self.uploaded_file.read())

            # Convert PDF to images using pdf2image
            # images = self.pdf_to_images(pdf_path)
            #
            # # Cleanup: Remove the temporary PDF file
            # os.remove(pdf_path)
            #
            # # for img in selected_images:
            #     cid = CID(img)

    '''
    Set the title and page configuration for wider layout
    '''
    @staticmethod
    def header():
        st.write('# Consignment Itemized Data')

    '''
    Upload pdf file
    '''
    def uploadFile(self):
        self.uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)
        print(f'self.uploaded_files: {self.uploaded_files}')

    '''
    Convert PDF to images using pdf2image
    '''
    @staticmethod
    def pdf_to_images(pdf_path):
        images = convert_from_path(pdf_path)
        return images


if __name__ == '__main__':
    if runtime.exists():
        # If the runtime environment exists, create a Deployment object and start the runner
        dep = App()
        dep.runner()
    else:
        # If the runtime environment doesn't exist, start the Streamlit application
        sys.argv = ['streamlit', 'run', 'app.py']
        sys.exit(stcli.main())

# This code checks for the presence of a specific runtime environment and launches a Streamlit application if the
# environment doesn't exist. The 'runtime' object is used to check for the environment, and the 'exists()' function
# returns True if the environment is present and False otherwise. If the environment exists, a Deployment object is
# created and its 'runner()' method is called. Otherwise, the Streamlit application is started using the 'sys.argv' and
# 'stcli.main()' functions.

