import streamlit as st
from groq import Groq
import requests
from urllib.parse import quote
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="AI Social Media Manager", layout="wide")
st.title("📱 AI Social Media Manager")
st.write("ഒരു വാചകം നൽകൂ, AI നിങ്ങൾക്ക് വേണ്ടി പോസ്റ്റും ചിത്രവും ഉണ്ടാക്കാം!")

# API Keys
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

if not GROQ_API_KEY:
    st.warning("Groq API Key ലഭ്യമല്ല. ദയവായി Secrets പരിശോധിക്കുക.")

# Input from user
business_type = st.text_input("നിങ്ങളുടെ ബിസിനസ്സ് എന്താണ്? (ഉദാ: Supermarket, Restaurant, Clothing Store)")
prompt = st.text_area("ഇന്ന് നിങ്ങൾ പോസ്റ്റ് ചെയ്യാൻ ആഗ്രഹിക്കുന്ന കാര്യം എഴുതുക:", 
                      placeholder="ഉദാ: ഇന്ന് ഓറഞ്ചിന് 20% ഓഫർ ഉണ്ട്.")

if st.button("Generate Post 🚀"):
    if prompt and business_type:
        with st.spinner("AI നിങ്ങളുടെ പോസ്റ്റ് ഉണ്ടാക്കുന്നു..."):
            try:
                client = Groq(api_key=GROQ_API_KEY)
                
                # 1. AI വഴി ക്യാപ്ഷൻ ഉണ്ടാക്കുന്നു
                system_msg = "You are an expert social media manager. Create a short, catchy, and engaging social media caption (with emojis and hashtags) based on the user's prompt. Output in Malayalam and English."
                
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": f"Business: {business_type}. Offer: {prompt}"}
                    ],
                    model="openai/gpt-oss-120b",
                )
                caption = chat_completion.choices[0].message.content
                
                # 2. AI വഴി ചിത്രം ഉണ്ടാക്കുന്നു (Pollinations.ai - 100% Free)
                img_prompt = f"A professional advertisement for a {business_type}. {prompt}. High quality, vibrant colors, 4k."
                encoded_prompt = quote(img_prompt)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
                
                # ചിത്രം ഡൗൺലോഡ് ചെയ്യുന്നു
                response = requests.get(image_url)
                img = Image.open(BytesIO(response.content))
                
                # Output കാണിക്കുന്നു
                st.success("പോസ്റ്റ് തയ്യാറായി!")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("🖼️ Generated Image")
                    st.image(img, use_column_width=True)
                    
                    # ഡൗൺലോഡ് ബട്ടൺ
                    buf = BytesIO()
                    img.save(buf, format="PNG")
                    st.download_button("⬇️ Download Image", buf.getvalue(), "social_post.png", "image/png")
                    
                with col2:
                    st.subheader("📝 Caption")
                    st.text_area("Copy this text:", value=caption, height=300)
                    st.info("ഈ ചിത്രവും ടെക്സ്റ്റും ഉപയോഗിച്ച് നിങ്ങൾക്ക് Instagram, Facebook, WhatsApp Status എന്നിവയിൽ പോസ്റ്റ് ചെയ്യാം.")

            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("ദയവായി ബിസിനസ്സിന്റെ പേരും ഓഫറും എഴുതി നൽകുക!")