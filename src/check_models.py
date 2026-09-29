import os
import google.generativeai as genai
from dotenv import load_dotenv

print("--- Iniciando Diagnóstico de Modelos ---")

# Carrega a chave de API do arquivo .env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("ERRO: Chave de API não encontrada. Verifique seu arquivo .env")
else:
    try:
        genai.configure(api_key=api_key)
        print("Chave de API configurada com sucesso.\n")
        print("Modelos disponíveis para esta chave:")
        print("------------------------------------")

        # Itera sobre todos os modelos disponíveis
        for m in genai.list_models():
            # Verifica se o modelo suporta o método 'generateContent' que estamos usando
            if 'generateContent' in m.supported_generation_methods:
                # Imprime as informações do modelo
                print(f"Nome do Modelo: {m.name}")
                print(f"  - Descrição: {m.description}")
                print(f"  - Métodos Suportados: {m.supported_generation_methods}\n")

        print("------------------------------------")
        print("Diagnóstico concluído.")

    except Exception as e:
        print(f"Ocorreu um erro ao conectar à API: {e}")