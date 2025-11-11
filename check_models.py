import google.generativeai as genai

# Replace with your actual Gemini API key
genai.configure(api_key="AIzaSyAkc-nGXq2Mtgq_6qlKYmaVPdzpacV6u2k")

for model in genai.list_models():
    print(model.name)
