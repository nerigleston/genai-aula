from agents import agente_traducao, agente_sumarizacao, agente_geracao_imagem, agente_geracao_codigo, agente_dectectar_idioma, agent_route_decider, agente_imagem_para_texto, agent_traduzir_texto, agent_responder_pergunta

def realizar_rota(texto):
    return agent_route_decider(texto)

def dectectar_idioma(texto):
    return agente_dectectar_idioma(texto)

def realizar_traducao(texto, idioma_destino):
    idioma_destino = dectectar_idioma(texto)
    return agente_traducao(texto, idioma_destino)

def realizar_sumarizacao(texto, max_tokens=500):
    return agente_sumarizacao(texto, max_tokens)

def realizar_geracao_imagem(descricao):
    return agente_geracao_imagem(descricao)

def realizar_geracao_codigo(descricao_tarefa):
    return agente_geracao_codigo(descricao_tarefa)

def realizar_imagem_para_texto(file, user_input):
    return agente_imagem_para_texto(file, user_input)

def realizar_traducao_texto(request):
    return agent_traduzir_texto(request)

def realizar_responder_pergunta(user_input):
    return agent_responder_pergunta(user_input)
