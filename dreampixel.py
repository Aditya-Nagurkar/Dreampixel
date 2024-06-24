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
    submit_button = st.form_submit_button(label='Generate Images', use_container_width=True)

# Session state to store images and their byte data
if 'images' not in st.session_state:
    st.session_state.images = []
if 'image_bytes' not in st.session_state:
    st.session_state.image_bytes = []
if 'selected_image_index' not in st.session_state:
    st.session_state.selected_image_index = None
if 'downloaded' not in st.session_state:
    st.session_state.downloaded = False

def generate_image(prompt):
    # Send a POST request to the model endpoint
    response = requests.post(
        "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
        headers={"Authorization": "Bearer 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"},
        json={"inputs": prompt}
    )
    return response

if submit_button:
    if input_text:
        # Reset the session state
        st.session_state.downloaded = False
        st.session_state.images = []
        st.session_state.image_bytes = []
        st.session_state.selected_image_index = None

        # Display a loading message
        with st.spinner("Generating images..."):
            for i in range(4):  # Generate 4 images
                # Slightly alter the prompt for each request to ensure variety
                altered_prompt = f"{input_text} variation {i+1}"
                response = generate_image(altered_prompt)

                # Check if the request was successful
                if response.status_code == 200:
                    # Retrieve the image from the response content
                    image_bytes = response.content
                    st.session_state.image_bytes.append(image_bytes)
                    # Open the image using PIL
                    image = Image.open(BytesIO(image_bytes))
                    st.session_state.images.append(image)
                else:
                    st.error(f"Request failed with status code: {response.status_code}")
                    break

        # Display images in a 2x2 grid
        if len(st.session_state.images) == 4:
            cols = st.columns(2)
            for i, image in enumerate(st.session_state.images):
                col = cols[i % 2]
                with col:
                    if st.button(f"Select Image {i+1}", key=f"select_button_{i}"):
                        st.session_state.selected_image_index = i
                    st.image(image, caption=f"Image {i+1}", use_column_width=True)

# Display the selected image in original size
if st.session_state.selected_image_index is not None:
    st.write("### Selected Image")
    st.image(st.session_state.images[st.session_state.selected_image_index], use_column_width=True)

    # Display the download button if an image is available and it hasn't been downloaded yet
    if not st.session_state.downloaded:
        download_placeholder = st.empty()
        with download_placeholder:
            if st.download_button(
                label="Download Selected Image",
                data=st.session_state.image_bytes[st.session_state.selected_image_index],
                file_name="selected_image.png",
                mime="image/png",
                use_container_width=True
            ):
                # Set the download state to True after the image is downloaded
                st.session_state.downloaded = True
                # Clear the download button
                download_placeholder.empty()
