from PyPDF2 import PdfReader
from app.utils.resume_analysis_utils import analyze_with_gemini
import io


async def analyze_resume_service(file_contents: bytes, filename: str) -> dict:
    """
    Service para análise de currículo
    """
    # Lê e extrai texto do PDF
    if len(file_contents) == 0:
        raise ValueError("O arquivo está vazio")

    pdf_file = io.BytesIO(file_contents)
    reader = PdfReader(pdf_file)

    if reader.is_encrypted:
        raise ValueError("PDF criptografado não é suportado")

    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    if not text.strip():
        raise ValueError("Nenhum texto foi encontrado no PDF")

    # Analisa o currículo com Gemini
    analysis_result = await analyze_with_gemini(text)

    return {
        "filename": filename,
        "total_pages": len(reader.pages),
        "analysis": analysis_result,
    }
