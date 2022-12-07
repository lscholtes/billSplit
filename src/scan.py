import io
from typing import Union

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


def parse_and_clean(receipt_image: io.BytesIO) -> Union[Receipt, None]:

    # Get total price to validate that scan is correct
    total_price_container = st.container()
    with total_price_container:
        total_bill_cost = st.text_input("Please enter bill total below:")

    if total_bill_cost:

        total_bill_cost = float(total_bill_cost)

        # This should be False by default, usually OCR works better
        # for receipts with psm=4
        alternate_psm = st.checkbox(
            "Alternate OCR PSM",
            help="Toggle this setting if the extracted text is poor quality.",
        )
        psm = 6 if alternate_psm else 4

        parsed_text = parse_cropped_image(receipt_image, psm=psm)

        cleaned_text = st.text_area(
            "Parsed Text, please fix - line entry names should be unique.",
            parsed_text,
            height=500,
        )

        receipt = Receipt.parse_receipt_text(cleaned_text)

        if receipt.total_cost != total_bill_cost:
            with total_price_container:
                st.markdown(
                    f"""
                    ## Wait! ⚠️
                    **The bill total provided, £{total_bill_cost:.2f}, does not \
                    match the total bill amount below, £{receipt.total_cost:.2f}.**  
                    *Please fix the scanned text manually to ensure they match.*"""
                )
            return

        return receipt
