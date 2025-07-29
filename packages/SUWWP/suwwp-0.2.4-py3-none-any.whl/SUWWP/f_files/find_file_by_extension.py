import os
from typing import List

def find_files_by_extension(directory: str, extension: str, recursive: bool = True, 
                          case_sensitive: bool = False) -> List[str]:
    if not os.path.isdir(directory):
        raise ValueError(f"Директория не существует или не является папкой: {directory}")
    if not extension.startswith('.'):
        extension = f'.{extension}'
    
    if not case_sensitive:
        extension = extension.lower()
    
    found_files = []
    
    if recursive:
        for root, _, files in os.walk(directory):
            for file in files:
                file_ext = os.path.splitext(file)[1]
                if not case_sensitive:
                    file_ext = file_ext.lower()
                if file_ext == extension:
                    found_files.append(os.path.join(root, file))
    else:
        for item in os.listdir(directory):
            full_path = os.path.join(directory, item)
            if os.path.isfile(full_path):
                file_ext = os.path.splitext(item)[1]
                if not case_sensitive:
                    file_ext = file_ext.lower()
                if file_ext == extension:
                    found_files.append(full_path)
    
    return found_files

print(*find_files_by_extension("."), sep="\n")