import os
import shutil
import pandas as pd


# Step 1: Get the list of file names in the given path
def getFileNames(location):
    files = [f for f in os.listdir(location) if os.path.isfile(os.path.join(location, f))]
    return [os.path.splitext(f)[0] for f in files]


# Step 3: Remove "-2" suffix from file names
def removeSuffix(name_list):
    return [name[:-2] if name.endswith('_2') else name for name in name_list]


# Step 4: Filter DataFrame based on conditions
def filterDataframe(data, name_list):
    filtered = []
    for file_name in name_list:
        if file_name in data['ClaimNo'].values:
            filtered.append(file_name)
    return filtered


# Step 5: Rename PDF files with "_KPJ" suffix
def renameBills(location, filtered, code):
    for file_name in filtered:
        old_path = os.path.join(location, f'{file_name}.pdf')
        new_path = os.path.join(location, f'{file_name}_{code}.pdf')

        # print(f'old_path: {old_path}')
        # print(f'new_path: {new_path}')

        try:
            os.rename(old_path, new_path)
        except FileNotFoundError:
            old_path = os.path.join(location, file_name + "_2.pdf")
            os.rename(old_path, new_path)


# Step 6: Copy selected PDF files to "KPJ" folder
def copyFileToFolder(directory_path, filtered, code):
    kpj_folder = os.path.join(directory_path, code)
    os.makedirs(kpj_folder, exist_ok=True)

    for file_name in filtered:
        source_path = os.path.join(directory_path, f'{file_name}_{code}.pdf')
        destination_path = os.path.join(kpj_folder, f'{file_name}_{code}.pdf')
        shutil.copy(source_path, destination_path)


# Example usage
if __name__ == "__main__":
    hosp_code = ['KPJ', 'GLE', 'PAN', 'ANS']
    # Provide the file path
    path = 'D:/Bill'
    excel_file_path = 'C:/Users/ChiaChungLim/Downloads/claim_data.xlsx'

    # Step 1: Get the list of file names
    file_names = getFileNames(path)

    # Step 2: Read "KPJ" sheet from Excel file into DataFrame
    df = pd.read_excel(excel_file_path, sheet_name=hosp_code[0])

    # Step 3: Remove "-2" suffix from file names
    file_names = removeSuffix(file_names)

    # Step 4: Filter DataFrame based on conditions
    filtered_list = filterDataframe(df, file_names)

    # Print the result
    print(f'Length: {len(filtered_list)}')

    # Step 5: Rename PDF files with "_KPJ" suffix
    renameBills(path, filtered_list, hosp_code[0])

    # Step 6: Copy selected PDF files to "KPJ" folder
    copyFileToFolder(path, filtered_list, hosp_code[0])
