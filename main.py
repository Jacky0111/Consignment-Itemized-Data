import streamlit as st
from pdf2image import convert_from_path
from PIL import Image
import os
import io


def pdf_to_images(pdf_path):
    # Convert PDF to images using pdf2image
    images = convert_from_path(pdf_path)
    return images


def remove_unselected_images(output_folder, selected_pages):
    # Remove unselected pages
    for i in range(1, len(selected_pages) + 1):
        image_path = os.path.join(output_folder, f"output_image-{i}.png")
        if i not in selected_pages and os.path.exists(image_path):
            os.remove(image_path)


def main():
    # Set the page configuration for wider layout
    st.set_page_config(page_title="PDF Viewer with Streamlit", layout="wide")

    # Allow user to select a PDF file
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

    if uploaded_file is not None:
        # Save the uploaded PDF file to a temporary location
        pdf_path = "temp.pdf"
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.read())

        # Convert PDF to images using pdf2image
        images = pdf_to_images(pdf_path)

        # Display selected images in the Streamlit app
        selected_pages = st.multiselect("Select pages to keep", [i + 1 for i in range(len(images))],
                                        default=[i + 1 for i in range(len(images))])

        # Mark selected pages in the backend
        print("Selected pages:", selected_pages)

        # Remove unselected pages
        remove_unselected_images("output_images", selected_pages)

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


if __name__ == "__main__":
    main()
