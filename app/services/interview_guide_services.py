from app.utils.interview_guide_utils import generate_interview_guide_with_gemini
from PyPDF2 import PdfReader
import io


async def generate_interview_guide_service(file_contents: bytes, filename: str, job_description: str) -> dict:
    """
    Service para geração de guia de entrevista
    """
    # Lê e extrai texto do PDF
    if len(file_contents) == 0:
        raise ValueError("O arquivo está vazio")

    pdf_file = io.BytesIO(file_contents)
    reader = PdfReader(pdf_file)

    if reader.is_encrypted:
        raise ValueError("PDF criptografado não é suportado")

    resume_text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            resume_text += page_text + "\n"

    if not resume_text.strip():
        raise ValueError("Nenhum texto foi encontrado no PDF")

    # Gera o guia de entrevista com Gemini
    interview_guide = await generate_interview_guide_with_gemini(resume_text, job_description)

    return {
        "filename": filename,
        "job_description_preview": job_description[:100] + "..." if len(job_description) > 100 else job_description,
        "interview_guide": interview_guide
    }
