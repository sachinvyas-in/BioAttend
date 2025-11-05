"""
Biometric simulation utilities for iris template generation and matching
"""

import hashlib
from PIL import Image
import io
import base64


def generate_iris_template(image_file):
    """
    Simulate iris template generation by creating a hash from the uploaded image.
    In a real system, this would extract biometric features from the iris.
    
    Args:
        image_file: Uploaded image file object
    
    Returns:
        str: Hashed template representing the iris features
    """
    try:
        # Read the image data
        image_data = image_file.read()
        
        # Reset file pointer for potential future use
        image_file.seek(0)
        
        # Create hash from image data (simulating feature extraction)
        hash_object = hashlib.sha256(image_data)
        iris_template = hash_object.hexdigest()
        
        return iris_template
        
    except Exception as e:
        print(f"Error generating iris template: {e}")
        return None


def validate_image_format(image_file):
    """
    Validate that the uploaded file is a valid image
    
    Args:
        image_file: Uploaded file object
    
    Returns:
        bool: True if valid image, False otherwise
    """
    try:
        # Try to open the image with PIL
        image = Image.open(image_file)
        
        # Reset file pointer
        image_file.seek(0)
        
        # Check if it's a supported format
        if image.format and image.format.lower() in ['jpeg', 'jpg', 'png', 'bmp', 'tiff']:
            return True
        else:
            return False
            
    except Exception:
        return False


def match_iris_templates(template1, template2, threshold=0.95):
    """
    Simulate iris template matching by comparing hash strings.
    In a real system, this would use sophisticated biometric matching algorithms.
    
    Args:
        template1: First iris template hash
        template2: Second iris template hash
        threshold: Matching threshold (not used in exact hash matching)
    
    Returns:
        bool: True if templates match, False otherwise
    """
    # For simulation, we use exact hash matching
    # In real biometric systems, fuzzy matching would be used
    return template1 == template2


def get_image_info(image_file):
    """
    Get basic information about the uploaded image
    
    Args:
        image_file: Uploaded image file object
    
    Returns:
        dict: Image information (size, format, etc.)
    """
    try:
        image = Image.open(image_file)
        image_file.seek(0)
        
        return {
            'format': image.format,
            'size': image.size,
            'mode': image.mode,
            'is_valid': True
        }
    except Exception as e:
        return {
            'is_valid': False,
            'error': str(e)
        }


def process_enrollment_image(image_file):
    """
    Process image for enrollment (validation + template generation)
    
    Args:
        image_file: Uploaded image file object
    
    Returns:
        dict: Processing result with template or error
    """
    # Validate image format
    if not validate_image_format(image_file):
        return {
            'success': False,
            'error': 'Invalid image format. Please upload a JPEG, PNG, BMP, or TIFF image.'
        }
    
    # Get image info
    image_info = get_image_info(image_file)
    
    # Generate iris template
    iris_template = generate_iris_template(image_file)
    
    if iris_template:
        return {
            'success': True,
            'iris_template': iris_template,
            'image_info': image_info
        }
    else:
        return {
            'success': False,
            'error': 'Failed to generate iris template from the image.'
        }


def process_verification_image(image_file, stored_templates):
    """
    Process image for verification against stored templates
    
    Args:
        image_file: Uploaded image file object
        stored_templates: List of stored iris templates to match against
    
    Returns:
        dict: Verification result
    """
    # Validate and process the image
    process_result = process_enrollment_image(image_file)
    
    if not process_result['success']:
        return process_result
    
    # Get the template from uploaded image
    uploaded_template = process_result['iris_template']
    
    # Try to match against all stored templates
    for template in stored_templates:
        if match_iris_templates(uploaded_template, template):
            return {
                'success': True,
                'match_found': True,
                'matched_template': template
            }
    
    # No match found
    return {
        'success': True,
        'match_found': False,
        'uploaded_template': uploaded_template
    }