from typing import Union

import streamlit as st
from PIL import Image


def rotate_image(image: Image) -> Image:
    rotate_image = st.selectbox("Rotate image?", ["0°", "90°", "180°", "270°"])
    if rotate_image == "90°":
        image = image.transpose(Image.ROTATE_90)
    elif rotate_image == "180°":
        image = image.transpose(Image.ROTATE_180)
    elif rotate_image == "270°":
        image = image.transpose(Image.ROTATE_270)
    return image


def upload_and_crop() -> Union[Image.Image, None]:

    welcome_banner_container = st.container()

    with st.expander("File Upload"):
        st.markdown(
            "Please upload a top-down image of the receipt with good \
            lighting. If possible, ensure that image has been cropped to \
            show only line items."
        )
        receipt_image = st.file_uploader("Upload image")
        if receipt_image is None:
            with welcome_banner_container:
                st.markdown(
                    """
                    # Welcome to BillSplit! 👋
                    To begin splitting, upload a picture of your bill:
                    """
                )
            return

    receipt_image = Image.open(receipt_image)

    if receipt_image:

        receipt_image = rotate_image(receipt_image)
        st.markdown("Uploaded image")
        st.image(receipt_image)

    return receipt_image
