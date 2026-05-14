# app.py
# AI OCR Food Scanner with Health Analysis

import streamlit as st
import easyocr
import numpy as np
from PIL import Image, ImageEnhance
import re

# =========================
# НАСТРОЙКИ
# =========================

st.set_page_config(
    page_title="AI Food Scanner",
    page_icon="🧾",
    layout="centered"
)

st.title("🧾 AI Food Label Scanner")
st.write("Сканирай хранителни етикети и анализирай съставките.")

# =========================
# ЗДРАВЕН ПРОФИЛ
# =========================

st.subheader("🩺 Здравен профил")

selected_conditions = st.multiselect(
    "Изберете здравословни състояния:",
    [
        "Диабет тип 1",
        "Диабет тип 2",
        "Автоимунен тиреоидит",
        "Цьолиакия",
        "Лупус",
        "Ревматоиден артрит",
        "Високо кръвно налягане",
        "Сърдечни проблеми",
        "Лактозна непоносимост",
        "Алергии"
    ]
)

if selected_conditions:
    st.info(f"Избрани състояния: {', '.join(selected_conditions)}")
else:
    st.info("Няма избрани заболявания.")

# =========================
# ВРЕДНИ СЪСТАВКИ
# =========================

harmful_ingredients = {

    "e621": {
        "name": "Мононатриев глутамат",

        "healthy_alternative": "Подправки и естествени билки",

        "risks": {
            "Автоимунен тиреоидит": "Може да засили възпалението",
            "Високо кръвно налягане": "Съдържа високо количество натрий"
        }
    },

    "e250": {
        "name": "Натриев нитрит",

        "healthy_alternative": "Прясно месо без консерванти",

        "risks": {
            "Сърдечни проблеми": "Свързва се с повишен риск за сърцето"
        }
    },

    "e951": {
        "name": "Аспартам",

        "healthy_alternative": "Стевия",

        "risks": {
            "Диабет тип 2": "Изкуствен подсладител",
            "Автоимунен тиреоидит": "Възможна чувствителност"
        }
    },

    "палмово масло": {
        "name": "Palm Oil",

        "healthy_alternative": "Зехтин или слънчогледово масло",

        "risks": {
            "Сърдечни проблеми": "Съдържа наситени мазнини",
            "Диабет тип 2": "Често присъства в силно преработени храни"
        }
    },

    "palm oil": {
        "name": "Palm Oil",

        "healthy_alternative": "Зехтин или слънчогледово масло",

        "risks": {
            "Сърдечни проблеми": "Съдържа наситени мазнини",
            "Диабет тип 2": "Често присъства в силно преработени храни"
        }
    },

    "захар": {
        "name": "Sugar",

        "healthy_alternative": "Стевия или плодове",

        "risks": {
            "Диабет тип 2": "Повишава кръвната захар"
        }
    },

    "sugar": {
        "name": "Sugar",

        "healthy_alternative": "Стевия или плодове",

        "risks": {
            "Диабет тип 2": "Повишава кръвната захар"
        }
    },

    "глутен": {
        "name": "Gluten",

        "healthy_alternative": "Безглутенови продукти",

        "risks": {
            "Цьолиакия": "Може да предизвика реакция"
        }
    },

    "gluten": {
        "name": "Gluten",

        "healthy_alternative": "Безглутенови продукти",

        "risks": {
            "Цьолиакия": "Може да предизвика реакция"
        }
    },

    "лактоза": {
        "name": "Lactose",

        "healthy_alternative": "Безлактозни продукти",

        "risks": {
            "Лактозна непоносимост": "Може да причини дискомфорт"
        }
    },

    "lactose": {
        "name": "Lactose",

        "healthy_alternative": "Безлактозни продукти",

        "risks": {
            "Лактозна непоносимост": "Може да причини дискомфорт"
        }
    }
}

# =========================
# ИЗБОР НА ЕЗИК
# =========================

language_option = st.selectbox(
    "🌍 Изберете OCR език:",
    ["Български + Английски", "Само Английски"]
)

if language_option == "Български + Английски":
    languages = ['bg', 'en']
else:
    languages = ['en']

# =========================
# OCR МОДЕЛ
# =========================

