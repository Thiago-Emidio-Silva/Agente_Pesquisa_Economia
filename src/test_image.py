import os
from dotenv import load_dotenv
import google.genai as genai

def test_single_image():
    """
    Testa apenas a geração de uma única imagem, de forma isolada.
    """
    print("--- Iniciando Teste de Geração de Imagem Isolado ---")

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("ERRO: Chave 'GEMINI_API_KEY' não encontrada no .env")
        return

    try:
        # Inicializa o cliente com a chave
        client = genai.Client(api_key=api_key)
        print("Cliente GenAI inicializado.")

        # Um prompt de texto simples e direto
        prompt_simples = "um pato verde com um boné vermelho, estilo de desenho animado, fundo branco"
        print(f"Enviando prompt: '{prompt_simples}'")

        # A chamada de API que está causando o problema
        result = client.models.generate_images(
            model="models/imagen-4.0-generate-001",
            prompt=prompt_simples  # Passando a string diretamente
        )

        if result.generated_images:
            # O novo SDK tem um método .save() muito conveniente
            result.generated_images[0].image.save("teste_sucesso.png")
            print("\nSUCESSO! Imagem 'teste_sucesso.png' foi gerada e salva!")
        else:
            print("\nFALHA: Nenhuma imagem foi gerada.")
            if hasattr(result, 'rai_filtered_reason') and result.rai_filtered_reason:
                print(f"   Motivo do bloqueio: {result.rai_filtered_reason}")

    except Exception as e:
        print(f"\nERRO DURANTE O TESTE: {e}")

if __name__ == "__main__":
    test_single_image()