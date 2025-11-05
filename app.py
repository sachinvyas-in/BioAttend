"""
BioAttend: Biometric Smart Attendance System (Simulated Iris Scanner)
Main Flask Application
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime, date
import sqlite3

# Import our custom modules
from database import (
    init_database, add_student, get_student_by_roll_no, 
    get_student_by_iris_template, mark_attendance, 
    get_attendance_by_date, get_all_students,
    get_student_attendance_history, get_student_by_id,
    update_student, delete_student, get_student_stats
)
from biometric_utils import (
    process_enrollment_image, process_verification_image,
    validate_image_format
)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'bioattend_secret_key_2024_dev')

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE  # Enforce upload size limit

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database on startup
init_database()


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/enroll', methods=['GET', 'POST'])
def enroll():
    """Student enrollment page"""
    if request.method == 'GET':
        return render_template('enroll.html')
    
    # Handle POST request
    name = request.form.get('name', '').strip()
    roll_no = request.form.get('roll_no', '').strip()
    
    # Validate input
    if not name or not roll_no:
        flash('Please fill in all required fields.', 'error')
        return render_template('enroll.html')
    
    # Check if file was uploaded
    if 'iris_image' not in request.files:
        flash('Please upload an iris image.', 'error')
        return render_template('enroll.html')
    
    file = request.files['iris_image']
    
    # Check if file is selected
    if file.filename == '':
        flash('Please select an iris image file.', 'error')
        return render_template('enroll.html')
    
    # Validate file
    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload PNG, JPG, JPEG, BMP, or TIFF images only.', 'error')
        return render_template('enroll.html')
    
    try:
        # Process the image
        result = process_enrollment_image(file)
        
        if not result['success']:
            flash(f'Image processing error: {result["error"]}', 'error')
            return render_template('enroll.html')
        
        iris_template = result['iris_template']
        
        # Check if student already exists
        existing_student = get_student_by_roll_no(roll_no)
        if existing_student:
            flash(f'Student with roll number {roll_no} is already enrolled.', 'error')
            return render_template('enroll.html')
        
        # Check if iris template already exists
        existing_iris = get_student_by_iris_template(iris_template)
        if existing_iris:
            flash('This iris pattern is already registered with another student.', 'error')
            return render_template('enroll.html')
        
        # Add student to database
        student_id = add_student(name, roll_no, iris_template)
        
        if student_id:
            flash(f'Student {name} (Roll No: {roll_no}) enrolled successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Enrollment failed. Please try again.', 'error')
            return render_template('enroll.html')
            
    except Exception as e:
        flash(f'An error occurred during enrollment: {str(e)}', 'error')
        return render_template('enroll.html')


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    """Attendance verification page"""
    if request.method == 'GET':
        return render_template('verify.html')
    
    # Handle POST request
    if 'iris_image' not in request.files:
        flash('Please upload an iris image for verification.', 'error')
        return render_template('verify.html')
    
    file = request.files['iris_image']
    
    if file.filename == '':
        flash('Please select an iris image file.', 'error')
        return render_template('verify.html')
    
    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload PNG, JPG, JPEG, BMP, or TIFF images only.', 'error')
        return render_template('verify.html')
    
    try:
        # Get all student templates for matching
        students = get_all_students()
        stored_templates = []
        
        # Get iris templates from database
        for student in students:
            student_data = get_student_by_roll_no(student['roll_no'])
            if student_data:
                stored_templates.append(student_data['iris_template'])
        
        # Process verification
        result = process_verification_image(file, stored_templates)
        
        if not result['success']:
            flash(f'Image processing error: {result["error"]}', 'error')
            return render_template('verify.html')
        
        if result['match_found']:
            # Find the student with matching template
            matched_template = result['matched_template']
            student = get_student_by_iris_template(matched_template)
            
            if student:
                # Mark attendance
                today = datetime.now().strftime('%Y-%m-%d')
                attendance_marked = mark_attendance(student['id'], today)
                
                if attendance_marked:
                    flash(f'Attendance marked successfully for {student["name"]} (Roll No: {student["roll_no"]})', 'success')
                else:
                    flash(f'Attendance already marked today for {student["name"]} (Roll No: {student["roll_no"]})', 'warning')
                
                return render_template('verify.html', student=student, verified=True)
            else:
                flash('Student data not found. Please contact administrator.', 'error')
        else:
            flash('Iris verification failed. Student not recognized or not enrolled.', 'error')
        
        return render_template('verify.html')
        
    except Exception as e:
        flash(f'An error occurred during verification: {str(e)}', 'error')
        return render_template('verify.html')


@app.route('/reports')
def reports():
    """Attendance reports page"""
    # Get today's date
    today = datetime.now().strftime('%Y-%m-%d')
    selected_date = request.args.get('date', today)
    
    try:
        # Get attendance records for the selected date
        attendance_records = get_attendance_by_date(selected_date)
        
        # Get all students for enrollment statistics
        all_students = get_all_students()
        total_students = len(all_students)
        present_today = len(attendance_records)
        absent_today = total_students - present_today
        
        return render_template('reports.html', 
                             attendance_records=attendance_records,
                             selected_date=selected_date,
                             total_students=total_students,
                             present_today=present_today,
                             absent_today=absent_today)
    
    except Exception as e:
        flash(f'Error loading reports: {str(e)}', 'error')
        return render_template('reports.html', attendance_records=[], selected_date=selected_date)


@app.route('/students')
def students():
    """Students management page"""
    try:
        all_students = get_all_students()
        return render_template('students.html', students=all_students)
    except Exception as e:
        flash(f'Error loading students: {str(e)}', 'error')
        return render_template('students.html', students=[])


@app.route('/edit-student/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    """Edit student information"""
    student = get_student_by_id(student_id)
    if not student:
        flash('Student not found.', 'error')
        return redirect(url_for('students'))
    
    if request.method == 'GET':
        return render_template('edit_student.html', student=student)
    
    # Handle POST request
    name = request.form.get('name', '').strip()
    roll_no = request.form.get('roll_no', '').strip()
    update_iris = request.form.get('update_iris') == 'on'
    
    # Validate input
    if not name or not roll_no:
        flash('Please fill in all required fields.', 'error')
        return render_template('edit_student.html', student=student)
    
    iris_template = None
    
    # Handle iris image update if requested
    if update_iris:
        if 'iris_image' not in request.files:
            flash('Please upload an iris image to update biometric data.', 'error')
            return render_template('edit_student.html', student=student)
        
        file = request.files['iris_image']
        if file.filename == '':
            flash('Please select an iris image file.', 'error')
            return render_template('edit_student.html', student=student)
        
        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload PNG, JPG, JPEG, BMP, or TIFF images only.', 'error')
            return render_template('edit_student.html', student=student)
        
        # Process the new iris image
        result = process_enrollment_image(file)
        if not result['success']:
            flash(f'Image processing error: {result["error"]}', 'error')
            return render_template('edit_student.html', student=student)
        
        iris_template = result['iris_template']
        
        # Check if this iris template already exists for another student
        existing_iris = get_student_by_iris_template(iris_template)
        if existing_iris and existing_iris['id'] != student_id:
            flash('This iris pattern is already registered with another student.', 'error')
            return render_template('edit_student.html', student=student)
    
    try:
        # Update student
        success, message = update_student(student_id, name, roll_no, iris_template)
        
        if success:
            flash(f'Student {name} updated successfully!', 'success')
            return redirect(url_for('students'))
        else:
            flash(f'Update failed: {message}', 'error')
            return render_template('edit_student.html', student=student)
            
    except Exception as e:
        flash(f'An error occurred while updating student: {str(e)}', 'error')
        return render_template('edit_student.html', student=student)


@app.route('/delete-student/<int:student_id>', methods=['POST'])
def delete_student_route(student_id):
    """Delete a student"""
    try:
        success, message = delete_student(student_id)
        
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
            
    except Exception as e:
        flash(f'An error occurred while deleting student: {str(e)}', 'error')
    
    return redirect(url_for('students'))


@app.route('/api/student/<int:student_id>/attendance')
def student_attendance_api(student_id):
    """API endpoint to get student attendance history"""
    try:
        attendance_history = get_student_attendance_history(student_id)
        return jsonify({
            'success': True,
            'attendance': [dict(record) for record in attendance_history]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    flash('File too large. Please upload an image smaller than 16MB.', 'error')
    return redirect(request.url)


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return render_template('500.html'), 500


if __name__ == '__main__':
    # Make sure uploads directory exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)