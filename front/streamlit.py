from utils import pdf_to_text, image_to_base64, enviar_solicitacao
import streamlit as st
from io import BytesIO
from PIL import Image
import base64

st.set_page_config(page_title="Chatbot IA", layout="wide")
st.title("Chatbot IA")
st.markdown("Chatbot para processar arquivos e responder perguntas com IA.")

with st.sidebar:
    st.header("📂 Upload ou Insira Texto")
    uploaded_file = st.file_uploader("Carregar um PDF ou Imagem", type=["pdf", "jpeg", "png"])
    max_tokens = st.number_input("Defina o número máximo de tokens (apenas para sumarização):", min_value=500, max_value=1000, value=500)
    texto = st.text_area("Digite sua pergunta ou texto para processar:")

text_pdf = None
file_base64 = None

if uploaded_file is not None:
    with st.expander("Detalhes do Arquivo", expanded=False):
        if uploaded_file.type == "application/pdf":
            text_pdf = pdf_to_text(uploaded_file)
            st.write(text_pdf)
        elif uploaded_file.type in ["image/jpeg", "image/png"]:
            file_base64 = image_to_base64(uploaded_file)
            image = Image.open(uploaded_file)
            st.image(image, caption="Imagem carregada", use_column_width=True)

if st.button("💬 Processar"):
    if texto.strip():
        resposta = enviar_solicitacao(texto, text_pdf, file_base64, token=max_tokens)
        if resposta:
            with st.container():
                st.markdown("#### 💬 Resposta do Chatbot:")
                if isinstance(resposta, str) and resposta.startswith("data:image/png;base64,"):
                    image_data = base64.b64decode(resposta.split(",")[1])
                    image = Image.open(BytesIO(image_data))
                    st.image(image, caption="Imagem gerada pela IA", use_column_width=True)
                else:
                    st.write(resposta)
    else:
        st.warning("Por favor, insira uma pergunta ou texto para continuar.")

st.markdown("---")
st.caption("Desenvolvido com Streamlit")
