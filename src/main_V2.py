import os
import json
from dotenv import load_dotenv
import io
from PIL import Image

# --- NOVO IMPORT ---
# Importa a nova biblioteca e seus tipos
import google.genai as genai
from google.genai import types

# --- Funções Auxiliares de Áudio (ainda necessárias) ---
import struct
import mimetypes
from typing import Dict, Optional

def parse_audio_mime_type(mime_type: str) -> Dict[str, Optional[int]]:
    # ... (código sem alterações) ...
    bits_per_sample = 16
    rate = 24000
    parts = mime_type.split(";")
    for param in parts:
        param = param.strip()
        if param.lower().startswith("rate="):
            try: rate = int(param.split("=", 1)[1])
            except (ValueError, IndexError): pass
    return {"bits_per_sample": bits_per_sample, "rate": rate}

def convert_to_wav(audio_data: bytes, mime_type: str) -> bytes:
    # ... (código sem alterações) ...
    parameters = parse_audio_mime_type(mime_type)
    bits_per_sample = parameters["bits_per_sample"]
    sample_rate = parameters["rate"]
    num_channels = 1; data_size = len(audio_data)
    bytes_per_sample = bits_per_sample // 8
    block_align = num_channels * bytes_per_sample
    byte_rate = sample_rate * block_align
    chunk_size = 36 + data_size
    header = struct.pack("<4sI4s4sIHHIIHH4sI", b"RIFF", chunk_size, b"WAVE", b"fmt ", 16, 1, num_channels, sample_rate, byte_rate, block_align, bits_per_sample, b"data", data_size)
    return header + audio_data

# --- Agentes Refatorados para o Novo SDK ---

def agente_pesquisador(client: genai.Client, tema: str) -> Optional[Dict]:
    print(f"\n[AGENTE PESQUISADOR] Iniciando pesquisa sobre: '{tema}'...")
    try:
        # NOVO: A chamada agora é feita através do objeto 'client'
        response = client.models.generate_content(
            model="models/gemini-1.5-flash-latest",
            contents=f"Você é um agente de pesquisa especialista... Pesquise o tópico '{tema}' e retorne um JSON com os campos: titulo_sugerido, resumo_principal, pontos_chave, fonte_confiavel."
        )
        json_text = response.text.replace("```json", "").replace("```", "").strip()
        dados_pesquisados = json.loads(json_text)
        print("[AGENTE PESQUISADOR] Pesquisa concluída.")
        return dados_pesquisados
    except Exception as e:
        print(f"[AGENTE PESQUISADOR] ERRO: {e}")
        return None

def agente_roteirista(client: genai.Client, dados_pesquisa: dict) -> str:
    print("\n[AGENTE ROTEIRISTA] Recebendo dados para criação do roteiro...")
    dados_formatados = json.dumps(dados_pesquisa, indent=2, ensure_ascii=False)
    prompt = f"""
                Você é um roteiro de podcast especialista em criar narrativas engajantes para o programa "Economia em Foco".
                Sua tarefa é transformar os dados estruturados a seguir em um roteiro de podcast dinâmico e conversacional.
                O podcast tem dois narradores: 'ANCORA' e 'ANALISTA'.
                O ANCORA é o apresentador principal. O ANALISTA é o especialista que fornece os dados.
                O roteiro final deve ter entre 600 e 800 palavras.
                ESTRUTURA OBRIGATÓRIA:
                1.  Comece com uma vinheta: [VINHETA DE ABERTURA - ECONOMIA EM FOCO]
                2.  O ANCORA faz uma introdução cativante.
                3.  O ANCORA se apresenta: Meu nome é Mateus Alves
                4.  O ANCORA apresenta o ANALISTA: Larissa Nogueira
                5.  O diálogo entre ANCORA e ANALISTA desenvolve os pontos-chave.
                6.  O ANCORA faz um resumo final e agradece.
                7.  Termine com a vinheta de encerramento: [VINHETA DE ENCERRAMENTO - ECONOMIA EM FOCO]

                REGRAS DE FORMATAÇÃO (MUITO IMPORTANTE):
                - Formate a saída OBRIGATORIAMENTE prefixando cada fala com o nome do locutor entre colchetes.
                - Exemplo de formato CORRETO:
                [ANCORA] Este é o texto do âncora.
                [ANALISTA] Este é o texto do analista.
                - NÃO use negrito (**) ou dois pontos (:) para os nomes dos locutores. O formato deve ser exatamente [NOME].
                """
    try:
        # NOVO: Chamada através do 'client'
        response = client.models.generate_content(
            model="models/gemini-1.5-pro-latest",
            contents=prompt
        )
        print("[AGENTE ROTEIRISTA] Roteiro gerado com sucesso.")
        return response.text
    except Exception as e:
        print(f"[AGENTE ROTEIRISTA] ERRO: {e}")
        return None

