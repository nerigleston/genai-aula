from fastapi import UploadFile
import requests
import aiofiles
import PyPDF2
import base64

def pdf_to_text(pdf_file):
    text = ''
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + '\n'
        return text
    except Exception as e:
        return f'Ocorreu um erro: {e}'

def image_to_base64(uploaded_file):
    try:
        if uploaded_file.type not in ["image/jpeg", "image/png"]:
            raise ValueError("Formato de arquivo não suportado. Use JPEG ou PNG.")

        file_content = uploaded_file.read()

        file_base64 = base64.b64encode(file_content).decode('utf-8')

        if uploaded_file.type == "image/jpeg":
            file_base64 = f"data:image/jpeg;base64,{file_base64}"
        elif uploaded_file.type == "image/png":
            file_base64 = f"data:image/png;base64,{file_base64}"

        return file_base64
    except Exception as e:
        return f'Ocorreu um erro: {e}'

def enviar_solicitacao(texto, text_pdf=None, file_base64=None, token=500):
    API_URL = "http://backend:8000/ia"

    payload = {
        "texto": texto,
        "max_tokens": token,
        "text_pdf": text_pdf,
        "file": file_base64
    }

    response = requests.post(API_URL, json=payload)

    if response.status_code == 200:
        try:
            resposta_json = response.json()
            return resposta_json.get("response", resposta_json)
        except ValueError:
            return None
