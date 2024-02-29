import os

def rename_files_in_path(path, new_prefix):
    # Change the current working directory to the specified path
    os.chdir(path)

    # Get a list of all files in the directory
    files = os.listdir()

    # Rename each file in the directory
    for old_name in files:
        # Check if the file name ends with "_KPJ"
        if old_name.endswith("_KPJ.pdf"):
            # Construct the new file name without the "_KPJ" suffix
            new_name = old_name[:-8] + ".pdf"

            # Rename the file
            os.rename(old_name, new_name)
            print(f"Renamed: {old_name} to {new_name}")


if __name__ == "__main__":
    # Specify the path to the directory containing the files
    directory_path = "C:\Bill"

    # Specify the new prefix for the files
    new_prefix = "new_prefix"

    # Call the function to rename files in the specified path
    rename_files_in_path(directory_path, new_prefix)
