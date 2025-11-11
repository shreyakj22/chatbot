import google.generativeai as genai

genai.configure(api_key="AIzaSyAkc-nGXq2Mtgq_6qlKYmaVPdzpacV6u2k")  # Replace with your actual Gemini API key

for model in genai.list_models():
    print(model.name)
