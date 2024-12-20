import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import time

# Configure page settings
st.set_page_config(
    page_title="Dreampixel: AI Image Generator",
    page_icon="🎨",
    layout="wide"
)

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

# Cache the API call to prevent repeated calls
@st.cache_data(ttl=3600, show_spinner=False)
def generate_single_image(prompt, api_key, variation_number):
    """Generate a single image with error handling"""
    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"inputs": f"{prompt} Variation {variation_number}"},
            timeout=30  # Add timeout
        )
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except requests.exceptions.RequestException as e:
        st.error(f"Error generating image {variation_number}: {str(e)}")
        return None

def generate_images(prompt, api_key, num_images=4):
    """Generate multiple images with progress tracking"""
    images = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(num_images):
        status_text.text(f"Generating image {i+1}/{num_images}...")
        image = generate_single_image(prompt, api_key, i+1)
        if image:
            images.append(image)
        progress_bar.progress((i + 1) / num_images)
        time.sleep(0.1)  # Prevent rate limiting
    
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

    # API key input (you might want to move this to secrets management)
    api_key = st.sidebar.text_input(
        "Enter Hugging Face API Key",
        type="password",
        help="Enter your Hugging Face API key. Get one at huggingface.co"
    )

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
        num_images = st.slider("Number of variations", min_value=1, max_value=4, value=4)
        
        # Submit button
        submit_button = st.form_submit_button(
            label='🎨 Generate Images',
            use_container_width=True
        )

    # Handle form submission
    if submit_button:
        if not api_key:
            st.error("Please enter your Hugging Face API key in the sidebar.")
        elif not input_text:
            st.warning("Please enter a prompt to generate images.")
        else:
            try:
                with st.spinner("🎨 Creating your masterpiece..."):
                    st.session_state.generated_images = generate_images(
                        input_text,
                        api_key,
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
                st.image(image, caption=f"Variation {idx+1}", use_column_width=True)
                
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