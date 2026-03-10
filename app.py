import streamlit as st
import qrcode
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
import io
import os

# 1. Configuración de página
st.set_page_config(page_title="Validador Ayapel", page_icon="🛡️", layout="centered")

# 2. Estética de Caja Flotante y Colores Institucionales
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    .block-container {
        background-color: white !important;
        padding: 40px !important;
        border-radius: 25px !important;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.1) !important;
        margin-top: 30px !important;
        max-width: 650px !important;
    }
    .verde-ayapel {
        color: #04D918 !important;
        font-family: 'Arial', sans-serif !important;
        font-weight: bold !important;
        text-align: center !important;
        margin-bottom: 0px !important;
    }
    .caja-verificacion {
        background-color: #f9fff9;
        border: 2px solid #04D918;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        margin-top: 20px;
    }
    /* Centrado forzado para imágenes */
    [data-testid="stHorizontalBlock"] {
        align-items: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Función mejorada para CENTRADO ABSOLUTO
def mostrar_escudo(tamano=250):
    # Usamos HTML para forzar el centrado total
    nombre_archivo = "escudo.png" if os.path.exists("escudo.png") else "escudo.PNG"
    
    if os.path.exists(nombre_archivo):
        st.markdown(
            f"""
            <div style="display: flex; justify-content: center; margin-bottom: 10px;">
                <img src="data:image/png;base64,{get_image_base64(nombre_archivo)}" width="{tamano}">
            </div>
            """,
            unsafe_allow_html=True
        )
# Necesitamos esta pequeña función extra para que el HTML lea la imagen de GitHub
import base64
def get_image_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()
# --- LÓGICA DE NAVEGACIÓN ---
query_params = st.query_params

if "validar" in query_params:
    # --- VISTA CIUDADANO (PANTALLA VERDE DEL QR) ---
    id_doc = query_params.get("validar")
    url_doc = query_params.get("url")
    
    mostrar_escudo(tamano=250) # Escudo grande para el ciudadano
    
    st.markdown('<p class="verde-ayapel" style="font-size: 28px;">ALCALDÍA DE AYAPEL</p>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="caja-verificacion">
        <h3 style="color: #1b5e20; margin-top:0;">✅ DOCUMENTO ORIGINAL VERIFICADO</h3>
        <p style="font-size: 18px; margin-bottom:10px;"><b>ID del Proceso:</b> {id_doc}</p>
        <hr style="border: 0.5px solid #04D918; opacity: 0.3;">
        <p style="font-size: 16px; color: #333; line-height: 1.6; text-align: justify;">
            Se certifica que este documento es <b>original</b>. En el expediente físico institucional, 
            este documento cuenta con la firma autógrafa (a <b>puño y letra</b>) del funcionario responsable. 
            La versión digital cargada en la plataforma SECOP I es fiel copia del original que 
            reposa en los archivos de la Alcaldía de Ayapel, Córdoba.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.link_button("📂 VER DOCUMENTO ORIGINAL EN DRIVE", url_doc, use_container_width=True)

else:
    # --- VISTA ADMINISTRADOR (GENERADOR) ---
    mostrar_escudo(tamano=180)
    
    st.markdown('<p class="verde-ayapel" style="font-size: 24px;">ALCALDÍA DE AYAPEL CÓRDOBA</p>', unsafe_allow_html=True)
    st.markdown('<p class="verde-ayapel" style="font-size: 18px; color: #666 !important;">VALIDADOR DE DOCUMENTOS SECOP 1</p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    archivo = st.file_uploader("📂 1. Suba el documento PDF", type="pdf")
    id_proc = st.text_input("📝 2. Ingrese el ID del Proceso (Evite espacios)")
    link_drive = st.text_input("🔗 3. Pegue el Link de Drive")

    if st.button("🚀 GENERAR DOCUMENTO VALIDADO", use_container_width=True):
        if archivo and id_proc and link_drive:
            with st.spinner('Procesando...'):
                # CONFIGURA TU URL AQUÍ ABAJO:
                base_url = "https://validador-ayapel-bkmse63yk9sif272ml6fcr.streamlit.app"
                # Creamos el link para el QR (usamos replace para evitar errores de espacios en la URL)
                url_portal = f"{base_url}/?validar={id_proc.replace(' ', '%20')}&url={link_drive}"
                
                # Generar QR
                qr = qrcode.make(url_portal)
                img_buffer = io.BytesIO()
                qr.save(img_buffer, format="PNG")
                
                # Crear estampa legal en el PDF
                packet = io.BytesIO()
                can = canvas.Canvas(packet)
                can.drawInlineImage(qr, 480, 40, width=75, height=75)
                can.setFont("Helvetica-Bold", 8)
                can.drawString(50, 65, "CERTIFICACIÓN DE ORIGINALIDAD")
                can.setFont("Helvetica", 7)
                can.drawString(50, 55, f"ID: {id_proc}. Documento original firmado a puño y letra.")
                can.drawString(50, 47, "Verifique la autenticidad escaneando el código QR.")
                can.save()
                
                # Unir con el PDF original
                reader = PdfReader(archivo)
                writer = PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)
                writer.pages[-1].merge_page(PdfReader(io.BytesIO(packet.getvalue())).pages[0])
                
                out = io.BytesIO()
                writer.write(out)
                
                st.success("✅ ¡Documento Validado Exitosamente!")
                st.download_button(
                    label="⬇️ DESCARGAR PDF CON QR",
                    data=out.getvalue(),
                    file_name=f"VALIDADO_{id_proc}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        else:
            st.error("⚠️ Por favor complete todos los campos (Archivo, ID y Link).")

