import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# Streamlit UI setup
st.title("Dreampixel: Your Gateway To Limitless Visual Creativity!")

# Form for input and button
with st.form(key='image_generation_form'):
    # Prompt input from user
    input_text = st.text_input("Enter your prompt to generate an image:")
    # Submit button
    submit_button = st.form_submit_button(label='Generate Image')

# Session state to store the image and its byte data
if 'image' not in st.session_state:
    st.session_state.image = None
if 'image_bytes' not in st.session_state:
    st.session_state.image_bytes = None
if 'downloaded' not in st.session_state:
    st.session_state.downloaded = False

if submit_button:
    if input_text:
        # Reset the download state
        st.session_state.downloaded = False

        # Display a loading message
        with st.spinner("Generating image..."):
            # Send a POST request to the model endpoint
            response = requests.post(
                "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1",
                headers={"Authorization": "Bearer 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"},
                json={"inputs": input_text}
            )

            # Check if the request was successful
            if response.status_code == 200:
                # Retrieve the image from the response content
                st.session_state.image_bytes = response.content
                # Open the image using PIL
                st.session_state.image = Image.open(BytesIO(st.session_state.image_bytes))

                # Display the image in the Streamlit app
                st.image(st.session_state.image, caption="Generated Image", use_column_width=True)
            else:
                st.error(f"Request failed with status code: {response.status_code}")
    else:
        st.warning("Please enter a prompt to generate an image.")

# Display the download button if an image is available and it hasn't been downloaded yet
if st.session_state.image and not st.session_state.downloaded:
    download_placeholder = st.empty()
    with download_placeholder:
        if st.download_button(
            label="Download Image",
            data=st.session_state.image_bytes,
            file_name="generated_image.png",
            mime="image/png",
            use_container_width=True
        ):
            # Set the download state to True after the image is downloaded
            st.session_state.downloaded = True
            # Clear the download button
            download_placeholder.empty()
