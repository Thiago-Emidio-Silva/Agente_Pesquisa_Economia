import google.genai as genai
import json
from typing import Dict, Optional, List

class AgenteSintetizador:
    """
    Agente responsável por receber todas as pesquisas coletadas e sintetizá-las
    no formato JSON final para os próximos agentes.
    """
    def __init__(self, client: genai.Client):
        self.client = client

    def executar(self, tema: str, pesquisas_coletadas: List[Dict]) -> Optional[Dict]:
        print("\n[AGENTE SINTETIZADOR] Sintetizando todas as pesquisas em um relatório final...")
        
        pesquisas_formatadas = "\n\n".join([f"Pergunta: {p['pergunta']}\nResposta: {p['resposta']}" for p in pesquisas_coletadas])
        
        prompt = f"""
        Você é um editor-chefe. Sua tarefa é pegar uma coleção de pesquisas (perguntas e respostas)
        e sintetizá-las em um relatório final no formato JSON.
        O tema geral do relatório é: "{tema}".

        PESQUISAS COLETADAS:
        ---
        {pesquisas_formatadas}
        ---

        Sua saída DEVE ser apenas um JSON válido com os seguintes campos:
        - "titulo_sugerido": Um título curto e chamativo para um podcast sobre o tema.
        - "resumo_principal": Um parágrafo de 3 a 4 frases resumindo as descobertas.
        - "pontos_chave": Uma lista de 5 a 7 strings, onde cada string é um ponto crucial extraído das pesquisas.
        - "Seção 1: Sumário Executivo": Um sumário executivo sobre os fatos encontrados.
        - "Seção 2: Panorama Macroeconômico": Um panorama geral sobre os pontos encontrados.
        - "Seção 3: Mercados Financeiros em Foco": Uma análise sobre o mercado financeiro, nacional e internacional.
        - "Seção 4: Area Internacional": Verificar o mercado financeiro internacional e relacionar com mercado interno.
        - "Seção 5: Síntese e Perspectiva Estratégica": Uma perspectiva estratégica das informações encontradas.
        - "Seção 6: Análise competitiva": Uma análise de como os acontecimentos seus principais concorrentes.
        - "Seção 7: Riscos e oportunidades": Uma avaliação equilibrada dos potenciais riscos (desafios, obstáculos, possíveis resultados negativos) e das oportunidades (potencial de crescimento, novas linhas de negócio, vantagens estratégicas) que surgem a partir das informações pesquisadas.
        - "Seção 8: Impacto no cosumidor e na cadeia de valor":  Explora como as notícias afetam o cliente final e outros parceiros de negócio
        - "Seção 9: Indicadores-chave de desempenho (KPI's)": Uma pequena tabela ou lista com os números mais importantes mencionados na pesquisa
        - "Seção 10: Opinião de analistas": Um resumo do que analistas de mercado estão a dizer e uma projeção dos próximos eventos ou anúncios esperados
        - "fonte_confiavel": Um link para a fonte mais relevante mencionada nas pesquisas.
        """
        try:
            # Usamos o modelo Pro para garantir uma síntese de alta qualidade
            response = self.client.models.generate_content(
                model="models/gemini-2.5-flash",
                contents=prompt
            )
            json_text = response.text.replace("```json", "").replace("```", "").strip()
            relatorio_final = json.loads(json_text)
            print("[AGENTE SINTETIZADOR] Relatório final gerado com sucesso.")
            return relatorio_final
        except Exception as e:
            print(f"[AGENTE SINTETIZADOR] ERRO: {e}")
            return None

