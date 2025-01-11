import os
import sys

def get_resource_path(relative_path):
    """Obtém o caminho correto para o arquivo, seja em desenvolvimento ou no executável."""
    if hasattr(sys, '_MEIPASS'):
        # Quando executado como um executável
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        # Durante o desenvolvimento
        return os.path.join(os.path.abspath("."), relative_path)