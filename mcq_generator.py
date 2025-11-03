import streamlit as st
import PyPDF2
import anthropic
import os
import json
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="PDF MCQ Generator",
    page_icon="📝",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        height: 3em;
        border-radius: 5px;
    }
    .mcq-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #4CAF50;
    }
    </style>
""", unsafe_allow_html=True)

def extract_text_from_pdf(pdf_file):
    """Extract text content from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

def generate_mcqs(text, num_questions, difficulty, api_key):
    """Generate MCQs using Claude API"""
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        prompt = f"""Based on the following text, generate {num_questions} multiple-choice questions at {difficulty} difficulty level.

Text:
{text[:4000]}  # Limiting text size for API

Please format your response as a JSON array with this structure:
[
    {{
        "question": "Question text here?",
        "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
        "correct_answer": "A",
        "explanation": "Brief explanation of why this is correct"
    }}
]

Make sure the questions are:
- Clear and unambiguous
- Relevant to the content
- At {difficulty} difficulty level
- Have exactly 4 options (A, B, C, D)
"""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text
        
        # Extract JSON from response
        start_idx = response_text.find('[')
        end_idx = response_text.rfind(']') + 1
        json_str = response_text[start_idx:end_idx]
        
        mcqs = json.loads(json_str)
        return mcqs
        
    except Exception as e:
        st.error(f"Error generating MCQs: {str(e)}")
        return None

def display_mcqs(mcqs):
    """Display generated MCQs in a nice format"""
    for idx, mcq in enumerate(mcqs, 1):
        st.markdown(f"### Question {idx}")
        st.markdown(f"**{mcq['question']}**")
        
        for option in mcq['options']:
            st.write(option)
        
        with st.expander("Show Answer & Explanation"):
            st.success(f"✅ Correct Answer: {mcq['correct_answer']}")
            st.info(f"📖 {mcq['explanation']}")
        
        st.markdown("---")

def export_to_json(mcqs):
    """Export MCQs to JSON format"""
    return json.dumps(mcqs, indent=2)

def export_to_text(mcqs):
    """Export MCQs to text format"""
    text = ""
    for idx, mcq in enumerate(mcqs, 1):
        text += f"Question {idx}: {mcq['question']}\n"
        for option in mcq['options']:
            text += f"  {option}\n"
        text += f"\nCorrect Answer: {mcq['correct_answer']}\n"
        text += f"Explanation: {mcq['explanation']}\n"
        text += "\n" + "="*50 + "\n\n"
    return text

# Main App
def main():
    st.title("📝 PDF MCQ Generator")
    st.markdown("Upload a PDF and generate multiple-choice questions automatically using AI")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        api_key = st.text_input(
            "Anthropic API Key",
            type="password",
            help="Get your API key from https://console.anthropic.com/"
        )
        
        num_questions = st.slider(
            "Number of Questions",
            min_value=1,
            max_value=20,
            value=5
        )
        
        difficulty = st.selectbox(
            "Difficulty Level",
            ["Easy", "Medium", "Hard"]
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.info("This tool uses Claude AI to generate high-quality MCQs from your PDF documents.")
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload PDF File",
            type=['pdf'],
            help="Upload a PDF document to generate questions from"
        )
    
    with col2:
        st.markdown("### Quick Stats")
        if uploaded_file:
            st.metric("File Size", f"{uploaded_file.size / 1024:.2f} KB")
    
    if uploaded_file and api_key:
        if st.button("🚀 Generate MCQs"):
            with st.spinner("Extracting text from PDF..."):
                text = extract_text_from_pdf(uploaded_file)
            
            if text:
                word_count = len(text.split())
                st.success(f"✅ Extracted {word_count} words from PDF")
                
                with st.spinner("Generating MCQs with AI... This may take a moment."):
                    mcqs = generate_mcqs(text, num_questions, difficulty, api_key)
                
                if mcqs:
                    st.success(f"✅ Generated {len(mcqs)} questions!")
                    
                    # Store in session state
                    st.session_state['mcqs'] = mcqs
                    
                    # Display MCQs
                    st.markdown("## 📋 Generated Questions")
                    display_mcqs(mcqs)
                    
                    # Export options
                    st.markdown("## 💾 Export Options")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        json_data = export_to_json(mcqs)
                        st.download_button(
                            label="Download as JSON",
                            data=json_data,
                            file_name="mcqs.json",
                            mime="application/json"
                        )
                    
                    with col2:
                        text_data = export_to_text(mcqs)
                        st.download_button(
                            label="Download as Text",
                            data=text_data,
                            file_name="mcqs.txt",
                            mime="text/plain"
                        )
    
    elif not api_key:
        st.warning("⚠️ Please enter your Anthropic API key in the sidebar to continue.")
    elif not uploaded_file:
        st.info("👆 Upload a PDF file to get started!")
    
    # Display existing MCQs if available
    if 'mcqs' in st.session_state and st.session_state['mcqs']:
        if not (uploaded_file and api_key):
            st.markdown("## 📋 Previously Generated Questions")
            display_mcqs(st.session_state['mcqs'])

if __name__ == "__main__":
    main()
