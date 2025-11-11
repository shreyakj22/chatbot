import google.generativeai as genai

# 1️⃣ Configure your Gemini API key
genai.configure(api_key="AIzaSyAkc-nGXq2Mtgq_6qlKYmaVPdzpacV6u2k")

# 2️⃣ Choose a model
model = genai.GenerativeModel("models/gemini-2.5-flash")

# 3️⃣ Generate a response
response = model.generate_content("Hello! How are you today?")
print("Gemini says:", response.text)
