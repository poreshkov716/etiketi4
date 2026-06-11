
import streamlit as st
import easyocr
from PIL import Image
import numpy as np
import pandas as pd

st.set_page_config(
    page_title="Анализатор на съставки",
    page_icon="🥗",
    layout="centered"
)

@st.cache_resource
def load_reader():
    return easyocr.Reader(['bg', 'en'])

reader = load_reader()

INGREDIENTS = {
    "захар": ("Вредни", "Рафинирана захар."),
    "глюкоза": ("Вредни", "Проста захар."),
    "декстроза": ("Вредни", "Бърз въглехидрат."),
    "канела": ("Полезни", "Богата на антиоксиданти."),
    "ябълки": ("Полезни", "Съдържат фибри."),
    "пшенично": ("Безвредни", "Пшенично брашно."),
    "лецитин": ("Безвредни", "Емулгатор E322.")
}

st.title("🥗 Анализатор на Съставки")

uploaded_file = st.file_uploader(
    "Качи снимка на етикет",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(image, use_container_width=True)

    with st.spinner("Разпознаване на текст..."):

        img_np = np.array(image)

        result = reader.readtext(
            img_np,
            paragraph=True
        )

        text = " ".join(result).lower()

    st.subheader("Разпознат текст")

    st.write(text)

    found = []

    for ingredient in INGREDIENTS:

        if ingredient in text:

            category, description = INGREDIENTS[ingredient]

            found.append({
                "Съставка": ingredient,
                "Категория": category,
                "Описание": description
            })

    if found:

        df = pd.DataFrame(found)

        st.subheader("Намерени съставки")

        st.dataframe(
            df[["Съставка", "Категория"]],
            use_container_width=True
        )

        selected = st.selectbox(
            "Избери съставка",
            df["Съставка"]
        )

        row = df[df["Съставка"] == selected].iloc[0]

        st.info(row["Описание"])

    else:

        st.warning(
            "Не са открити познати съставки."
        )
```
