from typing import Union

from PIL import Image
import streamlit as st
from streamlit_cropper import st_cropper


def upload_and_crop() -> Union[Image.Image, None]:

    with st.expander("File Upload"):
        receipt_image = st.file_uploader("Upload image")
        crop_image = st.checkbox(
            "Crop image?",
            help="Picture should contain receipt line entries only. MOBILE USERS, please pre-crop any uploaded pictures, do not use this option.",
        )
        if receipt_image is None:
            return

    receipt_image = Image.open(receipt_image)

    if crop_image:
        left, right = st.columns([2, 1])
        with left:
            st.markdown("Original image")
            cropped_image = st_cropper(receipt_image)
        with right:
            st.markdown("Line entries only")
            st.image(cropped_image)
        return cropped_image
    else:
        st.markdown("Uploaded image")
        st.image(receipt_image)
    return receipt_image
