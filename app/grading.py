from flask import Blueprint, render_template, request, jsonify, session, flash, current_app, redirect
import os
import uuid
import json
from werkzeug.utils import secure_filename
from app.utils.ai_grader import AIGrader
from app.utils.file_processor import FileProcessor

# Create blueprint for grading system
grading_bp = Blueprint('grading', __name__, 
                      template_folder='templates/grading',
                      url_prefix='/grading')

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'txt', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# Initialize AI Grader
ai_grader = AIGrader()
file_processor = FileProcessor()

@grading_bp.route('/')
def index():
    return render_template('grading/index.html')

@grading_bp.route('/upload-questions', methods=['GET', 'POST'])
def upload_questions():
    if request.method == 'POST':
        # Generate unique session ID for this grading session
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
        
        # Create session directory
        session_dir = f"sessions/{session_id}"
        os.makedirs(session_dir, exist_ok=True)
        
        # Process question paper
        if 'question_file' not in request.files:
            flash('No file selected')
            return render_template('grading/upload_questions.html')
        
        file = request.files['question_file']
        if file.filename == '':
            flash('No file selected')
            return render_template('grading/upload_questions.html')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            question_path = os.path.join(session_dir, 'questions' + os.path.splitext(filename)[1])
            file.save(question_path)
            
            # Extract text from question paper
            try:
                questions_data = file_processor.extract_questions(question_path)
                session['questions_data'] = questions_data
                session['total_marks'] = sum(q.get('marks', 1) for q in questions_data)
                
                flash('Question paper uploaded successfully!')
                return render_template('grading/upload_answers.html', 
                                    questions_count=len(questions_data),
                                    total_marks=session['total_marks'])
            
            except Exception as e:
                flash(f'Error processing question paper: {str(e)}')
                return render_template('grading/upload_questions.html')
    
    return render_template('grading/upload_questions.html')

@grading_bp.route('/upload-answers', methods=['POST'])
def upload_answers():
    if 'question_file' not in request.files or 'student_id' not in request.form:
        return jsonify({'error': 'Missing file or student ID'}), 400
    
    file = request.files['question_file']
    student_id = request.form['student_id']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'error': 'Session expired'}), 400
        
        session_dir = f"sessions/{session_id}"
        filename = secure_filename(file.filename)
        answer_path = os.path.join(session_dir, f'answers_{student_id}' + os.path.splitext(filename)[1])
        file.save(answer_path)
        
        try:
            # Extract answers from student script
            questions_data = session.get('questions_data', [])
            student_answers = file_processor.extract_answers(answer_path, len(questions_data))
            
            # Grade answers using AI
            grading_results = ai_grader.grade_answers(questions_data, student_answers, student_id)
            
            # Store results in session
            if 'grading_results' not in session:
                session['grading_results'] = {}
            session['grading_results'][student_id] = grading_results
            
            return jsonify({
                'success': True,
                'results': grading_results,
                'student_id': student_id
            })
            
        except Exception as e:
            return jsonify({'error': f'Error processing answers: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@grading_bp.route('/results/<student_id>')
def show_results(student_id):
    results = session.get('grading_results', {}).get(student_id)
    if not results:
        flash('Results not found')
        return redirect('/')
    
    return render_template('grading/results.html', results=results)

@grading_bp.route('/batch-summary')
def batch_summary():
    grading_results = session.get('grading_results', {})
    if not grading_results:
        flash('No grading results available')
        return redirect('/')
    
    summary = ai_grader.generate_batch_summary(grading_results)
    return render_template('grading/summary.html', summary=summary)

@grading_bp.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy'})

