import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import time
import json

# Configure page settings
st.set_page_config(
    page_title="Dreampixel: AI Image Generator",
    page_icon="🎨",
    layout="wide"
)

# API Configuration
API_KEY = "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"
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

# Custom CSS to improve the UI
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
    </style>
""", unsafe_allow_html=True)

def query_api_with_retry(payload, max_retries=5, initial_wait=5):
    """Query the API with retry logic for rate limits"""
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
            
            # Handle rate limiting
            elif response.status_code == 429:
                wait_time = initial_wait * (2 ** attempt)  # Exponential backoff
                st.warning(f"Rate limit reached. Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                continue
            
            # Model still loading
            elif response.status_code == 503:
                response_json = response.json()
                if "estimated_time" in response_json:
                    wait_time = response_json["estimated_time"]
                    st.warning(f"Model is loading. Waiting {wait_time:.1f} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    time.sleep(5)  # Default wait if no estimate provided
                    continue
                    
            else:
                response.raise_for_status()
                
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:  # Last attempt
                raise Exception(f"Failed after {max_retries} attempts. Error: {str(e)}")
            time.sleep(initial_wait)
            continue
            
    raise Exception(f"Failed after {max_retries} attempts due to rate limiting")

@st.cache_data(ttl=3600, show_spinner=False)
def generate_single_image(prompt, variation_number):
    """Generate a single image with error handling and retries"""
    try:
        payload = {"inputs": f"{prompt} Variation {variation_number}"}
        image_bytes = query_api_with_retry(payload)
        return Image.open(BytesIO(image_bytes))
    except Exception as e:
        st.error(f"Error generating image {variation_number}: {str(e)}")
        return None

def generate_images(prompt, num_images=4):
    """Generate multiple images with progress tracking"""
    images = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(num_images):
        status_text.text(f"Generating image {i+1}/{num_images}...")
        image = generate_single_image(prompt, i+1)
        if image:
            images.append(image)
        progress_bar.progress((i + 1) / num_images)
        time.sleep(2)  # Increased delay between requests to prevent rate limiting
    
    status_text.empty()
    progress_bar.empty()
    return images

def main():
    # Title and description
    st.title("🎨 Dreampixel: Your Gateway To Limitless Visual Creativity!")
    st.markdown("""
        Transform your ideas into stunning images using state-of-the-art AI technology.
        Simply enter your prompt below and watch the magic happen!
    """)

    # Initialize session state for storing generated images
    if 'generated_images' not in st.session_state:
        st.session_state.generated_images = None

    # Form for input
    with st.form(key='image_generation_form'):
        # Text input with placeholder and help text
        input_text = st.text_input(
            "What would you like to create?",
            placeholder="E.g., A serene landscape with mountains and a lake at sunset",
            help="Be specific and descriptive for better results"
        )
        
        # Number of images selector
        num_images = st.slider("Number of variations", min_value=1, max_value=4, value=2)  # Default reduced to 2
        
        # Submit button
        submit_button = st.form_submit_button(
            label='🎨 Generate Images',
            use_container_width=True
        )

    # Handle form submission
    if submit_button:
        if not input_text:
            st.warning("Please enter a prompt to generate images.")
        else:
            try:
                with st.spinner("🎨 Creating your masterpiece... This might take a minute."):
                    st.session_state.generated_images = generate_images(
                        input_text,
                        num_images
                    )
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")

    # Display generated images
    if st.session_state.generated_images:
        st.subheader("Generated Images")
        
        # Create columns for the grid layout
        cols = st.columns(2)
        for idx, image in enumerate(st.session_state.generated_images):
            with cols[idx % 2]:
                st.image(
                    image,
                    caption=f"Variation {idx+1}",
                    use_container_width=True
                )
                
                # Create download button for each image
                img_bytes = BytesIO()
                image.save(img_bytes, format='PNG')
                st.download_button(
                    label=f"📥 Download Variation {idx+1}",
                    data=img_bytes.getvalue(),
                    file_name=f"dreampixel_generation_{idx+1}.png",
                    mime="image/png",
                    key=f"download_{idx}"
                )

if __name__ == "__main__":
    main()