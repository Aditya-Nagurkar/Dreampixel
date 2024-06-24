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

# Function to generate multiple images
def generate_images(prompt, num_images=4):
    images = []
    for i in range(num_images):
        response = requests.post(
            "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
            headers={"Authorization": "Bearer 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"},
            json={"inputs": f"{prompt} Variation {i+1}"}
        )
        if response.status_code == 200:
            image_bytes = response.content
            image = Image.open(BytesIO(image_bytes))
            images.append(image)
        else:
            st.error(f"Request for image {i+1} failed with status code: {response.status_code}")
    return images

# Display images in a grid and enable download
if submit_button:
    if input_text:
        # Generate 4 variations of the image
        images = generate_images(input_text, num_images=4)
        
        # Display images in a 2x2 grid
        col1, col2 = st.columns(2)
        for i in range(4):
            with col1 if i < 2 else col2:
                st.image(images[i], caption=f"Generated Image {i+1}", use_column_width=True)
                # Convert image to bytes
                img_bytes = BytesIO()
                images[i].save(img_bytes, format='PNG')
                # Download button for each image
                if st.download_button(
                    label=f"Download Image {i+1}",
                    data=img_bytes.getvalue(),
                    file_name=f"generated_image_{i+1}.png",
                    mime="image/png",
                    key=f"download_button_{i+1}"
                ):
                    st.info(f"Image {i+1} downloaded successfully!")
    else:
        st.warning("Please enter a prompt to generate images.")
