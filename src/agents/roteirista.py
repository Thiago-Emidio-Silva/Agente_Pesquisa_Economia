import google.genai as genai
import json
from typing import Dict, Optional

class AgenteRoteirista:
    """
    Agente responsável por receber o relatório de pesquisa e transformá-lo
    em um roteiro de podcast com duas vozes.
    """
    def __init__(self, client: genai.Client):
        self.client = client

    def executar(self, dados_pesquisa: Dict) -> Optional[str]:
        print("\n[AGENTE ROTEIRISTA] Recebendo dados para criação do roteiro...")
        
        dados_formatados = json.dumps(dados_pesquisa, indent=2, ensure_ascii=False)
        
        prompt = f"""
        Você é um roteirista de podcast especialista em criar narrativas engajantes para o programa "Economia em Foco".
        Sua tarefa é transformar os dados estruturados a seguir em um roteiro de podcast dinâmico e conversacional.
        O podcast tem dois narradores: 'ANCORA' e 'ANALISTA'.
        O ANCORA é o apresentador principal. O ANALISTA é o especialista que fornece os dados.
        O roteiro final deve ter entre 1000 e 1200 palavras.

        ESTRUTURA OBRIGATÓRIA:
        1.  Comece com uma vinheta: [VINHETA DE ABERTURA - ECONOMIA EM FOCO]
        2.  O ANCORA faz uma introdução cativante.
        3.  O ANCORA se apresenta: Meu nome é Mateus Alves
        4.  O ANCORA apresenta o ANALISTA: Larissa Nogueira
        5.  O diálogo entre ANCORA e ANALISTA desenvolve o conteúdo do relatório de pesquisa, especialmente as seções e os pontos-chave.
        6.  O ANCORA faz um resumo final e agradece.
        7.  Termine com a vinheta de encerramento: [VINHETA DE ENCERRAMENTO - ECONOMIA EM FOCO]

        REGRAS DE FORMATAÇÃO (MUITO IMPORTANTE):
        - Formate a saída OBRIGATORIAMENTE prefixando cada fala com o nome do locutor entre colchetes.
        - Exemplo de formato CORRETO:
          [ANCORA] Este é o texto do âncora.
          [ANALISTA] Este é o texto do analista.
        - NÃO use negrito (**) ou dois pontos (:) para os nomes dos locutores. O formato deve ser exatamente [NOME].

        DADOS DE ENTRADA (Relatório da Pesquisa):
        ---
        {dados_formatados}
        ---
        """
        try:
            # Usamos o modelo Pro para tarefas criativas e de escrita longa
            response = self.client.models.generate_content(
                model="models/gemini-2.5-flash",
                contents=prompt
            )
            print("[AGENTE ROTEIRISTA] Roteiro gerado com sucesso.")
            return response.text
        except Exception as e:
            print(f"[AGENTE ROTEIRISTA] ERRO: {e}")
            return None

