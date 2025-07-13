# mythicpersona_app_part1.py
import streamlit as st
from datetime import datetime, date
import os, sys
import pandas as pd
from dotenv import load_dotenv

USER_CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "...", "user_data.csv"))
STORY_CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "story_data.csv"))


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
env_path = os.path.join(ROOT_DIR, ".env")
load_dotenv(dotenv_path=env_path)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  


# Set paths
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_DIR)
from horo_module.horo_extractor import get_birth_profile

# Load environment
env_path = os.path.join(ROOT_DIR, ".env")
load_dotenv(dotenv_path=env_path)

# CSV Path
CSV_PATH = os.path.join(ROOT_DIR, "user_data.csv")

# Streamlit page config
st.set_page_config(page_title="MythicPersona", page_icon="🔮")
st.title("🔮 MythicPersona")
st.subheader("Decode Your Celestial Identity Through Astrology & Mythology")
st.divider()

# Session keys
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False

# 📋 Form: Birth Details
with st.form("user_info_form"):
    st.subheader("📋 Enter Your Birth Details")
    name = st.text_input("Full Name")
    dob = st.date_input("Date of Birth", min_value=date(1900, 1, 1), max_value=date.today())
    hour = st.selectbox("Hour (24-hr)", list(range(0, 24)), index=12)
    minute = st.selectbox("Minute", list(range(0, 60, 1)), index=0)
    place = st.text_input("Place of Birth (e.g. Jaipur, India)")
    submitted = st.form_submit_button("🔍 Reveal My Celestial Profile")

if submitted:
    tob = datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M").time()
    profile = get_birth_profile(dob, tob, place)

    if profile.get("error"):
        st.error(f"❌ Error: {profile['error']}")
    else:
        st.session_state.update({
            "form_submitted": True,
            "name": name,
            "dob": dob,
            "tob": tob,
            "place": place,
            "profile": profile
        })
        st.success(f"Welcome, {name} 🌟 Proceed to the questionnaire below.")


# mythicpersona_app_part2.py
import csv

if st.session_state.get("form_submitted", False):
    profile = st.session_state["profile"]
    with st.form("questionnaire_form"):
        st.subheader("🧠 Personality Questionnaire")
        questions = [
            ("Do you prefer solitude or social settings?", ["Solitude", "Social"]),
            ("When stressed, are you more likely to:", ["Withdraw", "Act out", "Stay calm"]),
            ("Do you value rules or freedom more?", ["Rules", "Freedom"]),
            ("Are you guided more by logic or emotion?", ["Logic", "Emotion"]),
            ("How do you react to conflict?", ["Avoid", "Confront", "Manipulate"]),
            ("Do you seek power, peace, or knowledge?", ["Power", "Peace", "Knowledge"]),
            ("Which do you fear most?", ["Rejection", "Loss", "Failure"]),
            ("Are your actions driven by duty or desire?", ["Duty", "Desire"]),
            ("Which describes you best?", ["Protector", "Creator", "Rebel", "Sage"]),
            ("Would you rather lead, follow, or stay unseen?", ["Lead", "Follow", "Unseen"]),
        ]
        answers = [st.radio(f"{i+1}. {q}", opts, key=f"q{i}") for i, (q, opts) in enumerate(questions)]
        submit_persona = st.form_submit_button("🧬 Discover My Mythic Persona")

    if submit_persona:
        from persona_engine.persona_matcher import match_persona

        row = [
            st.session_state["name"], st.session_state["dob"].isoformat(),
            st.session_state["tob"].strftime("%H:%M"), st.session_state["place"],
            profile.get("zodiac", {}).get("name", ""),
            profile.get("chandra_rasi", {}).get("name", ""),
            profile.get("nakshatra", {}).get("name", ""),
            profile.get("nakshatra", {}).get("lord", {}).get("name", ""),
            profile.get("nakshatra", {}).get("pada", ""),
            profile.get("chandra_rasi", {}).get("lord", {}).get("name", ""),
            profile.get("soorya_rasi", {}).get("name", ""),
            profile.get("soorya_rasi", {}).get("lord", {}).get("name", ""),
            profile.get("additional_info", {}).get("ganam", ""),
            profile.get("additional_info", {}).get("deity", ""),
            profile.get("additional_info", {}).get("animal_sign", ""),
            profile.get("additional_info", {}).get("nadi", ""),
            profile.get("additional_info", {}).get("color", ""),
            profile.get("additional_info", {}).get("birth_stone", ""),
            profile.get("additional_info", {}).get("symbol", ""),
            profile.get("additional_info", {}).get("planet", ""),
            profile.get("additional_info", {}).get("enemy_yoni", "")
        ] + answers

        user_headers = [
            "Name", "DOB", "TOB", "Place", "Zodiac", "Moon_Sign", "Nakshatra", "Nakshatra_Lord", "Pada",
            "Moon_Lord", "Sun_Sign", "Sun_Lord", "Ganam", "Deity", "Animal_Sign", "Nadi", "Color",
            "Birth_Stone", "Symbol", "Planet", "Enemy_Yoni"
        ] + [f"Q{i+1}" for i in range(10)]

        file_exists = os.path.exists(CSV_PATH)
        with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(user_headers)
            writer.writerow(row)

        st.session_state.persona_submitted = True
        st.rerun()
