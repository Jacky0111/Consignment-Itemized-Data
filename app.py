import os
import sys
import tempfile
import webbrowser
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit import runtime
from streamlit.web import cli as stcli
from pdf2image import convert_from_path

st.set_page_config(layout="wide")
pd.set_option('display.max_columns', None)


class App:
    # df = pd.DataFrame()

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

            # Display selected images in the Streamlit app
            selected_pages = st.multiselect("Select pages to keep", [i + 1 for i in range(len(images))],
                                            default=[i + 1 for i in range(len(images))])

            # Mark selected pages in the backend
            print("Selected pages:", selected_pages)

            # Remove unselected pages
            self.remove_unselected_images("output_images", selected_pages)

            # Display selected images
            selected_images = [images[i - 1] for i in selected_pages]

            # Sort selected pages in ascending order
            selected_pages.sort()

            # Create placeholder for dynamic update
            st.empty()

            # Display selected images in rows and columns dynamically
            num_columns = 5
            for i in range(0, len(selected_images), num_columns):
                row = st.columns(num_columns)
                for j in range(num_columns):
                    index = i + j
                    if index < len(selected_images):
                        si = selected_images[index]
                        row[j].image(si, caption=[f"Page {selected_pages[index]}"])

            # Cleanup: Remove the temporary PDF file
            os.remove(pdf_path)

    '''
    Set the title and page configuration for wider layout
    '''
    @staticmethod
    def header():
        # st.set_page_config(page_title="PDF Viewer with Streamlit", layout="wide")
        st.write('# PDF Viewer with Streamlit')

    '''
    Upload pdf file
    '''
    def uploadFile(self):
        self.uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

    '''
    Convert PDF to images using pdf2image
    '''
    @staticmethod
    def pdf_to_images(pdf_path):
        images = convert_from_path(pdf_path)
        return images

    '''
    Remove unselected pages
    '''
    @staticmethod
    def remove_unselected_images(output_folder, selected_pages):
        for i in range(1, len(selected_pages) + 1):
            image_path = os.path.join(output_folder, f"output_image-{i}.png")
            if i not in selected_pages and os.path.exists(image_path):
                os.remove(image_path)


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

