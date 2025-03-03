import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import time
import json

st.set_page_config(
    page_title="Dreampixel: AI Image Generator",
    layout="wide"
)

API_KEY = "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"
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

st.markdown("""
    <style>
        .stButton > button {
            background-color: #FF4B4B;
            color: white;
            border-radius: 5px;
            padding: 0.5rem 1rem;
        }
        .stButton > button:hover {
            background-color: #FF6B6B;
        }
        .aspect-ratio-box {
            padding: 10px;
            border-radius: 5px;
            background-color: #f0f2f6;
            margin: 10px 0;
        }
    </style>
""", unsafe_allow_html=True)

ASPECT_RATIOS = {
    "Square (1:1)": (1024, 1024),
    "Landscape (16:9)": (1024, 576),
    "Portrait (9:16)": (576, 1024),
    "Widescreen (21:9)": (1024, 440),
    "Classic (4:3)": (1024, 768),
    "Tall (9:21)": (436, 1024)
}

def query_api_with_retry(payload, max_retries=5, initial_wait=5):
    headers = {"Authorization": f"Bearer {API_KEY}"}

    for attempt in range(max_retries):
        try:
            response = requests.post(
                API_URL,
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                return response.content

            elif response.status_code == 429:
                wait_time = initial_wait * (2 ** attempt)
                st.warning(f"Rate limit reached. Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue

            elif response.status_code == 503:
                response_json = response.json()
                if "estimated_time" in response_json:
                    wait_time = response_json["estimated_time"]
                    st.warning(f"Model is loading. Waiting {wait_time:.1f} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    time.sleep(5)
                    continue

            else:
                response.raise_for_status()

        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise Exception(f"Failed after {max_retries} attempts. Error: {str(e)}")
            time.sleep(initial_wait)
            continue

    raise Exception(f"Failed after {max_retries} attempts due to rate limiting")

@st.cache_data(ttl=3600, show_spinner=False)
def generate_single_image(prompt, variation_number, width, height):
    try:
        payload = {
            "inputs": f"{prompt} Variation {variation_number}",
            "parameters": {
                "width": width,
                "height": height,
                "num_inference_steps": 50,
                "guidance_scale": 7.5,
                "negative_prompt": "blurry, low quality, distorted, deformed",
            }
        }
        image_bytes = query_api_with_retry(payload)
        return Image.open(BytesIO(image_bytes))
    except Exception as e:
        st.error(f"Error generating image {variation_number}: {str(e)}")
        return None

def main():
    st.title("Dreampixel: Your Gateway To Limitless Visual Creativity!")
    st.markdown("""
        Transform your ideas into stunning images using state-of-the-art AI technology.
        Simply enter your prompt below and watch the magic happen!
    """)

    # Initialize session state variables
    if 'generated_images' not in st.session_state:
        st.session_state.generated_images = []
    if 'current_image_index' not in st.session_state:
        st.session_state.current_image_index = 0
    if 'generation_complete' not in st.session_state:
        st.session_state.generation_complete = False
    if 'generating' not in st.session_state:
        st.session_state.generating = False

    with st.form(key='image_generation_form'):
        input_text = st.text_input(
            "What would you like to create?",
            placeholder="E.g., A serene landscape with mountains and a lake at sunset",
            help="Be specific and descriptive for better results"
        )

        aspect_ratio = st.selectbox(
            "Choose aspect ratio",
            options=list(ASPECT_RATIOS.keys()),
            help="Select the desired dimensions for your generated images"
        )

        num_images = st.slider("Number of variations", min_value=1, max_value=4, value=2)

        submit_button = st.form_submit_button(
            label='Generate Images',
            use_container_width=True
        )

    if submit_button:
        if not input_text:
            st.warning("Please enter a prompt to generate images.")
        else:
            # Reset state for new generation
            st.session_state.generated_images = []
            st.session_state.current_image_index = 0
            st.session_state.generation_complete = False
            st.session_state.generating = True
            st.session_state.num_images_to_generate = num_images
            st.session_state.prompt = input_text
            st.session_state.selected_aspect_ratio = aspect_ratio

    # Create placeholders for progress and images
    progress_container = st.empty()
    status_text = st.empty()
    image_container = st.container()
    
    # Generate images sequentially
    if st.session_state.generating and len(st.session_state.generated_images) < st.session_state.num_images_to_generate:
        with progress_container:
            progress = st.progress((len(st.session_state.generated_images)) / st.session_state.num_images_to_generate)
        
        current_index = len(st.session_state.generated_images) + 1
        status_text.text(f"Generating image {current_index}/{st.session_state.num_images_to_generate}...")
        
        width, height = ASPECT_RATIOS[st.session_state.selected_aspect_ratio]
        
        try:
            new_image = generate_single_image(
                st.session_state.prompt, 
                current_index, 
                width, 
                height
            )
            
            if new_image:
                st.session_state.generated_images.append(new_image)
                st.session_state.current_image_index = len(st.session_state.generated_images) - 1
                
                # Check if generation is complete
                if len(st.session_state.generated_images) == st.session_state.num_images_to_generate:
                    st.session_state.generation_complete = True
                    st.session_state.generating = False
                    progress_container.empty()
                    status_text.empty()
                
                # Force rerun to continue generation
                if not st.session_state.generation_complete:
                    time.sleep(2)  # Brief pause between generations
                    st.experimental_rerun()
                    
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
            st.session_state.generating = False
            progress_container.empty()
            status_text.empty()
    
    # Display generated images
    if st.session_state.generated_images:
        with image_container:
            st.subheader("Generated Images")
            
            # Display images sequentially
            for idx, image in enumerate(st.session_state.generated_images):
                st.image(
                    image,
                    caption=f"Variation {idx+1}",
                    use_container_width=True
                )
                
                img_bytes = BytesIO()
                image.save(img_bytes, format='PNG')
                st.download_button(
                    label=f"Download Variation {idx+1}",
                    data=img_bytes.getvalue(),
                    file_name=f"dreampixel_generation_{idx+1}.png",
                    mime="image/png",
                    key=f"download_{idx}"
                )
                
                # Add some spacing between images
                st.markdown("<hr>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()