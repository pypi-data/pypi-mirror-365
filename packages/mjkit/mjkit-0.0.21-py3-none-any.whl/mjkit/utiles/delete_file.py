import os
from mjkit.utiles import get_logger
import logging

def delete_file(path: str):
    """
    지정된 파일을 삭제합니다.

    Args:
        path (str): 삭제할 파일 경로
    """
    try:
        os.remove(path)
    except Exception as e:
        logger = get_logger(__name__, level=logging.WARNING)
        logger.warning(f"[Warning] Failed to delete file {path}: {e}")