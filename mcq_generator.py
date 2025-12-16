"""
AI Quiz Generator - Complete Streamlit Application
Author: AI Assistant
Description: Generate interactive quizzes from PDF documents
Version: 1.0
"""

import streamlit as st
import PyPDF2
import io
import json
import random
import re
from datetime import datetime
import pandas as pd
from typing import List, Dict
import os

# Configure Streamlit page
st.set_page_config(
    page_title="📚 AI Quiz Generator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .quiz-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .question-box {
        background-color: white;
        padding: 20px;
        border-left: 4px solid #1f77b4;
        margin: 15px 0;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    .correct-answer {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
        margin: 5px 0;
    }
    .incorrect-answer {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
        margin: 5px 0;
    }
    .score-display {
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
    .excellent-score {
        background-color: #d4edda;
        color: #155724;
    }
    .good-score {
        background-color: #fff3cd;
        color: #856404;
    }
    .poor-score {
        background-color: #f8d7da;
        color: #721c24;
    }
    .feature-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border: 1px solid #dee2e6;
    }
    .sidebar-section {
        background-color: #f1f3f4;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

class QuizGenerator:
    """Main class for generating quizzes from PDF content"""
    
    def __init__(self):
        self.questions = []
        self.extracted_text = ""
        
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text content from uploaded PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            total_pages = len(pdf_reader.pages)
            
            # Show progress for large PDFs
            if total_pages > 10:
                progress_bar = st.progress(0)
                status_text = st.empty()
            
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                text += page_text + "\n"
                
                # Update progress for large PDFs
                if total_pages > 10:
                    progress = (i + 1) / total_pages
                    progress_bar.progress(progress)
                    status_text.text(f'Processing page {i+1} of {total_pages}...')
            
            # Clear progress indicators
            if total_pages > 10:
                progress_bar.empty()
                status_text.empty()
            
            self.extracted_text = text.strip()
            return self.extracted_text
            
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
            return ""
    
    def clean_text(self, text: str) -> str:
        """Clean and preprocess extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might interfere
        text = re.sub(r'[^\w\s.,;:!?()-]', '', text)
        # Remove very short lines
        lines = text.split('\n')
        cleaned_lines = [line.strip() for line in lines if len(line.strip()) > 10]
        return ' '.join(cleaned_lines)
    
    def extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts and terms from text"""
        # Split into sentences
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        
        # Extract potential key terms (capitalized words, longer words)
        words = text.split()
        key_terms = []
        
        for word in words:
            word = word.strip('.,;:!?()[]{}"\'-')
            # Look for capitalized words (proper nouns) or longer significant words
            if (word.istitle() and len(word) > 3) or (len(word) > 7 and word.isalpha()):
                key_terms.append(word)
        
        # Remove duplicates and limit
        key_terms = list(set(key_terms))[:30]
        return key_terms
    
    def generate_multiple_choice_questions(self, text: str, num_questions: int = 5) -> List[Dict]:
        """Generate multiple choice questions using rule-based approach"""
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 30]
        questions = []
        
        if len(sentences) < 3:
            st.warning("The PDF content seems too short to generate meaningful questions.")
            return []
        
        # Question patterns with variety
        question_patterns = [
            "What is the main concept of {}?",
            "According to the document, what is {}?",
            "How is {} defined in the text?",
            "What are the key characteristics of {}?",
            "What does the document say about {}?",
            "Which statement best describes {}?",
            "What is the primary function of {}?",
            "According to the content, {} is:",
        ]
        
        # Extract key concepts
        key_terms = self.extract_key_concepts(text)
        
        if not key_terms:
            st.warning("Could not extract enough key concepts from the PDF.")
            return []
        
        used_terms = set()
        
        for i in range(min(num_questions, len(key_terms))):
            # Select a unique term
            available_terms = [term for term in key_terms if term not in used_terms]
            if not available_terms:
                break
                
            term = random.choice(available_terms)
            used_terms.add(term)
            
            # Create question
            question_text = random.choice(question_patterns).format(term)
            
            # Find context sentences containing the term
            context_sentences = [s for s in sentences if term.lower() in s.lower()]
            
            if not context_sentences:
                continue
            
            # Use the most relevant sentence as correct answer
            correct_context = context_sentences,[object Object],
            
            # Create a more concise correct answer
            correct_answer = f"A concept related to {term} as described in the document"
            if len(correct_context) < 100:
                correct_answer = correct_context
            
            # Generate plausible distractors
            other_sentences = [s for s in sentences if term.lower() not in s.lower()]
            
            distractors = []
            if len(other_sentences) >= 3:
                distractors = random.sample(other_sentences, 3)
            else:
                # Generate generic distractors if not enough content
                distractors = [
                    f"An unrelated concept not mentioned in the document",
                    f"A different topic entirely separate from {term}",
                    f"Information not covered in this document"
                ]
            
            # Ensure distractors are reasonably sized
            distractors = [d[:100] + "..." if len(d) > 100 else d for d in distractors]
            
            # Combine options and shuffle
            options = [correct_answer] + distractors[:3]
            random.shuffle(options)
            
            questions.append({
                'question': question_text,
                'options': options,
                'correct_answer': correct_answer,
                'explanation': f"This information relates to {term} as mentioned in the document: {correct_context[:150]}...",
                'topic': term
            })
        
        return questions
    
    def generate_true_false_questions(self, text: str, num_questions: int = 3) -> List[Dict]:
        """Generate true/false questions"""
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        questions = []
        
        for i in range(min(num_questions, len(sentences))):
            sentence = sentences[i]
            
            # Create true statement
            true_question = {
                'question': f"True or False: {sentence}",
                'options': ['True', 'False'],
                'correct_answer': 'True',
                'explanation': f"This statement is directly from the document.",
                'type': 'true_false'
            }
            
            questions.append(true_question)
            
            # Create false statement by modification
            if i + 1 < len(sentences):
                # Simple negation or modification
                modified_sentence = sentence.replace("is", "is not").replace("are", "are not")
                false_question = {
                    'question': f"True or False: {modified_sentence}",
                    'options': ['True', 'False'],
                    'correct_answer': 'False',
                    'explanation': f"This is a modified version of information in the document.",
                    'type': 'true_false'
                }
                questions.append(false_question)
        
        return questions[:num_questions]

def display_welcome_screen():
    """Display the welcome screen with instructions"""
    st.markdown("""
    ## 🎯 Welcome to AI Quiz Generator!
    
    Transform your PDF documents into engaging interactive quizzes instantly!
    
    ### 📋 **Key Features:**
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>📄 Smart PDF Processing</h4>
            <p>Advanced text extraction from any PDF document with progress tracking</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>🤖 Intelligent Question Generation</h4>
            <p>AI-powered algorithms create relevant multiple-choice and true/false questions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>📊 Comprehensive Analytics</h4>
            <p>Detailed results with explanations and downloadable reports</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    ### 🚀 **How to Get Started:**
    
    1. **📤 Upload Your PDF**: Use the file uploader in the sidebar to select your document
    2. **⚙️ Customize Settings**: Choose the number of questions and question types
    3. **🎯 Generate Quiz**: Click the generate button to create your personalized quiz
    4. **📝 Take the Quiz**: Answer the questions at your own pace
    5. **📈 View Results**: Get instant feedback with detailed explanations
    6. **💾 Export Data**: Download your results for future reference
    
    ### 💡 **Pro Tips:**
    - **Better PDFs = Better Questions**: Use documents with clear, structured text
    - **Mix Question Types**: Combine multiple-choice and true/false for variety
    - **Review Explanations**: Learn from both correct and incorrect answers
    - **Export Results**: Track your progress over time
    
    **Ready to create your first quiz?** 👆 Upload a PDF file in the sidebar to begin!
    """)
    
    # Sample quiz preview
    with st.expander("🔍 See Sample Quiz Question"):
        st.markdown("""
        **Sample Question:**
        
        **What is the primary purpose of machine learning algorithms?**
        
        A) To replace human decision-making entirely  
        B) To identify patterns in data and make predictions  ✅  
        C) To store large amounts of data  
        D) To create user interfaces  
        
        **Explanation:** Machine learning algorithms are designed to analyze data, identify patterns, and make predictions or decisions based on that analysis.
        """)

def display_quiz_interface(questions: List[Dict]):
    """Display the interactive quiz interface"""
    st.markdown('<h2 style="color: #1f77b4;">🧠 Take Your Quiz</h2>', unsafe_allow_html=True)
    
    with st.form("quiz_form"):
        for i, q in enumerate(questions):
            st.markdown(f'<div class="question-box">', unsafe_allow_html=True)
            
            # Question header with topic if available
            topic_info = f" (Topic: {q.get('topic', 'General')})" if q.get('topic') else ""
            st.markdown(f"**Question {i+1}{topic_info}**")
            
            # Question text
            st.markdown(f"**{q['question']}**")
            
            # Options
            user_answer = st.radio(
                f"Select your answer:",
                options=q['options'],
                key=f"q_{i}",
                index=None,
                help=f"Choose the best answer for question {i+1}"
            )
            
            if user_answer:
                st.session_state.user_answers[i] = user_answer
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Add separator except for last question
            if i < len(questions) - 1:
                st.markdown("---")
        
        # Submit button with styling
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button(
            "📝 Submit Quiz", 
            type="primary",
            help="Submit your answers to see results"
        )
        
        if submitted:
            if len(st.session_state.user_answers) == 0:
                st.warning("⚠️ Please answer at least one question before submitting!")
            else:
                st.session_state.quiz_submitted = True
                st.rerun()

def display_quiz_results(questions: List[Dict], user_answers: Dict):
    """Display comprehensive quiz results"""
    st.markdown('<h2 style="color: #1f77b4;">📊 Your Quiz Results</h2>', unsafe_allow_html=True)
    
    # Calculate score
    score = 0
    total_questions = len(questions)
    answered_questions = len(user_answers)
    
    results_data = []
    
    for i, q in enumerate(questions):
        user_answer = user_answers.get(i, "Not answered")
        correct_answer = q['correct_answer']
        is_correct = user_answer == correct_answer
        
        if is_correct:
            score += 1
        
        results_data.append({
            'Question': f"Q{i+1}",
            'Topic': q.get('topic', 'General'),
            'Your Answer': user_answer if user_answer != "Not answered" else "❌ Skipped",
            'Correct Answer': correct_answer,
            'Status': '✅ Correct' if is_correct else ('❌ Incorrect' if user_answer != "Not answered" else '⏭️ Skipped'),
            'Points': 1 if is_correct else 0
        })
    
    # Score display with styling
    percentage = (score / total_questions) * 100 if total_questions > 0 else 0
    
    if percentage >= 80:
        score_class = "excellent-score"
        score_emoji = "🎉"
        score_message = "Excellent! Outstanding performance!"
    elif percentage >= 60:
        score_class = "good-score"
        score_emoji = "👍"
        score_message = "Good job! Solid understanding shown."
    else:
        score_class = "poor-score"
        score_emoji = "📚"
        score_message = "Keep studying! Room for improvement."
    
    st.markdown(f"""
    <div class="score-display {score_class}">
        {score_emoji} Final Score: {score}/{total_questions} ({percentage:.1f}%)
        <br><small>{score_message}</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Performance metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Questions Answered", f"{answered_questions}/{total_questions}")
    with col2:
        st.metric("Correct Answers", score)
    with col3:
        st.metric("Accuracy Rate", f"{percentage:.1f}%")
    with col4:
        completion_rate = (answered_questions / total_questions) * 100
        st.metric("Completion Rate", f"{completion_rate:.1f}%")
    
    st.markdown("---")
    
    # Detailed question-by-question results
    st.subheader("📋 Detailed Question Analysis")
    
    for i, q in enumerate(questions):
        user_answer = user_answers.get(i, "Not answered")
        correct_answer = q['correct_answer']
        is_correct = user_answer == correct_answer
        was_answered = user_answer != "Not answered"
        
        # Determine status and styling
        if not was_answered:
            status = "⏭️ Skipped"
            expander_label = f"Question {i+1} - {status}"
        elif is_correct:
            status = "✅ Correct"
            expander_label = f"Question {i+1} - {status}"
        else:
            status = "❌ Incorrect"
            expander_label = f"Question {i+1} - {status}"
        
        with st.expander(expander_label):
            st.markdown(f"**Question:** {q['question']}")
            
            if q.get('topic'):
                st.markdown(f"**Topic:** {q['topic']}")
            
            if was_answered:
                if is_correct:
                    st.markdown(f'<div class="correct-answer">✅ Your answer: {user_answer}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="incorrect-answer">❌ Your answer: {user_answer}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="correct-answer">✅ Correct answer: {correct_answer}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="incorrect-answer">⏭️ Question was skipped</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="correct-answer">✅ Correct answer: {correct_answer}</div>', unsafe_allow_html=True)
            
            # Show explanation
            explanation = q.get('explanation', 'No explanation available.')
            st.markdown(f"**💡 Explanation:** {explanation}")
    
    # Results summary table
    st.subheader("📊 Results Summary Table")
    results_df = pd.DataFrame(results_data)
    st.dataframe(results_df, use_container_width=True)
    
    # Export options
    st.subheader("💾 Export Your Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV export
        csv = results_df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"quiz_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            help="Download detailed results as CSV file"
        )
    
    with col2:
        # JSON export with more details
        detailed_results = {
            'quiz_metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_questions': total_questions,
                'questions_answered': answered_questions,
                'score': score,
                'percentage': percentage
            },
            'questions_and_answers': [
                {
                    'question_number': i + 1,
                    'question_text': q['question'],
                    'topic': q.get('topic', 'General'),
                    'user_answer': user_answers.get(i, "Not answered"),
                    'correct_answer': q['correct_answer'],
                    'is_correct': user_answers.get(i) == q['correct_answer'],
                    'explanation': q.get('explanation', '')
                }
                for i, q in enumerate(questions)
            ]
        }
        
        json_str = json.dumps(detailed_results, indent=2)
        st.download_button(
            label="📥 Download as JSON",
            data=json_str,
            file_name=f"quiz_results_detailed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            help="Download comprehensive results as JSON file"
        )

def main():
    """Main application function"""
    # Header
    st.markdown('<h1 class="main-header">📚 AI Quiz Generator</h1>', unsafe_allow_html=True)
    st.markdown("*Transform your PDFs into engaging quizzes instantly!*")
    st.markdown("---")
    
    # Initialize session state
    if 'quiz_generated' not in st.session_state:
        st.session_state.quiz_generated = False
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'pdf_processed' not in st.session_state:
        st.session_state.pdf_processed = False
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.header("⚙️ Quiz Configuration")
        
        # Quiz settings
        st.subheader("🎯 Quiz Settings")
        num_questions = st.slider(
            "Number of Questions", 
            min_value=3, 
            max_value=20, 
            value=8,
            help="Choose how many questions to generate"
        )
        
        question_types = st.multiselect(
            "Question Types",
            ["Multiple Choice", "True/False"],
            default=["Multiple Choice"],
            help="Select the types of questions to include"
        )
        
        difficulty_level = st.selectbox(
            "Difficulty Level",
            ["Easy", "Medium", "Hard"],
            index=1,
            help="This affects question complexity (feature in development)"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # File upload section
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.subheader("📄 Upload PDF Document")
        
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Upload any PDF document to generate quiz questions",
            accept_multiple_files=False
        )
        
        # File info
        if uploaded_file:
            file_size = len(uploaded_file.read()) / 1024 / 1024  # MB
            uploaded_file.seek(0)  # Reset file pointer
            st.info(f"📄 **{uploaded_file.name}**\n\nSize: {file_size:.2f} MB")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Generate quiz button
        if uploaded_file:
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            
            if st.button("🚀 Generate Quiz", type="primary", use_container_width=True):
                with st.spinner("🔄 Processing PDF and generating questions..."):
                    quiz_gen = QuizGenerator()
                    
                    # Extract text
                    pdf_text = quiz_gen.extract_text_from_pdf(uploaded_file)
                    
                    if pdf_text:
                        # Clean text
                        cleaned_text = quiz_gen.clean_text(pdf_text)
                        
                        if len(cleaned_text) < 100:
                            st.error("❌ The PDF content is too short to generate meaningful questions. Please try a different document.")
                        else:
                            # Generate questions based on selected types
                            all_questions = []
                            
                            if "Multiple Choice" in question_types:
                                mc_questions = quiz_gen.generate_multiple_choice_questions(
                                    cleaned_text, 
                                    num_questions
                                )
                                all_questions.extend(mc_questions)
                            
                            if "True/False" in question_types:
                                tf_count = max(1, num_questions // 4)  # 25% true/false
                                tf_questions = quiz_gen.generate_true_false_questions(
                                    cleaned_text, 
                                    tf_count
                                )
                                all_questions.extend(tf_questions)
                            
                            # Limit to requested number and shuffle
                            if all_questions:
                                random.shuffle(all_questions)
                                final_questions = all_questions[:num_questions]
                                
                                st.session_state.questions = final_questions
                                st.session_state.quiz_generated = True
                                st.session_state.user_answers = {}
                                st.session_state.quiz_submitted = False
                                st.session_state.pdf_processed = True
                                
                                st.success(f"✅ Successfully generated {len(final_questions)} questions!")
                                st.balloons()
                            else:
                                st.error("❌ Failed to generate questions. The PDF content might not be suitable for quiz generation.")
                    else:
                        st.error("❌ Could not extract text from PDF. Please ensure the file is not corrupted or password-protected.")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Reset button
        if st.session_state.quiz_generated:
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            if st.button("🔄 Reset & Create New Quiz", use_container_width=True):
                # Clear all session state
                for key in ['quiz_generated', 'user_answers', 'quiz_submitted', 'questions', 'pdf_processed']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content area
    if st.session_state.quiz_generated and not st.session_state.quiz_submitted:
        # Display quiz interface
        display_quiz_interface(st.session_state.questions)
        
    elif st.session_state.quiz_submitted:
        # Display results
        display_quiz_results(st.session_state.questions, st.session_state.user_answers)
        
    else:
        # Display welcome screen
        display_welcome_screen()

if __name__ == "__main__":
    main()
