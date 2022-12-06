import io

import pytesseract
import streamlit as st
from PIL import Image

from src.models import Receipt


def preprocess_parsed_text(parsed_text: str):
    return parsed_text.strip()


@st.cache
def parse_cropped_image(cropped_image: Image, psm: int) -> str:
    if cropped_image.format != "JPEG":
        # Make sure the image type is something Tesseract can handle
        cropped_image = cropped_image.convert("RGB")
    parsed_text = pytesseract.image_to_string(
        cropped_image, config=rf"-l eng --psm {psm}"
    )
    parsed_text = preprocess_parsed_text(parsed_text)
    return parsed_text


def parse_and_clean(receipt_image: io.BytesIO) -> Receipt:

    # This should be False by default, usually OCR works better
    # for receipts with psm=4
    alternate_psm = st.checkbox("Alternate OCR PSM")
    psm = 6 if alternate_psm else 4

    parsed_text = parse_cropped_image(receipt_image, psm=psm)
    cleaned_text = st.text_area("Parsed Text, please clean", parsed_text, height=50)

    receipt = Receipt.parse_receipt_text(cleaned_text)

    return receipt