@st.cache_resource
def load_reader(lang_list):
    return easyocr.Reader(lang_list)

reader = load_reader(languages)

# =========================
# КАЧВАНЕ НА СНИМКА
# =========================

uploaded_file = st.file_uploader(
    "📂 Качи изображение",
    type=["png", "jpg", "jpeg"]
)

# =========================
# КАМЕРА
# =========================

camera_image = st.camera_input("📸 Направи снимка")

image_source = None

if uploaded_file is not None:
    image_source = uploaded_file

elif camera_image is not None:
    image_source = camera_image

# =========================
# OCR ОБРАБОТКА
# =========================

if image_source is not None:

    image = Image.open(image_source)

    st.image(image, caption="Избрано изображение", use_container_width=True)

    # Подобряване на контраста
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)

    # NumPy
    image_np = np.array(image)

    st.write("⏳ Разпознаване на текст...")

    # OCR
    results = reader.readtext(image_np)

    extracted_text = " ".join([result[1] for result in results])

    st.subheader("📄 Разпознат текст")
    st.write(extracted_text)

    # =========================
    # ЦВЕТНО МАРКИРАНЕ
    # =========================

    highlighted_text = extracted_text

    for ingredient in harmful_ingredients.keys():

        pattern = re.compile(re.escape(ingredient), re.IGNORECASE)

        highlighted_text = pattern.sub(
            f"🔴 {ingredient.upper()} 🔴",
            highlighted_text
        )

    st.subheader("🎨 Маркирани опасни съставки")
    st.write(highlighted_text)

    # =========================
    # АНАЛИЗ НА СЪСТАВКИТЕ
    # =========================

    found_ingredients = []

    lower_text = extracted_text.lower()

    for ingredient, info in harmful_ingredients.items():

        if ingredient in lower_text:

            matched_conditions = []

            for condition in selected_conditions:

                if condition in info["risks"]:

                    matched_conditions.append({
                        "condition": condition,
                        "message": info["risks"][condition]
                    })

            found_ingredients.append({
                "ingredient": ingredient,
                "name": info["name"],
                "warnings": matched_conditions
            })

    # =========================
    # HEALTH SCORE
    # =========================

    risk_score = 0

    for item in found_ingredients:
        risk_score += len(item["warnings"])

    health_score = max(0, 100 - (risk_score * 15))

    # =========================
    # ПОКАЗВАНЕ НА HEALTH SCORE
    # =========================

    st.subheader("📈 Health Score")

    if health_score >= 80:
        st.success(f"🟢 {health_score}/100 → Отличен продукт")

    elif health_score >= 60:
        st.warning(f"🟡 {health_score}/100 → Умерен риск")

    else:
        st.error(f"🔴 {health_score}/100 → Нездравословен продукт")

    # =========================
    # РЕЗУЛТАТИ
    # =========================

    st.subheader("⚠️ Анализ на хранителните съставки")

    if found_ingredients:

        for item in found_ingredients:

            st.error(
                f"Открито: {item['ingredient']} → {item['name']}"
            )

            if item["warnings"]:

                for warning in item["warnings"]:

                    st.warning(
                        f"{warning['condition']} → {warning['message']}"
                    )

            else:
                st.info(
                    "Няма специфичен риск за избраните състояния."
                )

            st.info(
                f"🥗 По-здравословна алтернатива: "
                f"{harmful_ingredients[item['ingredient']]['healthy_alternative']}"
            )

    else:
        st.success("✅ Не са открити рискови съставки.")

# =========================
# ИНФОРМАЦИЯ
# =========================

with st.expander("ℹ️ Използвани технологии"):

    st.markdown("""
    ### Streamlit
    Създава уеб приложението.

    ### EasyOCR
    AI модел за разпознаване на текст.

    ### Pillow (PIL)
    Обработка и подобрение на изображения.

    ### NumPy
    Работа с изображения като числови масиви.
    """)

with st.expander("📚 Източници за хранителни добавки"):

    st.markdown("""
    - Списъци с E-номера
    - Статии за хранителни добавки
    - Надеждни здравни сайтове

    Примерни търсения:
    - "E numbers list harmful"
    - "вредни хранителни добавки"
    """)
