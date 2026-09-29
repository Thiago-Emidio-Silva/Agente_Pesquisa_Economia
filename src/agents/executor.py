import google.genai as genai
from typing import Optional

class AgenteExecutor:
    """
    Agente responsável por receber uma pergunta específica e usar a busca na web
    para encontrar a resposta mais factual e concisa.
    """
    def __init__(self, client: genai.Client):
        self.client = client

    def executar(self, pergunta: str) -> Optional[str]:
        print(f"  [AGENTE EXECUTOR] Pesquisando pergunta: '{pergunta}'...")
        prompt = f"""
        Responda à seguinte pergunta, baseando-se em informações atuais da internet: {pergunta}.
        Procure cinco fontes nacionais de informação para cada pergunta e 3 fontes internacionais para cada pergunta.
        Responda de forma clara e de facil entendimento.
        """
        try:
            # Usamos o modelo Pro para obter respostas mais detalhadas e com melhor raciocínio
            response = self.client.models.generate_content(
                model="models/gemini-2.5-flash",
                contents=prompt
            )
            print(f"  [AGENTE EXECUTOR] Resposta encontrada: '{response}'")
            return response.text
        except Exception as e:
            print(f"  [AGENTE EXECUTOR] ERRO ao pesquisar: {e}")
            return None

