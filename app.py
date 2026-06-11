import streamlit as st
import easyocr
from PIL import Image
import numpy as np
import pandas as pd

# 1. Настройка на страницата
st.set_page_config(
    page_title="Анализатор на Съставки",
    page_icon="🥗",
    layout="centered"
)

# 2. OCR (кеширан)
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['bg', 'en'], gpu=False)

reader = load_ocr()

# 3. База данни
INGREDIENTS_DB = {
    "вредни": {
        "хидрогенирано растително масло": "Трансмазнини, повишават LDL холестерола.",
        "глюкозо-фруктозен сироп": "Води до инсулинова резистентност.",
        "натриев бензоат": "Консервант E211.",
        "калиев сорбат": "Консервант E202.",
        "захар": "Рафинирана захар.",
        "декстроза": "Бърз въглехидрат.",
        "глюкоза": "Проста захар."
    },
    "безвредни": {
        "пшенично брашно": "Основна съставка.",
        "ябълково брашно": "Естествен продукт.",
        "слънчогледово олио": "Мазнина за готвене.",
        "яйчен меланж": "Пастьоризирани яйца.",
        "амониев бикарбонат": "Набухвател.",
        "натриев бикарбонат": "Сода за хляб.",
        "лимонена киселина": "Регулатор на киселинност.",
        "суха млечна суроватка": "Млечен продукт.",
        "какао на прах": "Какао.",
        "какаова маса": "Шоколадова основа.",
        "соев лецитин": "Емулгатор.",
        "pgpr": "Емулгатор."
    },
    "полезни": {
        "ябълки": "Плод с фибри.",
        "канела": "Антиоксидант.",
        "аромат лимон": "Аромат."
    }
}

# 4. OCR корекции
SEARCH_MAPPING = {
    "хидрогенира": "хидрогенирано растително масло",
    "фруктозен": "глюкозо-фруктозен сироп",
    "ензоат": "натриев бензоат",
    "сорбат": "калиев сорбат",
    "захар": "захар",
    "декстро": "декстроза",
    "глюкоза": "глюкоза",
    "пшенично": "пшенично брашно",
    "слънчогледово": "слънчогледово олио",
    "меланж": "яйчен меланж",
    "амониев": "амониев бикарбонат",
    "натриев": "натриев бикарбонат",
    "лимонена": "лимонена киселина",
    "суроватка": "суха млечна суроватка",
    "какао": "какао на прах",
    "лецитин": "соев лецитин",
    "ябълка": "ябълки",
    "канела": "канела",
    "лимон": "аромат лимон"
}

# 5. UI
st.title("🥗 Анализатор на съставки")

uploaded_file = st.file_uploader("Качи снимка", type=["jpg", "jpeg", "png"])

if uploaded_file:

    image = Image.open(uploaded_file)
    st.image(image, use_container_width=True)

    with st.spinner("Разпознаване..."):

        img_np = np.array(image)

        results = reader.readtext(img_np, paragraph=True)

        text = " ".join([r[1] for r in results]).lower()

    st.subheader("Разпознат текст")
    st.write(text)

    found = []
    used = set()

    for k, v in SEARCH_MAPPING.items():
        if k in text and v not in used:

            for cat, items in INGREDIENTS_DB.items():

                if v in items:

                    found.append({
                        "Съставка": v,
                        "Категория": cat,
                        "Описание": items[v]
                    })

                    used.add(v)
                    break

    if found:

        df = pd.DataFrame(found)

        order = {"полезни": 0, "безвредни": 1, "вредни": 2}

        df["order"] = df["Категория"].map(order)

        df = df.sort_values("order").drop("order", axis=1)

        st.dataframe(df[["Съставка", "Категория"]], use_container_width=True)

        st.subheader("📖 Детайли")

        choice = st.selectbox("Избери съставка", df["Съставка"])

        row = df[df["Съставка"] == choice].iloc[0]

        if row["Категория"] == "вредни":
            st.error(row["Описание"])

        elif row["Категория"] == "полезни":
            st.success(row["Описание"])

        else:
            st.info(row["Описание"])

        st.subheader("🏆 Оценка")

        harmful = len(df[df["Категория"] == "вредни"])

        if harmful == 0:
            st.success("Няма открити вредни съставки.")
        elif harmful <= 2:
            st.warning("Има малко вредни съставки.")
        else:
            st.error("Има много вредни съставки.")

    else:
        st.warning("Не са открити съставки.")
