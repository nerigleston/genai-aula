from fastapi import FastAPI, HTTPException, File, UploadFile
from models import TextoEntrada
from ia import (
    realizar_traducao,
    realizar_sumarizacao,
    realizar_geracao_imagem,
    realizar_geracao_codigo,
    dectectar_idioma,
    realizar_rota,
    realizar_imagem_para_texto,
    realizar_traducao_texto,
    realizar_responder_pergunta
)

app = FastAPI(
    title="API de IA",
    description="API para realizar tradução, sumarização, geração de imagem e geração de código.",
    version="0.1.0",
    openapi_url="/openapi.json",
    docs_url="/",
)

@app.post(
    "/ia",
    description="Rota principal para realizar operações de IA.",
    tags=["IA"],
)
async def rota(request: TextoEntrada):
    extract_info = None

    if request.file:
        selected_route = '/imagem-para-texto'
        return await imagem_para_texto(request)

    if not request.file:
        extract_info = realizar_rota(f"'texto': {request.texto}, 'text_pdf': {request.text_pdf}")

    if isinstance(extract_info, dict):
        selected_route = extract_info.get('route')
    else:
        raise HTTPException(status_code=400, detail="Rota não reconhecida. Esperava um dicionário.")

    if not selected_route:
        raise HTTPException(status_code=400, detail="Rota não reconhecida. Verifique se o texto está correto.")

    if selected_route == '/traducao':
        return await traducao(request)
    elif selected_route == '/sumarizacao':
        return await sumarizacao(request)
    elif selected_route == '/geracao-imagem':
        return await geracao_imagem(request)
    elif selected_route == '/geracao-codigo':
        return await geracao_codigo(request)
    elif selected_route == '/conhecimentos':
        return await conhecimentos_gerais(request)
    else:
        raise HTTPException(status_code=400, detail="Rota não reconhecida. Verifique se o texto está correto.")

@app.post(
    "/traducao",
    description="Traduz o texto fornecido para o idioma de destino especificado. Ideal para adaptar conteúdos a diferentes idiomas e culturas.",
    response_description="Resultado da tradução, retornando o texto no idioma desejado.",
    include_in_schema=False
)
async def traducao(request: TextoEntrada):
    texto = f"'texto': {request.texto}, 'text_pdf': {request.text_pdf}"
    idioma = dectectar_idioma(request.texto)
    resultado = realizar_traducao(request.texto, idioma)
    return {"response": resultado}

@app.post(
    "/sumarizacao",
    description="Gera uma sumarização do texto fornecido, capturando os pontos principais em um número máximo de tokens especificado. Útil para sintetizar informações longas.",
    response_description="Texto sumarizado, fornecendo uma versão condensada do conteúdo original.",
    include_in_schema=False
)
async def sumarizacao(request: TextoEntrada):
    texto = f"'texto': {request.texto}, 'text_pdf': {request.text_pdf}"
    resultado = realizar_sumarizacao(texto, request.max_tokens)
    return {"response": resultado}

@app.post(
    "/geracao-imagem",
    description="Cria uma imagem com base em uma descrição textual. Perfeito para visualizar ideias ou conceitos a partir de descrições abstratas ou específicas. Ele sempre vai me retornar en base64",
    response_description="URL ou dados da imagem gerada, com base na descrição fornecida.",
    include_in_schema=False
)
async def geracao_imagem(request: TextoEntrada):
    resultado = realizar_geracao_imagem(request.texto)
    base64_imagem = resultado['artifacts'][0].get('base64', None)
    return {"response": f"data:image/png;base64, {base64_imagem}"}

@app.post(
    "/geracao-codigo",
    description="Gera um trecho de código para realizar uma tarefa específica, descrita em linguagem natural. Ideal para automatizar partes de desenvolvimento com base em instruções descritivas.",
    response_description="Código gerado que atende à descrição da tarefa fornecida.",
    include_in_schema=False
)
async def geracao_codigo(request: TextoEntrada):
    texto = f"'texto': {request.texto}, 'text_pdf': {request.text_pdf}"
    resultado = realizar_geracao_codigo(texto)
    return {"response": resultado}

@app.post(
    "/imagem-para-texto",
    description="Converte uma imagem em texto, permitindo a extração de informações de imagens para análise ou processamento posterior.",
    response_description="Texto extraído da imagem fornecida.",
    include_in_schema=False
)
async def imagem_para_texto(request: TextoEntrada):
    user_input = request.texto
    file_base64 = request.file

    img_text = realizar_imagem_para_texto(file_base64, user_input)

    resultado = realizar_traducao_texto(img_text)

    return {"response": resultado}

@app.post(
    "/conhecimentos",
    description="Responde a perguntas de conhecimentos gerais com base em um texto fornecido. Ideal para responder a perguntas sobre uma ampla variedade de tópicos.",
    response_description="Resposta à pergunta de conhecimentos gerais, com base no texto fornecido.",
    include_in_schema=False
)
async def conhecimentos_gerais(request: TextoEntrada):
    user_input = request.texto

    resultado = realizar_responder_pergunta(user_input)

    return {"response": resultado}
