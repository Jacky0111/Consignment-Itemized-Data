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
    uploaded_files = None

    def __init__(self):
        pass

    '''
    Set the title and page configuration for wider layout
    '''
    def header(self):
        st.write('# Consignment Itemized Data')

    '''
    Upload pdf file
    '''
    def uploadFile(self):
        pass



    

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
