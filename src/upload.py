from typing import Union

import streamlit as st
from PIL import Image


def upload_and_crop() -> Union[Image.Image, None]:

    with st.expander("File Upload"):
        st.markdown(
            "Please upload a top-down image of the receipt with good \
            lighting. If possible, ensure that image has been cropped to \
            show only line items."
        )
        receipt_image = st.file_uploader("Upload image")
        if receipt_image is None:
            return

    receipt_image = Image.open(receipt_image)

    st.markdown("Uploaded image")
    st.image(receipt_image)

    return receipt_image
