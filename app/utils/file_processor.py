import PyPDF2
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import docx
import re
import os
import logging
import subprocess
import numpy as np
from scipy import ndimage

logger = logging.getLogger(__name__)

class FileProcessor:
    def __init__(self):
        self.tesseract_available = self._check_tesseract()
        if not self.tesseract_available:
            self._auto_configure_tesseract()
    
    def _check_tesseract(self):
        """Check if Tesseract OCR is available"""
        try:
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR is available")
            return True
        except (pytesseract.TesseractNotFoundError, Exception) as e:
            logger.warning(f"Tesseract OCR not found: {e}")
            return False
    
    def _auto_configure_tesseract(self):
        """Try to automatically configure Tesseract path"""
        possible_paths = [
            # Windows default paths
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            # Linux/Mac paths
            "/usr/bin/tesseract",
            "/usr/local/bin/tesseract",
            # Common Unix paths
            "/bin/tesseract",
            "/opt/local/bin/tesseract"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    pytesseract.pytesseract.tesseract_cmd = path
                    # Test if it works
                    pytesseract.get_tesseract_version()
                    logger.info(f"Tesseract found at: {path}")
                    self.tesseract_available = True
                    return
                except Exception as e:
                    logger.warning(f"Tesseract at {path} not working: {e}")
                    continue
        
        # Last attempt: try to find in PATH using command line
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(['where', 'tesseract'], capture_output=True, text=True)
            else:  # Linux/Mac
                result = subprocess.run(['which', 'tesseract'], capture_output=True, text=True)
            
            if result.returncode == 0:
                tesseract_path = result.stdout.strip().split('\n')[0]
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
                pytesseract.get_tesseract_version()
                logger.info(f"Tesseract found in PATH: {tesseract_path}")
                self.tesseract_available = True
        except Exception as e:
            logger.error(f"Could not find Tesseract in PATH: {e}")
    
    def extract_questions(self, file_path: str) -> list:
        """Extract questions from uploaded file"""
        text = self._extract_text(file_path)
        return self._parse_questions(text)
    
    def extract_answers(self, file_path: str, expected_questions: int) -> list:
        """Extract answers from student script"""
        text = self._extract_text(file_path)
        return self._parse_answers(text, expected_questions)
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from various file formats"""
        file_ext = file_path.split('.')[-1].lower()
        
        if file_ext == 'pdf':
            return self._extract_from_pdf(file_path)
        elif file_ext in ['png', 'jpg', 'jpeg']:
            return self._extract_from_image(file_path)
        elif file_ext == 'docx':
            return self._extract_from_docx(file_path)
        elif file_ext == 'txt':
            return self._extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def _extract_from_image(self, file_path: str) -> str:
        """Extract text from image using OCR"""
        try:
            if not self.tesseract_available:
                raise Exception(
                    "Tesseract OCR is not installed or not in PATH. "
                    "Please install Tesseract OCR to process images. "
                    "See installation instructions in the README."
                )
            
            image = Image.open(file_path)
            
            # Preprocess image for better OCR results
            image = self._preprocess_image(image)
            
            # Configure OCR for better accuracy
            custom_config = r'--oem 3 --psm 6'
            
            # Use OCR to extract text
            text = pytesseract.image_to_string(image, config=custom_config)
            
            if not text.strip():
                raise Exception("No text could be extracted from the image. Please ensure the image is clear and contains readable text.")
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            raise
    
    def _preprocess_image(self, image):
        """Preprocess image for better OCR results"""
        try:
            logger.info("Starting image preprocessing...")
            
            # Store original dimensions for reference
            original_width, original_height = image.size
            logger.info(f"Original image size: {original_width}x{original_height}")
            
            # Step 1: Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            logger.info("Converted to grayscale")
            
            # Step 2: Resize image if too small or too large
            image = self._resize_image(image)
            
            # Step 3: Remove noise
            image = self._remove_noise(image)
            
            # Step 4: Enhance contrast
            image = self._enhance_contrast(image)
            
            # Step 5: Enhance sharpness
            image = self._enhance_sharpness(image)
            
            # Step 6: Deskew image (correct rotation)
            image = self._deskew_image(image)
            
            # Step 7: Apply binary thresholding
            image = self._apply_threshold(image)
            
            # Step 8: Final enhancement
            image = self._final_enhancement(image)
            
            logger.info("Image preprocessing completed successfully")
            return image
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {e}")
            # Return the original image if preprocessing fails
            return image.convert('L') if image.mode != 'L' else image
    
    def _resize_image(self, image):
        """Resize image to optimal dimensions for OCR"""
        width, height = image.size
        
        # Define optimal size range for OCR
        min_size = 800
        max_size = 2400
        
        # Calculate scaling factor
        scale_factor = 1.0
        
        if max(width, height) > max_size:
            scale_factor = max_size / max(width, height)
        elif min(width, height) < min_size:
            scale_factor = min_size / min(width, height)
        
        if scale_factor != 1.0:
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            logger.info(f"Resized image to: {new_width}x{new_height} (scale: {scale_factor:.2f})")
        
        return image
    
    def _remove_noise(self, image):
        """Remove noise from image using various techniques"""
        try:
            # Convert to numpy array for processing
            img_array = np.array(image)
            
            # Method 1: Median filter for salt-and-pepper noise
            img_array = ndimage.median_filter(img_array, size=2)
            
            # Method 2: Gaussian filter for general noise
            img_array = ndimage.gaussian_filter(img_array, sigma=0.5)
            
            # Convert back to PIL Image
            image = Image.fromarray(img_array.astype(np.uint8))
            logger.info("Applied noise removal filters")
            
        except Exception as e:
            logger.warning(f"Noise removal failed: {e}")
        
        return image
    
    def _enhance_contrast(self, image):
        """Enhance image contrast"""
        try:
            enhancer = ImageEnhance.Contrast(image)
            # Adjust contrast factor based on image analysis
            image = enhancer.enhance(1.5)  # Increase contrast by 50%
            logger.info("Enhanced contrast")
        except Exception as e:
            logger.warning(f"Contrast enhancement failed: {e}")
        
        return image
    
    def _enhance_sharpness(self, image):
        """Enhance image sharpness"""
        try:
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.3)  # Increase sharpness by 30%
            logger.info("Enhanced sharpness")
        except Exception as e:
            logger.warning(f"Sharpness enhancement failed: {e}")
        
        return image
    
    def _deskew_image(self, image):
        """Correct image skew/rotation"""
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Calculate skew angle using Hough transform
            edges = ndimage.sobel(img_array)
            coords = np.column_stack(np.where(edges > edges.mean()))
            
            if len(coords) > 100:  # Only deskew if we have enough edge points
                try:
                    # Calculate angle using principal component analysis
                    angle = np.arctan2(*(coords - coords.mean(axis=0)).T)[0]
                    angle_deg = np.degrees(angle)
                    
                    # Only correct if skew is significant
                    if abs(angle_deg) > 0.5:
                        image = image.rotate(angle_deg, resample=Image.Resampling.BICUBIC, expand=True, fillcolor=255)
                        logger.info(f"Deskewed image by {angle_deg:.2f} degrees")
                
                except Exception as e:
                    logger.warning(f"Skew detection failed: {e}")
        
        except Exception as e:
            logger.warning(f"Deskewing failed: {e}")
        
        return image
    
    def _apply_threshold(self, image):
        """Apply adaptive thresholding for better text separation"""
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Use Otsu's method for automatic thresholding
            from skimage.filters import threshold_otsu
            try:
                thresh = threshold_otsu(img_array)
                binary = img_array > thresh
                img_array = (binary * 255).astype(np.uint8)
                logger.info("Applied Otsu thresholding")
            except ImportError:
                # Fallback to simple threshold if scikit-image not available
                threshold = np.mean(img_array)
                img_array = np.where(img_array > threshold, 255, 0).astype(np.uint8)
                logger.info("Applied mean thresholding")
            
            image = Image.fromarray(img_array)
            
        except Exception as e:
            logger.warning(f"Thresholding failed: {e}")
        
        return image
    
    def _final_enhancement(self, image):
        """Apply final enhancements for OCR optimization"""
        try:
            # Apply mild unsharp mask for clarity
            image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
            
            # Final brightness adjustment
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.1)  # Slight brightness increase
            
            logger.info("Applied final enhancements")
            
        except Exception as e:
            logger.warning(f"Final enhancement failed: {e}")
        
        return image
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        try:
            doc = docx.Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            raise
    
    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error extracting text from TXT: {e}")
            raise
    
    def _parse_questions(self, text: str) -> list:
        """Parse questions from extracted text"""
        questions = []
        
        if not text.strip():
            return [{'number': 1, 'text': 'No text extracted from file.', 'type': 'essay', 'marks': 1}]
        
        # Split by common question patterns
        patterns = [
            r'\bQ\d+\.', r'\bQuestion\s+\d+', r'\d+\.\s*\(', r'\n\d+\.\s'
        ]
        
        for pattern in patterns:
            parts = re.split(pattern, text)
            if len(parts) > 1:
                for i, part in enumerate(parts[1:], 1):
                    if part.strip():
                        questions.append({
                            'number': i,
                            'text': part.strip(),
                            'type': self._detect_question_type(part),
                            'marks': self._extract_marks(part)
                        })
                break
        
        # Fallback: split by newlines and look for numbered items
        if not questions:
            lines = text.split('\n')
            question_text = ""
            for i, line in enumerate(lines):
                if re.match(r'^\d+[\.\)]', line.strip()):
                    if question_text:
                        questions.append({
                            'number': len(questions) + 1,
                            'text': question_text.strip(),
                            'type': 'essay',
                            'marks': 1
                        })
                    question_text = line
                elif question_text:
                    question_text += "\n" + line
            
            if question_text:
                questions.append({
                    'number': len(questions) + 1,
                    'text': question_text.strip(),
                    'type': 'essay',
                    'marks': 1
                })
        
        return questions if questions else [{'number': 1, 'text': text, 'type': 'essay', 'marks': 1}]
    
    def _parse_answers(self, text: str, expected_questions: int) -> list:
        """Parse answers from student script"""
        answers = []
        
        # Look for answer patterns
        patterns = [
            r'[Aa]ns\.?\s*\d+[\.\)]?\s*:?\s*(.*?)(?=(?:[Aa]ns\.?\s*\d+|\Z))',
            r'[Qq]\d+[\.\)]?\s*(.*?)(?=(?:[Qq]\d+|\Z))',
            r'\b\d+[\.\)]\s*(.*?)(?=(?:\b\d+[\.\)]|\Z))'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                answers = [match.strip() for match in matches]
                break
        
        # If no patterns found, split by lines
        if not answers:
            answers = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Ensure we have expected number of answers
        if len(answers) > expected_questions:
            answers = answers[:expected_questions]
        elif len(answers) < expected_questions:
            answers.extend(['No answer provided'] * (expected_questions - len(answers)))
        
        return answers
    
    def _detect_question_type(self, text: str) -> str:
        """Detect if question is MCQ or essay/theory"""
        text_lower = text.lower()
        
        mcq_indicators = [
            r'\(a\)', r'\(b\)', r'\(c\)', r'\(d\)',
            r'[abcd]\)', r'multiple choice', r'mcq',
            r'option', r'choose'
        ]
        
        for indicator in mcq_indicators:
            if re.search(indicator, text_lower):
                return 'mcq'
        
        return 'essay'
    
    def _extract_marks(self, text: str) -> int:
        """Extract marks from question text"""
        marks_pattern = r'\((\d+)\s*[Mm]arks?\)|\[(\d+)\s*[Mm]\]|(\d+)\s*[Mm]arks'
        matches = re.search(marks_pattern, text)
        
        if matches:
            for group in matches.groups():
                if group:
                    return int(group)
        
        return 1  # Default marks