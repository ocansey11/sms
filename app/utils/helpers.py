import re
from typing import Optional, Dict, Any, List
from datetime import datetime, date, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import secrets
import string
import hashlib
import structlog

logger = structlog.get_logger()

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    # Check if it's a valid length (10-15 digits)
    return len(digits) >= 10 and len(digits) <= 15

def validate_password_strength(password: str) -> Dict[str, Any]:
    """Validate password strength"""
    issues = []
    score = 0
    
    if len(password) < 8:
        issues.append("Password must be at least 8 characters long")
    else:
        score += 1
    
    if not re.search(r'[A-Z]', password):
        issues.append("Password must contain at least one uppercase letter")
    else:
        score += 1
    
    if not re.search(r'[a-z]', password):
        issues.append("Password must contain at least one lowercase letter")
    else:
        score += 1
    
    if not re.search(r'\d', password):
        issues.append("Password must contain at least one number")
    else:
        score += 1
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        issues.append("Password must contain at least one special character")
    else:
        score += 1
    
    strength_levels = {
        0: "Very Weak",
        1: "Weak",
        2: "Fair",
        3: "Good",
        4: "Strong",
        5: "Very Strong"
    }
    
    return {
        "is_valid": len(issues) == 0,
        "score": score,
        "strength": strength_levels[score],
        "issues": issues
    }

def generate_random_password(length: int = 12) -> str:
    """Generate a random password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_verification_code(length: int = 6) -> str:
    """Generate a numeric verification code"""
    return ''.join(secrets.choice(string.digits) for _ in range(length))

def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)

def hash_string(text: str) -> str:
    """Hash a string using SHA-256"""
    return hashlib.sha256(text.encode()).hexdigest()

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove or replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:255-len(ext)-1] + '.' + ext if ext else name[:255]
    
    return filename

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def calculate_age(birth_date: date) -> int:
    """Calculate age from birth date"""
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def get_academic_year(date_obj: date = None) -> str:
    """Get academic year for a given date"""
    if not date_obj:
        date_obj = date.today()
    
    # Academic year typically starts in September
    if date_obj.month >= 9:
        return f"{date_obj.year}-{date_obj.year + 1}"
    else:
        return f"{date_obj.year - 1}-{date_obj.year}"

def get_week_dates(date_obj: date = None) -> tuple:
    """Get start and end dates of the week for a given date"""
    if not date_obj:
        date_obj = date.today()
    
    # Get Monday of the week
    monday = date_obj - timedelta(days=date_obj.weekday())
    # Get Sunday of the week
    sunday = monday + timedelta(days=6)
    
    return monday, sunday

def get_month_dates(date_obj: date = None) -> tuple:
    """Get start and end dates of the month for a given date"""
    if not date_obj:
        date_obj = date.today()
    
    # First day of the month
    first_day = date_obj.replace(day=1)
    
    # Last day of the month
    if date_obj.month == 12:
        last_day = date_obj.replace(year=date_obj.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        last_day = date_obj.replace(month=date_obj.month + 1, day=1) - timedelta(days=1)
    
    return first_day, last_day

def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime object to string"""
    return dt.strftime(format_str)

def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Parse datetime string to datetime object"""
    return datetime.strptime(date_str, format_str)

def is_business_day(date_obj: date) -> bool:
    """Check if a date is a business day (Monday-Friday)"""
    return date_obj.weekday() < 5

def get_business_days_count(start_date: date, end_date: date) -> int:
    """Count business days between two dates"""
    count = 0
    current_date = start_date
    
    while current_date <= end_date:
        if is_business_day(current_date):
            count += 1
        current_date += timedelta(days=1)
    
    return count

def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate string to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace and non-printable characters"""
    # Remove non-printable characters
    cleaned = re.sub(r'[^\x20-\x7E]', '', text)
    # Remove extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def mask_email(email: str) -> str:
    """Mask email address for privacy"""
    if not validate_email(email):
        return email
    
    local, domain = email.split('@')
    
    if len(local) <= 2:
        masked_local = local
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"

def mask_phone(phone: str) -> str:
    """Mask phone number for privacy"""
    digits = re.sub(r'\D', '', phone)
    if len(digits) < 4:
        return phone
    
    return phone.replace(digits[:-4], '*' * len(digits[:-4]))

def calculate_percentage(part: float, whole: float) -> float:
    """Calculate percentage"""
    if whole == 0:
        return 0
    return round((part / whole) * 100, 2)

def calculate_grade(score: float, max_score: float) -> str:
    """Calculate letter grade based on score"""
    if max_score == 0:
        return "N/A"
    
    percentage = (score / max_score) * 100
    
    if percentage >= 90:
        return "A"
    elif percentage >= 80:
        return "B"
    elif percentage >= 70:
        return "C"
    elif percentage >= 60:
        return "D"
    else:
        return "F"

def get_grade_color(grade: str) -> str:
    """Get color code for grade"""
    grade_colors = {
        "A": "#4CAF50",  # Green
        "B": "#8BC34A",  # Light Green
        "C": "#FFC107",  # Yellow
        "D": "#FF9800",  # Orange
        "F": "#F44336",  # Red
        "N/A": "#9E9E9E"  # Grey
    }
    return grade_colors.get(grade, "#9E9E9E")

def paginate_results(items: List[Any], page: int, per_page: int) -> Dict[str, Any]:
    """Paginate a list of items"""
    start = (page - 1) * per_page
    end = start + per_page
    
    paginated_items = items[start:end]
    
    return {
        "items": paginated_items,
        "page": page,
        "per_page": per_page,
        "total": len(items),
        "pages": (len(items) + per_page - 1) // per_page,
        "has_next": end < len(items),
        "has_prev": start > 0
    }
