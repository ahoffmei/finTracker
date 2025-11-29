import os
import sys 
import platform
from pathlib import Path


def get_documents_folder(): 
    home    = Path.home() 
    system  = platform.system().lower()

    if os.name == "nt": # Windows 
        docs = os.path.join(os.environ.get("USERPROFILE", home), "Documents")
    elif system == "darwin" or system == "linux": # macOS / Linux 
        docs = os.path.join(home, "Documents")
    else: 
        raise NotImplementedError(f"Documents folder not supported for OS: {system}")

    return Path(docs)


CATEGORIZATION_DB_PATH = Path( os.path.join(get_documents_folder(), "LocalFinDb") )
FIN_DB_PATH            = Path( os.path.join(get_documents_folder(), "LocalFinDb") )