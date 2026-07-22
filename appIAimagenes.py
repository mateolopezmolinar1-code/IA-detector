import streamlit as st
from PIL import Image
import requests
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io
import base64
import json
import numpy as np



# ==========================
# CONFIGURACIÓN API
# ==========================

API_USER = "211833634"
API_SECRET = "RYx8neMxuNnmyuxY7pmt4u6gBw3yfKbP"





# ==========================
# CONFIGURACIÓN STREAMLIT
# ==========================

st.set_page_config(
    page_title="Detector IA",
    page_icon="🤖",
    layout="centered"
)


st.title("🤖 Detector de Imágenes IA")

st.image(
    "portada.png",
    use_container_width=True
)


st.write(
    "Detecta probabilidad de IA y analiza posibles modificaciones."
)



# ==========================
# SUBIR IMAGEN
# ==========================

uploaded = st.file_uploader(
    "📎 Sube una imagen",
    type=[
        "jpg",
        "jpeg",
        "png",
        "webp"
    ]
)



if uploaded:


    image = Image.open(
        uploaded
    ).convert(
        "RGB"
    )


    st.session_state["image"] = image


    st.image(
        image,
        caption="Imagen original",
        use_container_width=True
    )

    if uploaded:

        # ==========================================
    # BOTÓN 1 - ANALIZAR SI ES IA
    # ==========================================

        if st.button("🧠 Analizar si es IA"):


            with st.spinner("Analizando imagen..."):


                try:

                    files = {
                        "media": (
                            uploaded.name,
                            uploaded.getvalue(),
                            uploaded.type
                        )
                    }


                    data = {
                        "models": "genai",
                        "api_user": API_USER,
                        "api_secret": API_SECRET
                    }


                    response = requests.post(
                        "https://api.sightengine.com/1.0/check.json",
                        data=data,
                        files=files
                    )


                    resultado = response.json()



                    if "type" in resultado:


                        porcentaje = (
                            resultado["type"]["ai_generated"]
                            * 100
                        )


                        st.session_state["porcentaje"] = porcentaje



                        st.divider()


                        st.subheader(
                            "📊 Resultado"
                        )


                        st.metric(
                            "Probabilidad de IA",
                            f"{porcentaje:.2f}%"
                        )


                        st.progress(
                            min(
                                int(porcentaje),
                                100
                            )
                        )



                        if porcentaje >= 75:

                            st.error(
                                "🧠 Muy probablemente generada por IA"
                            )


                        elif porcentaje >= 45:

                            st.warning(
                                "⚠️ Posiblemente generada por IA"
                            )


                        elif porcentaje >= 25:

                            st.info(
                                "🤔 Difícil de determinar"
                            )


                        else:

                            st.success(
                                "✅ Probablemente imagen real"
                            )



                    else:

                        st.error(
                            "La API no devolvió resultado"
                        )

                        st.json(
                            resultado
                        )



                except Exception as e:


                    st.error(
                        "Error conectando con Sightengine:"
                    )

                    st.write(
                        e
                    )



        # Mostrar último resultado guardado

        if "porcentaje" in st.session_state:


            st.divider()


            st.caption(
                f"Último análisis: {st.session_state['porcentaje']:.2f}% IA"
            )



            if uploaded:

                    # ==========================================
    # BOTÓN 2 - DETECTAR MODIFICACIONES
    # ==========================================


                    if st.button("🔎 Detectar zonas sospechosas"):


                        with st.spinner("Analizando zonas de la imagen..."):


                            try:


                                img = np.array(image)


                                alto, ancho, _ = img.shape



                                # Ajuste automático de cuadrícula
                                tamaño = max(
                                    ancho,
                                    alto
                                ) // 8



                                resultados = []



                                for y in range(
                                    0,
                                    alto,
                                    tamaño
                                ):


                                    for x in range(
                                        0,
                                        ancho,
                                        tamaño
                                    ):


                                        x2 = min(
                                            x+tamaño,
                                            ancho
                                        )

                                        y2 = min(
                                            y+tamaño,
                                            alto
                                        )


                                        recorte = image.crop(
                                            (
                                                x,
                                                y,
                                                x2,
                                                y2
                                            )
                                        )


                                        buffer = io.BytesIO()


                                        recorte.save(
                                            buffer,
                                            format="PNG"
                                        )


                                        buffer.seek(0)



                                        files = {

                                            "media":
                                            (
                                                "zona.png",
                                                buffer.getvalue(),
                                                "image/png"
                                            )

                                        }



                                        data = {

                                            "models":"genai",

                                            "api_user":API_USER,

                                            "api_secret":API_SECRET

                                        }



                                        respuesta = requests.post(

                                            "https://api.sightengine.com/1.0/check.json",

                                            data=data,

                                            files=files

                                        )



                                        datos = respuesta.json()



                                        if "type" in datos:


                                            ia = (

                                                datos["type"]["ai_generated"]

                                                *100

                                            )


                                        else:

                                            ia = 0



                                        resultados.append(

                                            {

                                            "x":x,

                                            "y":y,

                                            "x2":x2,

                                            "y2":y2,

                                            "ia":ia

                                            }

                                        )



                                # Dibujar mapa


                                fig, ax = plt.subplots(
                                    figsize=(8,8)
                                )


                                ax.imshow(
                                    image
                                )



                                for zona in resultados:


                                    ia = zona["ia"]



                                    if ia >= 75:

                                        color="red"


                                    elif ia >= 40:

                                        color="orange"


                                    else:

                                        color="green"



                                    cuadro = patches.Rectangle(

                                        (

                                        zona["x"],

                                        zona["y"]

                                        ),

                                        zona["x2"]-zona["x"],

                                        zona["y2"]-zona["y"],

                                        linewidth=1,

                                        edgecolor=color,

                                        facecolor=color,

                                        alpha=0.25

                                    )



                                    ax.add_patch(
                                        cuadro
                                    )


                                ax.axis(
                                    "off"
                                )


                                st.subheader(
                                    "🗺️ Mapa de probabilidad IA"
                                )


                                st.pyplot(
                                    fig
                                )


                            except Exception as e:


                                st.error(
                                    "Error analizando zonas:"
                                )

                                st.write(
                                    e
                                )
