import streamlit as st
import requests
from PIL import Image
from io import BytesIO
from datetime import datetime
import os

# Streamlit UI setup
st.title("Dreampixel: Your Gateway To Limitless Visual Creativity!")

# Prompt input from user
input_text = st.text_input("Enter your prompt to generate an image:")

if st.button("Generate Image",use_container_width=True):
    if input_text:
        # Display a loading message
        with st.spinner("Generating image..."):
            # Send a POST request to the model endpoint 
            response = requests.post(
                "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1",
                headers={
                    "Authorization": "Bearer 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"
                },
                json={"inputs": input_text}
            )

            # Check if the request was successful
            if response.status_code == 200:
                # Retrieve the image from the response content
                image_bytes = response.content
                # Open the image using PIL
                image = Image.open(BytesIO(image_bytes))

                # Display the image in the Streamlit app
                st.image(image, caption="Generated Image", use_column_width=True)

                # Generate a timestamp for the filename (e.g., YYYYMMDD_HHMMSS)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                # Specify the path where you want to save the image with a unique filename
                output_path = f"output_{timestamp}.png"

                # Centering the buttons using columns with empty spaces
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col2:
                    if st.button("Save Image"):
                        # Save the image to the specified path
                        image.save(output_path)
                        st.success(f"Sweet! Your image has officially joined the perfectly saved masterpieces. Saved as {output_path}.")
                
                with col4:
                    if st.button("Delete Image"):
                        if os.path.exists(output_path):
                            os.remove(output_path)
                            st.success("Image deleted successfully.")
                        else:
                            st.warning("No image to delete.")
            else:
                st.error(f"Request failed with status code: {response.status_code}")
    else:
        st.warning("Please enter a prompt to generate an image.")
