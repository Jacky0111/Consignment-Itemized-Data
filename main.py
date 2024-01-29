import PySimpleGUI as sg
import PyPDF2


def choose_pdf_file():
    layout = [
        [sg.Text("Choose a PDF file:")],
        [sg.Input(key="file_path", enable_events=True), sg.FileBrowse()],
        [sg.Button("Submit"), sg.Button("Cancel")]
    ]

    window = sg.Window("PDF Page Processor", layout)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == "Cancel":
            window.close()
            return None

        if event == "Submit" and values["file_path"]:
            window.close()
            return values["file_path"]


def choose_page(pdf_path):
    pdf_file = open(pdf_path, "rb")
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    total_pages = len(pdf_reader.pages)

    layout = [
        [sg.Text(f"Choose a page (1 - {total_pages}):")],
        [sg.Input(key="page", enable_events=True)],
        [sg.Button("Submit"), sg.Button("Cancel")]
    ]

    window = sg.Window("PDF Page Processor", layout)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == "Cancel":
            window.close()
            return None

        if event == "Submit" and values["page"].isdigit():
            page_number = int(values["page"])
            if 1 <= page_number <= total_pages:
                window.close()
                return page_number

    pdf_file.close()


def process_page(pdf_path, page_number):
    pdf_file = open(pdf_path, "rb")
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    page = pdf_reader.pages[page_number - 1]
    text = page.extract_text()
    pdf_file.close()

    # Now you can do something with the extracted text, for example, print it
    print(text)


def main():
    pdf_path = choose_pdf_file()

    if pdf_path:
        page_number = choose_page(pdf_path)

        if page_number:
            process_page(pdf_path, page_number)


if __name__ == "__main__":
    main()
