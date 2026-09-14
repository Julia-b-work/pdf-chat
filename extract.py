from pypdf import PdfReader
reader = PdfReader ("PC_AULA5.pdf")
print(f"{len(reader.pages)} pages\n")

for i, page in enumerate(reader.pages):
    text = page.extract_text()
    print(f"--- page {i + 1} ---")
    print(text)

