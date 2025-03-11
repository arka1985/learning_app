import streamlit as st
import json
from fpdf import FPDF
from datetime import datetime

def load_content(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def generate_pdf_report(user_data, module_scores):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    
    # Header
    pdf.cell(0, 10, "Health Research Assessment Report", 0, 1, 'C')
    pdf.ln(10)
    
    # User Details
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Name: {user_data['name']}", 0, 1)
    pdf.cell(0, 10, f"Roll Number: {user_data['roll_number']}", 0, 1)
    pdf.cell(0, 10, f"Date & Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1)
    pdf.ln(10)
    
    # Scores Table
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Assessment Results", 0, 1)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, "Module", 1)
    pdf.cell(40, 10, "Score", 1)
    pdf.cell(40, 10, "Total Questions", 1)
    pdf.ln()
    
    pdf.set_font("Arial", '', 12)
    total_score = 0
    total_questions = 0
    for module_idx, score in module_scores.items():
        module = content["modules"][int(module_idx)]
        questions = len(module["assessment"])
        pdf.cell(100, 10, module["title"], 1)
        pdf.cell(40, 10, str(score), 1)
        pdf.cell(40, 10, str(questions), 1)
        pdf.ln()
        total_score += score
        total_questions += questions
    
    # Footer
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Total Score: {total_score}/{total_questions}", 0, 1)
    pdf.ln(5)
    pdf.set_font("Arial", 'I', 10)
    pdf.multi_cell(0, 5, "Note: This report is generated for educational and research purposes only.")
    
    # Save PDF
    filename = f"Report_{user_data['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename

# Initialize session state
if "current_module" not in st.session_state:
    st.session_state.current_module = 0
if "scores" not in st.session_state:
    st.session_state.scores = {}
if "module_scores" not in st.session_state:
    st.session_state.module_scores = {}
if "username" not in st.session_state:
    st.session_state.username = ""
if "roll_number" not in st.session_state:
    st.session_state.roll_number = ""
if "module_completed" not in st.session_state:
    st.session_state.module_completed = {}
if "all_modules_completed" not in st.session_state:
    st.session_state.all_modules_completed = False
if "start_quiz" not in st.session_state:
    st.session_state.start_quiz = False
if "report_generated" not in st.session_state:
    st.session_state.report_generated = False

content = load_content("content.json")

st.title("_Module_ of Classification of Health : Research[cool]")

# Sidebar
st.sidebar.title("Generative AI Based Module for Learning Research Methodology")
st.sidebar.write("Enter your details to start:")
name = st.sidebar.text_input("Name", key="name_input")
roll_number = st.sidebar.text_input("Roll Number", key="roll_number_input")

if st.sidebar.button("Start Module"):
    if name and roll_number:
        st.session_state.username = name
        st.session_state.roll_number = roll_number
        st.session_state.start_quiz = True
    else:
        st.sidebar.error("Please enter both your name and roll number.")

# Footer Note
st.sidebar.markdown("---")
st.sidebar.caption("It is for educational and research purpose")
st.sidebar.caption("Designed and Developed by Dr. Arkaprabha Sau, MBBS, MD (Gold Medal), DPH and PhD (CSE-AI-ML)")

# Main content
if st.session_state.username and st.session_state.roll_number and st.session_state.start_quiz:
    if not st.session_state.all_modules_completed:
        current_module = content["modules"][st.session_state.current_module]
        st.title(current_module["title"])

        # Display sections
        for section in current_module["sections"]:
            st.subheader(section["heading"])
            st.write(section["content"])

        # MCQ Assessment
        st.markdown("---")
        st.subheader("Assessment")
        all_answered = True
        for q_idx, question in enumerate(current_module["assessment"]):
            key = f"{current_module['title']}_{q_idx}"
            st.write(f"**Question {q_idx + 1}:** {question['question']}")
            answer = st.radio(
                "Select your answer:",
                question["options"],
                key=key,
                index=None if key not in st.session_state.scores else st.session_state.scores[key]
            )
            if answer is None:
                all_answered = False
            st.session_state.scores[key] = question["options"].index(answer) if answer is not None else None

        # Submit Score Logic
        if all_answered:
            if st.button("Submit Score"):
                module_score = 0
                for q_idx, question in enumerate(current_module["assessment"]):
                    key = f"{current_module['title']}_{q_idx}"
                    if st.session_state.scores.get(key) == question["options"].index(question["correct"]):
                        module_score += 1

                st.session_state.module_completed[st.session_state.current_module] = True
                st.session_state.module_scores[str(st.session_state.current_module)] = module_score

                # Save to leaderboard
                try:
                    with open("leaderboard.json", "r") as f:
                        leaderboard = json.load(f)
                except FileNotFoundError:
                    leaderboard = {}
                
                leaderboard_key = f"{st.session_state.username} ({st.session_state.roll_number})"
                leaderboard[leaderboard_key] = st.session_state.module_scores
                
                with open("leaderboard.json", "w") as f:
                    json.dump(leaderboard, f)

                # Navigate to next module
                if st.session_state.current_module < len(content["modules"]) - 1:
                    st.session_state.current_module += 1
                    st.rerun()
                else:
                    st.session_state.all_modules_completed = True
                    st.session_state.report_generated = True
                    st.rerun()

        else:
            st.warning("Please answer all questions to submit your score.")

        # Navigation
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Previous Module") and st.session_state.current_module > 0:
                st.session_state.current_module -= 1
                st.rerun()
        with col2:
            if st.session_state.module_completed.get(st.session_state.current_module, False):
                if st.button("Next Module") and st.session_state.current_module < len(content["modules"]) - 1:
                    st.session_state.current_module += 1
                    st.rerun()
            else:
                st.write("Complete the assessment and submit your score to proceed.")

    else:
        st.success("🎉 Congratulations! You have completed all modules.")
        st.balloons()
        
        # Generate and download report
        if st.session_state.report_generated:
            user_data = {
                "name": st.session_state.username,
                "roll_number": st.session_state.roll_number
            }
            report_filename = generate_pdf_report(user_data, st.session_state.module_scores)
            with open(report_filename, "rb") as f:
                st.download_button(
                    label="Download Full Report",
                    data=f,
                    file_name=report_filename,
                    mime="application/pdf"
                )
            st.session_state.report_generated = False  # Prevent regeneration on rerun

# Leaderboard
st.sidebar.title("Leaderboard")
if st.sidebar.button("Show Leaderboard"):
    try:
        with open("leaderboard.json", "r") as f:
            leaderboard = json.load(f)
        
        if not leaderboard:
            st.sidebar.warning("Leaderboard is empty!")
        else:
            # Get module titles
            modules = content["modules"]
            module_headers = [module["title"] for module in modules]
            
            # Create leaderboard table
            st.sidebar.markdown("### 📊 Leaderboard")
            header = "| Student | " + " | ".join(module_headers) + " | Total |"
            separator = "|--------|" + "|".join(["---------" for _ in module_headers]) + "|-------|"
            
            st.sidebar.markdown(header)
            st.sidebar.markdown(separator)
            
            for student, scores in leaderboard.items():
                module_scores = [str(scores.get(str(idx), 0)) for idx in range(len(modules))]
                total = sum([int(score) for score in module_scores])
                row = f"| {student} | " + " | ".join(module_scores) + f" | {total} |"
                st.sidebar.markdown(row)
                
    except FileNotFoundError:
        st.sidebar.error("No leaderboard data available yet!")
    except json.JSONDecodeError:
        st.sidebar.error("Corrupted leaderboard data!")