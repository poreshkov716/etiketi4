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
    # Използваме GPU=False за съвместимост, ако хостваш в Streamlit Community Cloud
    return easyocr.Reader(['bg', 'en'], gpu=False)

reader = load_ocr()

# 3. База данни със съставки
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

# Сплескваме базата данни за по-лесно търсене и я сортираме по дължина на името (низходящо)
# Това помага "глюкозо-фруктозен сироп" да се провери ПРЕДИ "глюкоза"
ALL_INGREDIENTS = []
for cat, items in INGREDIENTS_DB.items():
    for name, desc in items.items():
        ALL_INGREDIENTS.append({"name": name, "category": cat, "description": desc})

ALL_INGREDIENTS.sort(key=lambda x: len(x["name"]), reverse=True)


# 4. Потребителски интерфейс
st.title("🥗 Анализатор на съставки")
st.write("Качете снимка на етикета със съставки, за да ги анализираме.")

uploaded_file = st.file_uploader("Качи снимка", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, use_container_width=True)

    with st.spinner("Разпознаване на текст от изображението..."):
        img_np = np.array(image)
        results = reader.readtext(img_np, paragraph=True)
        text = " ".join([r[1] for r in results]).lower()

    # Показваме разпознатия текст в сгъващо се меню, за да не заема място
    with st.expander("🔍 Виж разпознатия текст от сканирането"):
        st.write(text)

    # Търсене на съставки
    found = []
    text_to_search = text
    
    for item in ALL_INGREDIENTS:
        if item["name"] in text_to_search:
            found.append({
                "Съставка": item["name"],
                "Категория": item["category"],
                "Описание": item["description"]
            })
            # Премахваме намерената съставка от текста, за да не се засичат по-къси нейни съвпадения
            text_to_search = text_to_search.replace(item["name"], "")

    if found:
        df = pd.DataFrame(found)

        # Сортиране по категории (Полезни -> Безвредни -> Вредни)
        order = {"полезни": 0, "безвредни": 1, "вредни": 2}
        df["order"] = df["Категория"].map(order)
        df = df.sort_values("order").drop("order", axis=1)

        # Създаване на табове за по-добро потребителско изживяване
        tab1, tab2, tab3 = st.tabs(["📊 Резултати", "📖 Детайли", "🏆 Оценка"])

        with tab1:
            st.subheader("Открити съставки")
            # Оцветяване на таблицата според категорията (опционално, за прегледност)
            st.dataframe(df[["Съставка", "Категория"]], use_container_width=True)

        with tab2:
            st.subheader("Детайлно описание")
            choice = st.selectbox("Избери съставка, за да научиш повече:", df["Съставка"])
            row = df[df["Съставка"] == choice].iloc[0]

            if row["Категория"] == "вредни":
                st.error(f"**{row['Съставка']}**: {row['Описание']}")
            elif row["Категория"] == "полезни":
                st.success(f"**{row['Съставка']}**: {row['Описание']}")
            else:
                st.info(f"**{row['Съставка']}**: {row['Описание']}")

        with tab3:
            st.subheader("Обща оценка на продукта")
            harmful_count = len(df[df["Категория"] == "вредни"])
            healthy_count = len(df[df["Категория"] == "полезни"])

            if harmful_count == 0:
                st.success(f"🎉 Чудесно! Не са открити вредни съставки. Продуктът съдържа {healthy_count} полезни компоненти.")
            elif harmful_count <= 2:
                st.warning(f"⚠️ Внимание! Продуктът съдържа {harmful_count} съставки, които е добре да избягваш.")
            else:
                st.error(f"🚨 Не се препоръчва! Открити са {harmful_count} вредни съставки. Помисли за по-здравословна алтернатива.")
    else:
        st.warning("Не можахме да разпознаем познати съставки. Опитай с по-чиста или по-добре осветена снимка.")
