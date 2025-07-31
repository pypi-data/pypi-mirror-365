"""FSQ miscellaneous variables and functions."""

import random
import string
from .api import FsqStorageDest

DEST_CHOICES = {
    'null': FsqStorageDest.FSQ_STORAGE_NULL,
    'local': FsqStorageDest.FSQ_STORAGE_LOCAL,
    'lustre': FsqStorageDest.FSQ_STORAGE_LUSTRE,
    'tsm': FsqStorageDest.FSQ_STORAGE_TSM,
    'lustre_tsm': FsqStorageDest.FSQ_STORAGE_LUSTRE_TSM,
}

def generate_random_str(length: int=32) -> str:
    """Generate random string of letters and digits."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
