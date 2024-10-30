from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import requests
import json
import os

load_dotenv()

llm_google = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("google_api_key")
)

llm_gemma = HuggingFaceEndpoint(
    endpoint_url="https://api-inference.huggingface.co/models/google/gemma-2-2b-it",
    huggingfacehub_api_token=os.getenv("huggingface_api_key")
)

def agent_route_decider(user_input):
    try:
        openapi_path = os.path.join(os.path.dirname(__file__), 'openapi.json')
        with open(openapi_path) as f:
            openapi_data = json.load(f)
    except Exception as e:
        print(f"Erro ao carregar o arquivo OpenAPI: {e}")
        return None

    paths = openapi_data.get('paths', {})
    route_descriptions = {}

    for route, methods in paths.items():
        for method, details in methods.items():
            route_descriptions[route] = details.get('description', '')

    template = """
        A seguir estão as descrições das rotas de uma API:

        {routes_descriptions}

        Pergunta do usuário: {user_input}

        Com base nas descrições das rotas, na pergunta do usuário e se houver histórico acrescente caso seja NULL não mande o histórico, determine qual rota se encaixa melhor para responder à pergunta.
        Responda apenas com a rota mais apropriada.
    """

    prompt = template.format(
        routes_descriptions=json.dumps(route_descriptions, indent=2),
        user_input=user_input
    )

    response = llm_google.invoke(prompt)

    chosen_route = response.content.strip().replace('`', '')

    print(f"Rota escolhida: {chosen_route}")
    return {"route": chosen_route}

def agente_dectectar_idioma(texto):
    prompt = PromptTemplate.from_template(f'''
        Detecte o idioma para qual o usuário deseja traduzir o seguinte texto: {texto}.
        Retorne apenas a sigla do idioma. Exemplo: 'en'
    ''')
    resposta = llm_google.invoke([{"role": "user", "content": prompt.format(texto=texto)}])
    return resposta.content

def agente_traducao(texto, idioma):
    prompt = PromptTemplate.from_template(f'''
        Traduza o seguinte texto para {idioma}: {texto}
        Sempre retorne da seguinte forma:
        idioma original:\n
        texto original\n
        --------------------------------\n
        idioma traduzido:\n
        texto traduzido
    ''')
    resposta = llm_google.invoke([{"role": "user", "content": prompt.format(idioma=idioma, texto=texto)}])
    return resposta.content

def agente_sumarizacao(texto, max_tokens=600):
    prompt = PromptTemplate.from_template(f'''
        Resuma o seguinte texto em até {max_tokens} tokens: {texto}
    ''')
    resposta = llm_google.invoke([{"role": "user", "content": prompt.format(max_tokens=max_tokens, texto=texto)}])
    return resposta.content

def agente_geracao_imagem(descricao):
    invoke_url = "https://ai.api.nvidia.com/v1/genai/stabilityai/sdxl-turbo"
    headers = {
        "Authorization": f"Bearer {os.getenv('nvidia_api_key')}",
        "Accept": "application/json",
    }
    payload = {
        "text_prompts": [{"text": descricao}],
        "seed": 0,
        "sampler": "K_EULER_ANCESTRAL",
        "steps": 2
    }
    response = requests.post(invoke_url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def agente_geracao_codigo(descricao_tarefa):
    prompt = PromptTemplate.from_template(f'''
        Você é um desenvolvedor de software e precisa escrever um código para a seguinte tarefa: {descricao}.
        Escreva o código que resolve o problema.
    ''')
    resposta = llm_google.invoke([{"role": "user", "content": prompt.format(descricao=descricao_tarefa)}])
    return resposta.content

def agente_imagem_para_texto(file, user_input):
    try:
        client = InferenceClient(api_key=os.getenv("huggingface_api_key"))

        response = client.chat_completion(
            model="meta-llama/Llama-3.2-11B-Vision-Instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": file}},
                        {"type": "text", "text": f"{user_input}, resume"},
                    ],
                }
            ],
            max_tokens=500
        )

        return response.choices[0].message['content']
    except Exception as e:
        print(f"Erro ao converter imagem em texto: {e}")

def agent_traduzir_texto(texto):
    prompt = PromptTemplate.from_template(f'''
        Traduza o seguinte texto para português: {texto}, mostre APENAS texto traduzido.
    ''')
    resposta = llm_google.invoke([{"role": "user", "content": prompt.format(texto=texto)}])
    return resposta.content

def agent_responder_pergunta(pergunta):
    prompt = PromptTemplate.from_template(f'''
        Responda a seguinte pergunta: {pergunta}
        e gere uma resposta coerente e relevante, pode conter fatos ou informações gerais,
        para deixar a resposta mais completa e informativa.\n
        Sem fornecer informações falsas, se não souber a resposta, retorne 'Não sei'.
    ''')
    resposta = llm_google.invoke([{"role": "user", "content": prompt.format(pergunta=pergunta)}])
    return resposta.content