def agente_artista_visual(client: genai.Client, roteiro_completo: str, pasta_saida: str) -> bool:
    print("\n[AGENTE ARTISTA VISUAL] Analisando roteiro para criar imagens...")
    try:
        # Etapa 1: Criar os prompts de imagem (esta parte já funciona)
        prompt_para_prompts = f"Você é um diretor de arte... Crie 3 prompts para imagens em uma lista JSON... ROTEIRO:\n---\n{roteiro_completo}\n---"
        response_prompts = client.models.generate_content(
            model="models/gemini-1.5-pro-latest",
            contents=prompt_para_prompts
        )
        json_text_prompts = response_prompts.text.replace("```json", "").replace("```", "").strip()
        prompts_de_imagem = json.loads(json_text_prompts)
        print(f"[AGENTE ARTISTA VISUAL] Prompts de imagem criados com sucesso.")

        # Etapa 2: Gerar as imagens com a chamada de API correta
        print("\n[AGENTE ARTISTA VISUAL] Selecionando modelo Imagen e gerando imagens...")
        for i, prompt_item in enumerate(prompts_de_imagem):
            print(f"[AGENTE ARTISTA VISUAL] Gerando imagem {i+1}/{len(prompts_de_imagem)}...")
            
            # --- CORREÇÃO FINAL E DEFINITIVA APLICADA AQUI ---
            # Garantimos que o prompt é um texto (string), extraindo-o caso
            # a IA o tenha retornado dentro de uma estrutura mais complexa.
            if isinstance(prompt_item, dict) and 'prompt' in prompt_item:
                prompt_final = prompt_item['prompt']
            else:
                prompt_final = str(prompt_item) # Garante que é uma string
            # ----------------------------------------------------

            result = client.models.generate_images(
                model="models/imagen-4.0-generate-001",
                prompt=prompt_final 
            )

            if result.generated_images:
                result.generated_images[0].image.save(os.path.join(pasta_saida, f"imagem_{i+1}.png"))
                print(f"[AGENTE ARTISTA VISUAL] Imagem {i+1} salva.")
            else:
                print(f"[AGENTE ARTISTA VISUAL] ERRO: Nenhuma imagem gerada para o prompt {i+1}.")
                if hasattr(result, 'rai_filtered_reason') and result.rai_filtered_reason:
                    print(f"   Motivo do bloqueio: {result.rai_filtered_reason}")
        return True
    except Exception as e:
        print(f"[AGENTE ARTISTA VISUAL] ERRO: {e}")
        return False

