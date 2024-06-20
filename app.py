import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import pandas as pd
import streamlit as st

# Streamlit Cloud üzerinde Tesseract'ın kurulu olduğu yolu belirtme
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# Geçici olarak sayfa görüntülerini kaydedecek dizin oluşturma
os.makedirs('temp_images', exist_ok=True)

def process_pdf(pdf_file):
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    data = []
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        image_path = f'temp_images/page_{page_num + 1}.png'
        pix.save(image_path)

        # OCR kullanarak görüntüden metin çıkarma
        custom_oem_psm_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(image_path, lang='tur', config=custom_oem_psm_config)  # Türkçe dil desteği

        lines = text.split('\n')

        # Veriyi işleme
        for line in lines:
            if line.strip():  # Boş olmayan satırları işleme
                parts = line.split()
                if len(parts) >= 4:
                    hesap_kodu = parts[0]
                    hesap_adi = ' '.join(parts[1:-3])
                    borç = parts[-3]
                    alacak = parts[-2]
                    bakiye = parts[-1]
                    data.append([hesap_kodu, hesap_adi, borç, alacak, bakiye])

    # Geçici dizini ve içindeki dosyaları silme
    for root, dirs, files in os.walk('temp_images', topdown=False):
        for name in files:
            file_path = os.path.join(root, name)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
        for name in dirs:
            dir_path = os.path.join(root, name)
            try:
                os.rmdir(dir_path)
            except Exception as e:
                print(f'Failed to delete {dir_path}. Reason: {e}')
    try:
        os.rmdir('temp_images')
    except Exception as e:
        print(f'Failed to remove temp_images directory. Reason: {e}')

    # Veriyi pandas DataFrame'e dönüştürme
    df = pd.DataFrame(data, columns=['Hesap Kodu', 'Hesap Adı', 'Borç', 'Alacak', 'Bakiye'])
    return df

st.title('PDF to Excel Converter')
st.write('Upload a PDF file to convert it into an Excel file.')

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    with st.spinner('Processing...'):
        df = process_pdf(uploaded_file)
        st.write('Conversion completed successfully!')
        
        # Excel dosyasına kaydetme ve indirme bağlantısı oluşturma
        excel_path = 'converted_file.xlsx'
        df.to_excel(excel_path, index=False)
        with open(excel_path, 'rb') as f:
            st.download_button('Download Excel file', f, file_name='converted_file.xlsx')
