from mjkit.utiles import get_logger
import logging

def save_text_to_file(
    text: str,
    save_path: str = "ownership_report.txt"
) -> None:
    """
    주어진 텍스트를 지정된 경로에 파일로 저장합니다.

    이 함수는 UTF-8 인코딩으로 파일을 저장하며,
    파일 저장 중 오류가 발생하면 로깅을 통해 예외 정보를 출력합니다.

    Args:
        text (str): 저장할 텍스트 문자열
        save_path (str): 저장할 파일 경로 및 이름 (기본값: 'ownership_report.txt')

    Returns:
        None

    Raises:
        IOError: 파일 저장에 실패한 경우

    Example:
        >>> text = "제넥신\\n  - 네오이뮨텍: 21.18%"
        >>> save_text_to_file(text, "output.txt")
        ✅ 텍스트 파일이 저장되었습니다: output.txt
    """
    logger = get_logger(__name__, level=logging.INFO)
    try:
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(text)
        logger.info(f"✅ 텍스트 파일이 저장되었습니다: {save_path}")
    except Exception as e:

        logger.exception(f"❌ 텍스트 저장 중 오류 발생: {save_path}, {e}")