def agente_locutor(client: genai.Client, roteiro: str, pasta_saida: str) -> bool:
    print("\n[AGENTE LOCUTOR] Iniciando geração de áudio com o método Multi-Speaker...")
    try:
        # Etapa 1: Formatar o roteiro para a API
        texto_formatado = roteiro.replace("[ÂNCORA]", "Speaker 1:") \
                                 .replace("[ANALISTA]", "Speaker 2:") \
                                 .replace("[VINHETA DE ABERTURA - ECONOMIA EM FOCO]", "") \
                                 .replace("[VINHETA DE ENCERRAMENTO - ECONOMIA EM FOCO]", "").strip()

        # Etapa 2: Configurar e chamar a API de TTS (exatamente como você descobriu)
        model_tts = "gemini-2.5-pro-preview-tts"
        contents = [types.Content(role="user", parts=[types.Part.from_text(text=texto_formatado)])]
        tts_config = types.GenerateContentConfig(
            response_modalities=["audio"],
            speech_config=types.SpeechConfig(multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(speaker_voice_configs=[
                types.SpeakerVoiceConfig(speaker="Speaker 1", voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck"))),
                types.SpeakerVoiceConfig(speaker="Speaker 2", voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Charon"))),
            ]))
        )
        stream = client.models.generate_content_stream(model=model_tts, contents=contents, config=tts_config)

        # Etapa 3: Processar e salvar o áudio
        audio_buffer = b''; audio_mime_type = "audio/wav"
        for chunk in stream:
            if chunk.candidates and chunk.candidates[0].content and chunk.candidates[0].content.parts[0].inline_data:
                part = chunk.candidates[0].content.parts[0]
                audio_mime_type = part.inline_data.mime_type
                audio_buffer += part.inline_data.data
        
        if not audio_buffer: raise ValueError("Nenhum dado de áudio recebido.")
        
        final_audio_data = convert_to_wav(audio_buffer, audio_mime_type)
        caminho_arquivo = os.path.join(pasta_saida, "episodio_completo.wav")
        with open(caminho_arquivo, "wb") as f: f.write(final_audio_data)
        
        print(f"[AGENTE LOCUTOR] Áudio completo salvo com sucesso.")
        return True
    except Exception as e:
        print(f"[AGENTE LOCUTOR] ERRO: {e}")
        return False

def main():
    """Função principal que orquestra o fluxo de trabalho do 'Estúdio AI'."""
    print("--- [ORQUESTRADOR] Estúdio AI Iniciado com o NOVO SDK 'google-genai' ---")
    load_dotenv()
    
    try:
        # NOVO: Inicialização centralizada do cliente
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key: raise ValueError("Chave de API 'GEMINI_API_KEY' não encontrada.")
        client = genai.Client(api_key=api_key)
        print("[ORQUESTRADOR] Cliente GenAI inicializado com sucesso.")
    except Exception as e:
        print(f"[ORQUESTRADOR] ERRO ao inicializar o cliente: {e}")
        return
    
    tema_do_dia = "Impacto da inteligência artificial na produtividade de pequenas empresas no Brasil"
    
    # NOVO: Passamos o objeto 'client' para cada agente
    dados_pesquisados = agente_pesquisador(client=client, tema=tema_do_dia)
    
    if dados_pesquisados:
        roteiro_final = agente_roteirista(client=client, dados_pesquisa=dados_pesquisados)
        if roteiro_final:
            pasta_episodio = "episodio_gerado"
            os.makedirs(pasta_episodio, exist_ok=True)
            caminho_roteiro = os.path.join(pasta_episodio, "roteiro_final.txt")
            with open(caminho_roteiro, "w", encoding="utf-8") as f: f.write(roteiro_final)
            print(f"\n[ORQUESTRADOR] Roteiro salvo em '{caminho_roteiro}'")
            
            sucesso_imagens = agente_artista_visual(client=client, roteiro_completo=roteiro_final, pasta_saida=pasta_episodio)
            if sucesso_imagens:
                sucesso_audio = agente_locutor(client=client, roteiro=roteiro_final, pasta_saida=pasta_episodio)
                if sucesso_audio:
                    print("\n[ORQUESTRADOR] PROCESSO COMPLETO! Estúdio AI finalizado com sucesso!")
                else: print("\n[ORQUESTRADOR] Processo interrompido no Agente Locutor.")
            else: print("\n[ORQUESTRADOR] Processo interrompido no Agente Artista Visual.")
        else: print("\n[ORQUESTRADOR] Processo interrompido no Agente Roteirista.")
    else: print("\n[ORQUESTRADOR] Processo interrompido no Agente Pesquisador.")

    print("\n--- [ORQUESTRADOR] Fim da execução ---")

if __name__ == "__main__":
    main()