# mythicpersona_app_part3.py
import os
import json
import csv
import requests
import pyttsx3
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Paths
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
CSV_PATH = os.path.join(ROOT_DIR, "user_data.csv")
STORY_CSV_PATH = os.path.join(ROOT_DIR, "story_data.csv")

# Load OpenRouter API Key
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


if st.session_state.get("persona_submitted", False):
    # Go up one level from 'streamlit_app/' to reach 'MythicPersona/' root
    ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # CSVs stored in the root folder
    CSV_PATH = os.path.join(ROOT_DIR, "user_data.csv")
    STORY_CSV_PATH = os.path.join(ROOT_DIR, "story_data.csv")
    df = pd.read_csv(CSV_PATH)
    latest = df.iloc[-1]
    name = latest["Name"]
    traits = [latest["Zodiac"], latest["Moon_Sign"], latest["Nakshatra"], latest["Ganam"]]
    answers = [latest[f"Q{i+1}"] for i in range(10)]

    from persona_engine.persona_matcher import match_persona
    persona = match_persona()

    st.subheader("🌌 Your Astrological Profile")
    st.markdown(f"""
        - **Zodiac**: {latest['Zodiac']}
        - **Moon Sign**: {latest['Moon_Sign']} (Lord: {latest['Moon_Lord']})
        - **Nakshatra**: {latest['Nakshatra']} (Lord: {latest['Nakshatra_Lord']}, Pada: {latest['Pada']})
        - **Sun Sign**: {latest['Sun_Sign']} (Lord: {latest['Sun_Lord']})
        - **Ganam**: {latest['Ganam']}, **Deity**: {latest['Deity']}
        - **Animal Sign**: {latest['Animal_Sign']}, **Planet**: {latest['Planet']}
        - **Color**: {latest['Color']}, **Birth Stone**: {latest['Birth_Stone']}
        - **Symbol**: {latest['Symbol']}, **Enemy Yoni**: {latest['Enemy_Yoni']}
        """)  # Use full markdown like before

    st.subheader("🧬 Your Mythic Persona Alignment")
    st.markdown(f"""
        ### 🛕 Guardian Deities
        - **Hindu**: {persona['guardian_deity_hindu']}
        - **Greek**: {persona['guardian_deity_greek']}
        - **Norse**: {persona['guardian_deity_norse']}

        ### 👹 Shadow Counterparts
        - **Hindu Asura**: {persona['guardian_devil_hindu']}
        - **Greek Devil**: {persona['guardian_devil_greek']}
        - **Norse Devil**: {persona['guardian_devil_norse']}

        ### 🐉 Mythical Animal
        - **Guardian Beast**: {persona['mythical_animal']}
        """)
# Load last saved data

def generate_mythic_story(name, answers, traits, persona):
    trait_text = ", ".join(traits)
    core_trait = answers[7] if len(answers) > 7 else "a deep trait"
    deity_hindu = persona.get("guardian_deity_hindu", "a Hindu deity")
    deity_greek = persona.get("guardian_deity_greek", "a Greek god")
    deity_norse = persona.get("guardian_deity_norse", "a Norse god")

    devil_hindu = persona.get("guardian_devil_hindu", "a Hindu devil")
    devil_greek = persona.get("guardian_devil_greek", "a Greek devil")
    devil_norse = persona.get("guardian_devil_norse", "a Norse devil")

    animal = persona.get("mythical_animal", "a mythic beast")

    prompt = f"""
Write a 500-word mythological origin story in exactly 7 poetic paragraphs about a person named {name}.
They are guided by three guardian deities: {deity_hindu} (Hindu), {deity_greek} (Greek), and {deity_norse} (Norse).
They are challenged by three shadow devils: {devil_hindu} (Hindu), {devil_greek} (Greek), and {devil_norse} (Norse).
They are protected by a mythical beast: {animal}.
The person's core trait is '{core_trait}'.

Use rich symbolic language, ancient mythic tone, vivid imagery.
Write only the 7 paragraphs, no titles or extra commentary.
"""

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "MythicPersona"
        }
        body = {
            "model": "mistralai/mistral-small-3.2-24b-instruct:free",
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                 headers=headers, data=json.dumps(body))

        result = response.json()
       
        if "choices" not in result:
            raise Exception(f"Invalid response from OpenRouter: {result}")
    
     
        content = result["choices"][0]["message"]["content"]

        print("\n📜 Full 7-Part Mythic Story:\n")
        for i, para in enumerate(content.split("\n\n")):
            print(f"Part {i+1}:\n{para.strip()}\n")

        return [p.strip() for p in content.split("\n\n") if p.strip()]

    except Exception as e:
        print("⚠️ OpenRouter fallback error:", e)
        return [f"[Unavailable: {str(e)}]"] * 7


