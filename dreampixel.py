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
    submit_button = st.form_submit_button(label='Generate Image', use_container_width=True)

# Session state to store the image and its byte data
if 'image' not in st.session_state:
    st.session_state.image = None
if 'image_bytes' not in st.session_state:
    st.session_state.image_bytes = None
if 'downloaded' not in st.session_state:
    st.session_state.downloaded = False
if 'aspect_ratio' not in st.session_state:
    st.session_state.aspect_ratio = 'Original'

def generate_image(prompt, aspect_ratio):
    # Define aspect ratio modifications
    aspect_ratio_mods = {
        'Landscape': "in landscape mode",
        'Portrait': "in portrait mode",
        'Wide Angle': "in wide angle view",
        'Original': ""  # No modification for original
    }
    
    # Modify the prompt based on the selected aspect ratio
    modified_prompt = f"{prompt} {aspect_ratio_mods[aspect_ratio]}"
    
    # Send a POST request to the model endpoint
    response = requests.post(
        "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
        headers={"Authorization": "Bearer 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"},
        json={"inputs": modified_prompt}
    )

    # Check if the request was successful
    if response.status_code == 200:
        # Retrieve the image from the response content
        st.session_state.image_bytes = response.content
        # Open the image using PIL
        st.session_state.image = Image.open(BytesIO(st.session_state.image_bytes))

        # Display the image in the Streamlit app with default size
        st.image(st.session_state.image, caption=f"Generated Image - {aspect_ratio}", use_column_width=True)
    else:
        st.error(f"Request failed with status code: {response.status_code}")

if submit_button:
    if input_text:
        # Reset the download state
        st.session_state.downloaded = False
        st.session_state.aspect_ratio = 'Original'

        # Display a loading message
        with st.spinner("Generating image..."):
            generate_image(input_text, 'Original')
    else:
        st.warning("Please enter a prompt to generate an image.")

# Display aspect ratio options if an image is available
if st.session_state.image:
    st.write("Choose image size:")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Landscape"):
            st.session_state.aspect_ratio = 'Landscape'
            with st.spinner("Generating image..."):
                generate_image(input_text, 'Landscape')
    with col2:
        if st.button("Portrait"):
            st.session_state.aspect_ratio = 'Portrait'
            with st.spinner("Generating image..."):
                generate_image(input_text, 'Portrait')
    with col3:
        if st.button("Wide Angle"):
            st.session_state.aspect_ratio = 'Wide Angle'
            with st.spinner("Generating image..."):
                generate_image(input_text, 'Wide Angle')
    with col4:
        if st.button("Original"):
            st.session_state.aspect_ratio = 'Original'
            with st.spinner("Generating image..."):
                generate_image(input_text, 'Original')

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
