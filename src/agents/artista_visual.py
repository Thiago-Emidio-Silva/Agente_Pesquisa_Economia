import google.genai as genai
import json
import os
from typing import Dict, Optional

class AgenteArtistaVisual:
    """
    Agente responsável por criar e salvar imagens com base no roteiro do podcast.
    Ele primeiro gera os prompts e depois as imagens.
    """
    def __init__(self, client: genai.Client):
        self.client = client

    def executar(self, roteiro_completo: str, pasta_saida: str) -> bool:
        print("\n[AGENTE ARTISTA VISUAL] Analisando roteiro para criar imagens...")
        try:
            # Etapa 1: Criar os prompts de imagem com um modelo de texto.
            prompt_para_prompts = f"""
            Você é um diretor de arte. Leia o roteiro de podcast a seguir e identifique em cada paragrafo de cada locução
            momentos ou conceitos importantes para ilustrar.
            Para cada um, crie dois prompt de imagem detalhado, em inglês, para uma IA de geração de imagem.
            O estilo deve ser "corporate illustration, flat design, vibrant colors".
            Sua resposta DEVE ser apenas uma lista em formato JSON de 10 strings.
            ROTEIRO:
            ---
            {roteiro_completo}
            ---
            """
            response_prompts = self.client.models.generate_content(
                model="models/gemini-2.5-flash-lite",
                contents=prompt_para_prompts
            )
            json_text_prompts = response_prompts.text.replace("```json", "").replace("```", "").strip()
            prompts_de_imagem = json.loads(json_text_prompts)
            print(f"[AGENTE ARTISTA VISUAL] Prompts de imagem criados com sucesso.")

            # Etapa 2: Gerar as imagens com o modelo Imagen.
            print("\n[AGENTE ARTISTA VISUAL] Selecionando modelo Imagen e gerando imagens...")
            for i, prompt_item in enumerate(prompts_de_imagem):
                print(f"[AGENTE ARTISTA VISUAL] Gerando imagem {i+1}/{len(prompts_de_imagem)}...")
                
                # Garante que o prompt é um texto (string)
                if isinstance(prompt_item, dict) and 'prompt' in prompt_item:
                    prompt_final = prompt_item['prompt']
                else:
                    prompt_final = str(prompt_item)

                result = self.client.models.generate_images(
                    model="models/imagen-4.0-generate-001",
                    prompt=prompt_final 
                )

                if result.generated_images:
                    # O novo SDK tem um método .save() muito conveniente
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

