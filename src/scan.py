import io

from PIL import Image
import pytesseract
import streamlit as st
from streamlit_cropper import st_cropper

from src.models import Receipt


def preprocess_parsed_text(parsed_text: str):
    return parsed_text.strip()


def crop_image(receipt_image: io.BytesIO) -> Image:
        return st_cropper(
            Image.open(receipt_image), 
        )


@st.cache
def parse_cropped_image(cropped_image: Image, psm: int) -> str:
    parsed_text = pytesseract.image_to_string(cropped_image, config=fr'-l eng --psm {psm}')
    parsed_text = preprocess_parsed_text(parsed_text)
    return parsed_text


def crop_parse_clean(receipt_image: io.BytesIO) -> Receipt:
    left, first_right, second_right = st.columns([2, 1, 1])

    with left:
        st.markdown("Original image")
        cropped_image = crop_image(receipt_image)

    with first_right:
        st.markdown("Line entries only")
        st.image(cropped_image)

    with second_right:
        # This should be False by default, usually OCR works better for receipts with psm=4
        alternate_psm = st.checkbox("Alternate OCR PSM") 
        psm = 6 if alternate_psm else 4

        parsed_text = parse_cropped_image(cropped_image, psm=psm)
        cleaned_text = st.text_area("Parsed Text, please clean", parsed_text, height=500)

    receipt = Receipt.parse_receipt_text(cleaned_text)

    return receipt
