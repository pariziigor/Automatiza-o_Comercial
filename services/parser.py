import re

print("--- MÓDULO PARSER ATUALIZADO CARREGADO ---")

# --- CONFIGURACOES E LISTAS ---

STOP_WORDS = [
    "CADASTRAL", "SITUAÇÃO", "DATA", "MOTIVO", "NOME", "TITULO", "TÍTULO",
    "LOGRADOURO", "NÚMERO", "COMPLEMENTO", "CEP", "BAIRRO", "MUNICÍPIO",
    "UF", "TELEFONE", "ENTE", "CAPITAL", "PORTE", "NATUREZA", "MATRIZ",
    "CÓDIGO", "DESCRIÇÃO", "ATIVIDADE", "ECONÔMICA", "PRINCIPAL", "SECUNDÁRIA",
    "ABERTURA", "INSCRIÇÃO", "FANTASIA", "ESTABELECIMENTO", "E-MAIL", "EMAIL"
]

REGEX_PATTERNS = {
    "cnpj": r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}",
    "cpf": r"\d{3}\.\d{3}\.\d{3}-\d{2}",
    "cep": r"\d{2}\.\d{3}-\d{3}",
    "data": r"\d{2}/\d{2}/\d{4}",
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "celular": r"\(\d{2}\)\s?\d{4,5}-\d{4}"
}

MAPA_DE_BUSCA = {
    
    #Solicitante Dados
    "NOME_EMPRESA_SOLICITANTE": ["nome da empresa", "razão social", "nome empresarial", "cliente"],
    "CNPJ_CPF_SOLICITANTE": ["número de inscrição", "cnpj", "cpf"],
    "IE_SOLICITANTE": ["inscrição estadual", "inscr. estadual", "ie"],
    "ENDERECO_SOLICITANTE": ["endereço", "end.", "rua", "logradouro"],
    "BAIRRO_SOLICITANTE": ["bairro", "distrito"],
    "CIDADE_SOLICITANTE": ["cidade", "município"],
    "CEP_SOLICITANTE": ["cep"],
    "EMAIL_SOLICITANTE": ["email", "e-mail", "correio eletrônico"],
    "CELULAR_SOLICITANTE": ["celular", "whatsapp", "telefone", "contato"],

    #Contratante Dados
    "NOME_EMPRESA_CONTRATANTE": ["razão social", "nome da empresa", "sacado", "pagador", "faturar para", "nome empresarial"],
    "CNPJ_CPF_CONTRATANTE": ["cnpj", "cpf", "número de inscrição"],
    "ENDERECO_CONTRATANTE": ["endereço", "logradouro", "end.", "rua"],
    "BAIRRO_CONTRATANTE": ["bairro", "distrito" , "bairro/distrito"],
    "CIDADE_CONTRATANTE": ["cidade", "município"],
    "CEP_CONTRATANTE": ["cep"],
    "EMAIL_CONTRATANTE": ["email", "email financeiro", "contato financeiro"],
    "CELULAR_CONTRATANTE": ["telefone", "celular", "whatsapp"]
}

def limpar_linha(texto):
    if not texto: return ""
    try:
        # Tenta remover marcadores do tipo 
        texto_limpo = re.sub(r'\','' ', str(texto))
        return " ".join(texto_limpo.split())
    except Exception as e:
        print(f"Erro ao limpar linha: {e}")
        return str(texto).strip()

def extrair_por_regex(texto_completo, tipo_dado):
    if tipo_dado in REGEX_PATTERNS:
        match = re.search(REGEX_PATTERNS[tipo_dado], texto_completo)
        if match:
            return match.group(0)
    return None

def extrair_por_ancora(linhas, termos_busca):
    for i, linha in enumerate(linhas):
        linha_limpa = limpar_linha(linha)
        linha_upper = linha_limpa.upper()
        
        termo_encontrado = False
        for termo in termos_busca:
            if termo.upper() in linha_upper:
                termo_encontrado = True
                break
        
        if termo_encontrado:
            # ESTRATEGIA 1: Mesma linha
            if ":" in linha_limpa:
                partes = linha_limpa.split(":", 1)
                if len(partes) > 1:
                    possible_val = partes[1].strip()
                    eh_stop = False
                    for sw in STOP_WORDS:
                        if sw in possible_val.upper():
                            eh_stop = True
                            break
                    if possible_val and not eh_stop and len(possible_val) > 1:
                        return possible_val

            # ESTRATEGIA 2: Linha de baixo
            if i + 1 < len(linhas):
                proxima_linha = limpar_linha(linhas[i + 1])
                if not proxima_linha:
                    continue
                
                eh_titulo = False
                for sw in STOP_WORDS:
                    if sw in proxima_linha.upper():
                        eh_titulo = True
                        break
                
                tem_dois_pontos = ":" in proxima_linha

                if not eh_titulo and not tem_dois_pontos:
                    return proxima_linha
    return None

def identificar_tipo_dado(chave_placeholder):
    chave_lower = chave_placeholder.lower()
    if "cnpj" in chave_lower or "cpf" in chave_lower: return "cnpj"
    if "cep" in chave_lower: return "cep"
    if "data" in chave_lower: return "data"
    if "email" in chave_lower: return "email"
    if "celular" in chave_lower or "telefone" in chave_lower: return "celular"
    return None

def processar_dados(todos_placeholders, texto_cliente, sufixo_filtro=None):
    dados_encontrados = {}
    
    if not texto_cliente:
        return {}

    linhas = texto_cliente.split('\n')

    for p in todos_placeholders:
        if p.startswith("X_"): continue

        if sufixo_filtro and not p.endswith(sufixo_filtro):
            continue

        chave_limpa = p.replace("{", "").replace("}", "").strip()
        
        if chave_limpa not in MAPA_DE_BUSCA:
            continue

        valor = None
        
        # 1. Tenta Regex
        tipo = identificar_tipo_dado(chave_limpa)
        if tipo:
            valor = extrair_por_regex(texto_cliente, tipo)

        # 2. Tenta Ancora
        if not valor:
            termos = MAPA_DE_BUSCA[chave_limpa]
            valor = extrair_por_ancora(linhas, termos)

        if valor:
            dados_encontrados[p] = valor[:200]
            
    return dados_encontrados