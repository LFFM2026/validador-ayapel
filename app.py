import streamlit as st
import qrcode
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
import io
import os

# 1. Configuración de página
st.set_page_config(page_title="Validador Ayapel", page_icon="🛡️", layout="centered")

# 2. Estética de Caja Flotante
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    .block-container {
        background-color: white !important;
        padding: 40px !important;
        border-radius: 25px !important;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.1) !important;
        margin-top: 50px !important;
        max-width: 650px !important;
    }
    .verde-ayapel {
        color: #04D918 !important;
        font-family: 'Arial', sans-serif !important;
        font-weight: bold !important;
        text-align: center !important;
    }
    .caja-verificacion {
        background-color: #f9fff9;
        border: 2px solid #04D918;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE NAVEGACIÓN ---
query_params = st.query_params

if "validar" in query_params:
    # --- VISTA CIUDADANO ---
    id_doc = query_params.get("validar")
    url_doc = query_params.get("url")
    
    col1, col2, col3 = st.columns([1,0.5,1])
    with col2:
        if os.path.exists("escudo.png"): st.image("escudo.png", width=120)

    st.markdown('<h2 class="verde-ayapel">ALCALDÍA DE AYAPEL</h2>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="caja-verificacion">
        <h3 style="color: #1b5e20;">✅ DOCUMENTO ORIGINAL VERIFICADO</h3>
        <p style="font-size: 18px;"><b>Proceso ID:</b> {id_doc}</p>
        <hr style="border: 0.5px solid #04D918;">
        <p style="font-size: 16px; color: #333; line-height: 1.5;">
            Este documento es <b>original</b> y en su expediente en físico este documento 
            se encuentra firmado a <b>puño y letra</b>. La versión digital cargada en 
            SECOP I es fiel copia del original que reposa en los archivos de la Alcaldía.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.link_button("📂 ABRIR DOCUMENTO ORIGINAL (DRIVE)", url_doc, use_container_width=True)

else:
    # --- VISTA ADMINISTRADOR (TÚ) ---
    col1, col2, col3 = st.columns([1,0.5,1])
    with col2:
        if os.path.exists("escudo.png"): st.image("escudo.png", width=140)

    st.markdown('<p class="verde-ayapel" style="font-size: 24px;">ALCALDIA DE AYAPEL CORDOBA</p>', unsafe_allow_html=True)
    st.markdown('<p class="verde-ayapel" style="font-size: 20px;">VALIDADOR DE DOCUMENTOS SECOP 1</p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    archivo = st.file_uploader("📂 1. Suba el documento PDF", type="pdf")
    id_proc = st.text_input("📝 2. Ingrese el ID del Proceso")
    link_drive = st.text_input("🔗 3. Pegue el Link de Drive")

    if st.button("🚀 GENERAR DOCUMENTO VALIDADO", use_container_width=True):
        if archivo and id_proc and link_drive:
            # Obtener la URL de la app automáticamente
            base_url = "https://tu-app.streamlit.app" # Se actualizará al desplegar
            url_portal = f"{base_url}/?validar={id_proc}&url={link_drive}"
            
            qr = qrcode.make(url_portal)
            img_buffer = io.BytesIO()
            qr.save(img_buffer, format="PNG")
            
            packet = io.BytesIO()
            can = canvas.Canvas(packet)
            can.drawInlineImage(qr, 480, 40, width=75, height=75)
            can.setFont("Helvetica-Bold", 8)
            can.drawString(50, 65, "CERTIFICACIÓN DE ORIGINALIDAD")
            can.setFont("Helvetica", 7)
            can.drawString(50, 55, f"ID: {id_proc}. Documento original firmado a puño y letra.")
            can.drawString(50, 47, "Escanee el código QR para verificar autenticidad.")
            can.save()
            
            reader = PdfReader(archivo)
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            writer.pages[-1].merge_page(PdfReader(io.BytesIO(packet.getvalue())).pages[0])
            
            out = io.BytesIO()
            writer.write(out)
            st.success("✅ ¡Listo para descargar!")
            st.download_button("⬇️ DESCARGAR PDF", out.getvalue(), f"VALIDADO_{id_proc}.pdf", "application/pdf")