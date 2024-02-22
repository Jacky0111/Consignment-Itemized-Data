import os
import shutil
import pandas as pd


# Step 1: Get the list of file names in the given path
def get_file_names(directory_path):
    files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    return [os.path.splitext(f)[0] for f in files]


# Step 2: Read "KPJ" sheet from Excel file into a pandas DataFrame
def read_excel_to_dataframe(excel_file_path, code):
    df = pd.read_excel(excel_file_path, sheet_name=code)
    return df


# Step 3: Remove "-2" suffix from file names
def remove_suffix(file_names):
    return [name[:-2] if name.endswith('_2') else name for name in file_names]


# Step 4: Filter DataFrame based on conditions
def filter_dataframe(df, file_names):
    filtered_list = []
    for file_name in file_names:
        if file_name in df['ClaimNo'].values:
            filtered_list.append(file_name)
    return filtered_list


# Step 5: Rename PDF files with "_KPJ" suffix
def rename_pdf_files(directory_path, filtered_list, code):
    for file_name in filtered_list:
        old_path = os.path.join(directory_path, file_name + ".pdf")
        new_path = os.path.join(directory_path, file_name + f'_{code}.pdf')
        try:
            os.rename(old_path, new_path)
        except FileNotFoundError:
            old_path = os.path.join(directory_path, file_name + "_2.pdf")
            os.rename(old_path, new_path)


# Step 6: Copy selected PDF files to "KPJ" folder
def copy_to_kpj_folder(directory_path, filtered_list, code):
    kpj_folder = os.path.join(directory_path, code)
    os.makedirs(kpj_folder, exist_ok=True)

    for file_name in filtered_list:
        source_path = os.path.join(directory_path, file_name + f'_{code}.pdf')
        dest_path = os.path.join(kpj_folder, file_name + f'_{code}.pdf')
        shutil.copy(source_path, dest_path)


# Step 5: Delete files that are not in the DataFrame
def delete_files_not_in_dataframe(directory_path, file_names, filtered_list):
    files_to_delete = set(file_names) - set(filtered_list)
    for file_name in files_to_delete:
        file_path = os.path.join(directory_path, file_name + ".pdf")
        try:
            os.remove(file_path)
            print(f"File deleted: {file_path}")
        except FileNotFoundError:
            print(f"File not found: {file_path}")


# Example usage
if __name__ == "__main__":
    hosp_code = ['KPJ', 'GLE', 'PAN', 'ANS']
    # Provide the file path
    directory_path = 'D:/Bill'
    excel_file_path = 'C:/Users/ChiaChungLim/Downloads/claim_data.xlsx'

    # Step 1: Get the list of file names
    file_names = get_file_names(directory_path)
    # print(f'len(file_names): {len(file_names)}')
    # print(f'file_names: {file_names}')

    # Step 2: Read "KPJ" sheet from Excel file into DataFrame
    df = read_excel_to_dataframe(excel_file_path, hosp_code[0])

    # Step 3: Remove "-2" suffix from file names
    file_names = remove_suffix(file_names)

    # Step 4: Filter DataFrame based on conditions
    filtered_list = filter_dataframe(df, file_names)

    # Print the result
    print("Filtered List:", filtered_list)

    # Step 5: Rename PDF files with "_KPJ" suffix
    rename_pdf_files(directory_path, filtered_list, hosp_code[0])

    # Step 6: Copy selected PDF files to "KPJ" folder
    copy_to_kpj_folder(directory_path, filtered_list, hosp_code[0])

    # Step 5: Delete files that are not in the DataFrame
    # delete_files_not_in_dataframe(directory_path, file_names, filtered_list)