# 📜 Story Generation
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# CSVs stored in the root folder
CSV_PATH = os.path.join(ROOT_DIR, "user_data.csv")
STORY_CSV_PATH = os.path.join(ROOT_DIR, "story_data.csv")
df = pd.read_csv(CSV_PATH)
latest = df.iloc[-1]
traits = [latest["Zodiac"], latest["Moon_Sign"], latest["Nakshatra"], latest["Ganam"]]
name = latest["Name"]
answers = [latest[f"Q{i+1}"] for i in range(10)]

traits = [latest["Zodiac"], latest["Moon_Sign"], latest["Nakshatra"], latest["Ganam"]]
from persona_engine.persona_matcher import match_persona
persona = match_persona()
story_parts = generate_mythic_story(name, answers, traits, persona)
while len(story_parts) < 7:
    story_parts.append("[Unavailable]")
header = ["Name", "DOB"] + [f"Mythic_Part_{i+1}" for i in range(7)]
row = [name, dob] + story_parts

# Save to story_data.csv
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# CSVs stored in the root folder
CSV_PATH = os.path.join(ROOT_DIR, "user_data.csv")
STORY_CSV_PATH = os.path.join(ROOT_DIR, "story_data.csv")
write_header = not os.path.exists(STORY_CSV_PATH)
with open(STORY_CSV_PATH, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    if write_header:
        writer.writerow(header)
    writer.writerow(row)


import streamlit as st
from PIL import Image
import pandas as pd
import os

# 📁 Set up paths
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STORY_CSV_PATH = os.path.join(ROOT_DIR, "story_data.csv")
IMAGE_DIR = os.path.join(ROOT_DIR, "generated_images")

# 🛑 Stop if story CSV does not exist or is empty
if not os.path.exists(STORY_CSV_PATH):
    st.stop()

story_df = pd.read_csv(STORY_CSV_PATH)
if story_df.empty:
    st.stop()

# 🧠 Get current user's identity from session state
current_name = st.session_state.get("name")
current_dob = st.session_state.get("dob")

if not current_name or not current_dob:
    st.warning("Please generate your story first.")
    st.stop()

# 🔍 Find latest story entry for this specific user
user_rows = story_df[
    (story_df["Name"] == current_name) &
    (story_df["DOB"] == str(current_dob))
]

if user_rows.empty:
    st.warning("No story found for the current user.")
    st.stop()

latest_story = user_rows.iloc[-1]  # ✅ Use latest match for that user
story_parts = [latest_story.get(f"Mythic_Part_{i+1}", "[Missing Part]") for i in range(7)]

# 🎭 Display story paragraphs + images
st.subheader("📖 Your Mythical Origin Story")

for i, paragraph in enumerate(story_parts):
    st.markdown(f"### ✨ Part {i+1}")
    st.markdown(paragraph)

    img_path = os.path.join(IMAGE_DIR, f"manual_slide_{i+1}.jpg")
    if os.path.exists(img_path):
        st.image(Image.open(img_path), caption=f"Slide {i+1}", use_container_width=True)
    else:
        st.warning(f"⚠️ Missing image for Part {i+1}: manual_slide_{i+1}.jpg")


import streamlit as st
import pandas as pd
import os
from io import StringIO

# ✅ Setup
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STORY_CSV_PATH = os.path.join(ROOT_DIR, "story_data.csv")

# 🧠 Get user identity
current_name = st.session_state.get("name")
current_dob = st.session_state.get("dob")

st.subheader("📤 Download Your Mythic Story")

# 🛑 Validate
if not current_name or not current_dob:
    st.info("Please generate a story to export it.")
    st.stop()

if not os.path.exists(STORY_CSV_PATH):
    st.warning("Story file not found.")
    st.stop()

story_df = pd.read_csv(STORY_CSV_PATH)
user_rows = story_df[
    (story_df["Name"] == current_name) & (story_df["DOB"] == str(current_dob))
]

if user_rows.empty:
    st.warning("No story found for current user.")
    st.stop()

latest_story = user_rows.iloc[-1]

# 📄 Prepare plain text story
story_text = f"🧍 Name: {latest_story['Name']}\n📅 DOB: {latest_story['DOB']}\n\n"
for i in range(7):
    story_text += f"✨ Part {i+1}:\n{latest_story.get(f'Mythic_Part_{i+1}', '')}\n\n"

# 📥 Download button
st.download_button(
    label="📥 Download Your Mythic Story (Text File)",
    data=story_text,
    file_name=f"{current_name.replace(' ', '_')}_mythic_story.txt",
    mime="text/plain"
)
