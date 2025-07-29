'''
IMPORTS
'''
from .f_randoms.random_copy import (
    random_copy
    )

from .f_time.time_now import (
    time_now
    )

from .f_directories.structure_project import (
    structure_project
    )

from .f_files.file_read import (
    file_read, write_file,
    find_file_by_extension
    )


'''
ALIAS
'''
fr = file_read
wr = write_file
fbe = find_file_by_extension
sp = structure_project
tn = time_now 
rc = random_copy


__all__ = ["file_read", "fr", "structure_project", "sp", "time_now", "tn", "random_copy", "rc", "write_file", "wf", "find_file_by_extension", "fbe"]


__version__ = "0.2.4"

#Create by Xwared Team