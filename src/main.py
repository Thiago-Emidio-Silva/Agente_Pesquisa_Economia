import os
import json
from dotenv import load_dotenv

# SDKs
import google.genai as genai
import vertexai

# Importa as CLASSES dos nossos agentes a partir dos seus respetivos ficheiros
from agents.planejador import AgentePlanejador
from agents.executor import AgenteExecutor
from agents.sintetizador import AgenteSintetizador
from agents.roteirista import AgenteRoteirista
from agents.artista_visual import AgenteArtistaVisual
from agents.locutor import AgenteLocutor

def main():
    """
    Função principal que orquestra o fluxo de trabalho completo do 'Estúdio AI'.
    """
    print("--- [ORQUESTRADOR] Estúdio AI Iniciado (v2.0 - Modular) ---")
    load_dotenv()
    
    # --- Configurações Iniciais ---
    try:
        # Cliente do GenAI (para texto e TTS)
        client_genai = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        print("[ORQUESTRADOR] Cliente GenAI inicializado.")

        # Inicialização do Vertex AI (para imagens)
        PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
        LOCATION = "us-central1"
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        print(f"[ORQUESTRADOR] Vertex AI inicializado para o projeto '{PROJECT_ID}'.")
    except Exception as e:
        print(f"[ORQUESTRADOR] ERRO nas configurações iniciais: {e}")
        return

    # --- Instanciação dos Agentes ---
    print("\n[ORQUESTRADOR] A instanciar todos os agentes...")
    agente_planejador = AgentePlanejador(client=client_genai)
    agente_executor = AgenteExecutor(client=client_genai)
    agente_sintetizador = AgenteSintetizador(client=client_genai)
    agente_roteirista = AgenteRoteirista(client=client_genai)
    agente_artista_visual = AgenteArtistaVisual(client=client_genai)
    agente_locutor = AgenteLocutor(client=client_genai)

    # --- Execução do Fluxo de Trabalho ---
    tema_do_dia = "Procure na internet os ultimos acontecimentos na área de economica na semana entre 22/09/2025 e 25/09/2025"
    
    # Define o caminho absoluto para a pasta de saída para garantir que ela sempre seja encontrada.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pasta_episodio = os.path.join(script_dir, "episodio_gerado")
    os.makedirs(pasta_episodio, exist_ok=True)
    
    # 1. Fase de Pesquisa
    plano = agente_planejador.executar(tema=tema_do_dia)
    if not plano:
        print("[ORQUESTRADOR] Processo interrompido: Falha no planeamento.")
        return

    pesquisas_coletadas = []
    for pergunta in plano:
        resposta = agente_executor.executar(pergunta=pergunta)
        if resposta:
            pesquisas_coletadas.append({"pergunta": pergunta, "resposta": resposta})
    
    if not pesquisas_coletadas:
        print("[ORQUESTRADOR] Processo interrompido: Falha na execução da pesquisa.")
        return
        
    dados_pesquisados = agente_sintetizador.executar(tema=tema_do_dia, pesquisas_coletadas=pesquisas_coletadas)
    if not dados_pesquisados:
        print("[ORQUESTRADOR] Processo interrompido: Falha na síntese da pesquisa.")
        return

    # 2. Fase de Produção de Conteúdo
    roteiro_final = agente_roteirista.executar(dados_pesquisa=dados_pesquisados)
    if not roteiro_final:
        print("[ORQUESTRADOR] Processo interrompido: Falha na criação do roteiro.")
        return
        
    caminho_roteiro = os.path.join(pasta_episodio, "roteiro_final.txt")
    with open(caminho_roteiro, "w", encoding="utf-8") as f:
        f.write(roteiro_final)
    print(f"\n[ORQUESTRADOR] Roteiro salvo em '{caminho_roteiro}'")
            
    sucesso_imagens = agente_artista_visual.executar(roteiro_completo=roteiro_final, pasta_saida=pasta_episodio)
    if not sucesso_imagens:
        print("[ORQUESTRADOR] Processo interrompido: Falha na geração de imagens.")
        return

    sucesso_audio = agente_locutor.executar(roteiro=roteiro_final, pasta_saida=pasta_episodio)
    if not sucesso_audio:
        print("[ORQUESTRADOR] Processo interrompido: Falha na geração de áudio.")
        return

    print("\n[ORQUESTRADOR] PROCESSO COMPLETO! Estúdio AI finalizado com sucesso!")
    print(f"   Todos os ficheiros foram salvos na pasta: '{pasta_episodio}'")

if __name__ == "__main__":
    main()

