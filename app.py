import os
import sys
import pandas as pd
from PIL import Image
import streamlit as st
from streamlit import runtime
from streamlit.web import cli as stcli
from pdf2image import convert_from_path

from ConsignmentItemizedData import CID

st.set_page_config(layout="wide")
pd.set_option('display.max_columns', None)


class App:
    uploaded_file = None

    def __init__(self):
        App.header()
        self.uploadFile()

    def runner(self):
        if self.uploaded_file is not None:
            # Save the uploaded PDF file to a temporary location
            pdf_path = "temp.pdf"
            with open(pdf_path, "wb") as f:
                f.write(self.uploaded_file.read())

            # Convert PDF to images using pdf2image
            images = self.pdf_to_images(pdf_path)


            # Cleanup: Remove the temporary PDF file
            os.remove(pdf_path)

            # for img in selected_images:
            #     cid = CID(img)

    '''
    Set the title and page configuration for wider layout
    '''
    @staticmethod
    def header():
        st.write('# PDF Viewer with Streamlit')

    '''
    Upload pdf file
    '''
    def uploadFile(self):
        self.uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
        print(f'self.uploaded_file: {self.uploaded_file}')

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

