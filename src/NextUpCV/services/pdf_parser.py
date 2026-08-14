import io
from nextupcv.utilities.cleaner import clean_text, extract_contact_info
from pypdf import PdfReader

class ResumeParserService:
    @staticmethod
    def extract_text_from_bytes(file_bytes: bytes) -> str:
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text.strip()

# class ResumeParserService:
#     """
#     Extracts raw text content and contact information from binary PDF uploads.
#     """

#     def extract_raw_text(self, pdf_bytes: bytes) -> str:
#         extracted_pages = []
#         with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
#             for page in pdf.pages:
#                 text = page.extract_text(layout=False)
#                 if text:
#                     extracted_pages.append(text)
#         return "\n".join(extracted_pages)

#     def parse_resume(self, pdf_bytes: bytes) -> dict:
#         raw_text = self.extract_raw_text(pdf_bytes)

#         if not raw_text.strip():
#             return {"error": "Scanned or non-selectable image PDF detected."}

#         cleaned = clean_text(raw_text)
#         contact_details = extract_contact_info(raw_text)

#         return {"raw_text": cleaned, "contact_info": contact_details}
