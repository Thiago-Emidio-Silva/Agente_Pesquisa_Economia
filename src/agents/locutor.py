import google.genai as genai
from google.genai import types
import os
import re

# Importa as funções auxiliares do nosso novo ficheiro utils
# O ponto (.) antes de 'utils' significa que estamos a importar do mesmo pacote (pasta 'agents')
from .utils import convert_to_wav

class AgenteLocutor:
    """
    Agente responsável por receber um roteiro e gerar um único ficheiro de áudio
    com duas vozes, usando o método Multi-Speaker do Gemini.
    """
    def __init__(self, client: genai.Client):
        self.client = client

    def executar(self, roteiro: str, pasta_saida: str) -> bool:
        print("\n[AGENTE LOCUTOR] A iniciar a geração de áudio com o método Multi-Speaker...")
        try:
            # Etapa 1: Formatar o roteiro para a API de TTS.
            # O modelo espera 'Speaker 1:', 'Speaker 2:', etc.
            # Vamos substituir '[ANCORA]' por 'Speaker 1:' e '[ANALISTA]' por 'Speaker 2:'.
            texto_formatado = roteiro.replace("[ANCORA]", "Speaker 1:") \
                                     .replace("[ANALISTA]", "Speaker 2:") \
                                     .replace("[VINHETA DE ABERTURA - ECONOMIA EM FOCO]", "") \
                                     .replace("[VINHETA DE ENCERRAMENTO - ECONOMIA EM FOCO]", "").strip()

            # Etapa 2: Configurar e chamar a API de TTS.
            model_tts = "gemini-2.5-pro-preview-tts"
            contents = [types.Content(role="user", parts=[types.Part.from_text(text=texto_formatado)])]
            
            tts_config = types.GenerateContentConfig(
                response_modalities=["audio"],
                speech_config=types.SpeechConfig(
                    multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                        speaker_voice_configs=[
                            types.SpeakerVoiceConfig(
                                speaker="Speaker 1",
                                voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck"))
                            ),
                            types.SpeakerVoiceConfig(
                                speaker="Speaker 2",
                                voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Zephyr"))
                            ),
                        ]
                    )
                ),
            )

            print(f"[AGENTE LOCUTOR] A enviar roteiro para o modelo '{model_tts}' para síntese de voz...")
            stream = self.client.models.generate_content_stream(model=model_tts, contents=contents, config=tts_config)

            # Etapa 3: Processar o áudio recebido.
            audio_buffer = b''
            audio_mime_type = "audio/wav" # Padrão
            for chunk in stream:
                if chunk.candidates and chunk.candidates[0].content and chunk.candidates[0].content.parts[0].inline_data:
                    part = chunk.candidates[0].content.parts[0]
                    audio_mime_type = part.inline_data.mime_type
                    audio_buffer += part.inline_data.data
            
            if not audio_buffer:
                raise ValueError("Nenhum dado de áudio foi recebido.")
            
            # Etapa 4: Converter para .wav e salvar o ficheiro final, usando a função do utils.py.
            final_audio_data = convert_to_wav(audio_buffer, audio_mime_type)
            caminho_ficheiro = os.path.join(pasta_saida, "episodio_completo.wav")
            
            with open(caminho_ficheiro, "wb") as f:
                f.write(final_audio_data)
            
            print(f"[AGENTE LOCUTOR] Áudio completo salvo com sucesso.")
            return True
        except Exception as e:
            print(f"[AGENTE LOCUTOR] ERRO: {e}")
            return False

