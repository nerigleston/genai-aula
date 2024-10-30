from pydantic import BaseModel
from typing import Optional

class TextoEntrada(BaseModel):
    texto: str
    max_tokens: int = 500
    text_pdf: Optional[str] = None
    file: Optional[str] = None
