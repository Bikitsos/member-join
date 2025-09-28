from nicegui import ui
import re
import sqlite3
import os
from datetime import datetime

# Database path - can be overridden with environment variable
DB_PATH = os.getenv('DATABASE_PATH', 'members.db')


def is_valid_email(email: str) -> bool:
    """Validate email format using regex."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_valid_mobile(mobile: str) -> bool:
    """Validate mobile number - must be exactly 8 digits."""
    # Remove spaces, dashes, parentheses
    cleaned = re.sub(r'[\s\-\(\)]', '', mobile)
    # Check if it contains only digits and is exactly 8 digits long
    return cleaned.isdigit() and len(cleaned) == 8


def init_database():
    """Initialize the SQLite database and create the members table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            surname TEXT NOT NULL,
            mobile TEXT NOT NULL,
            email TEXT NOT NULL,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add unique constraints if they don't exist
    try:
        cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_members_email ON members(email)')
        cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_members_mobile ON members(mobile)')
    except sqlite3.Error as e:
        print(f"Note: Could not create unique indexes: {e}")
    
    conn.commit()
    conn.close()


def save_member_to_db(name: str, surname: str, mobile: str, email: str) -> bool:
    """Save member data to the database. Returns True on success, False on failure."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Clean the mobile number before saving
        cleaned_mobile = re.sub(r'[\s\-\(\)]', '', mobile)
        
        cursor.execute('''
            INSERT INTO members (name, surname, mobile, email, registration_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, surname, cleaned_mobile, email.lower(), datetime.now()))
        
        conn.commit()
        conn.close()
        return True
        
    except sqlite3.IntegrityError as e:
        # Handle duplicate constraints (email or mobile)
        error_msg = str(e).lower()
        if 'email' in error_msg:
            print(f"Database error: Duplicate email - {e}")
        elif 'mobile' in error_msg:
            print(f"Database error: Duplicate mobile - {e}")
        else:
            print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected database error: {e}")
        return False


def check_mobile_exists(mobile: str) -> bool:
    """Check if mobile number already exists in database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Clean the mobile number the same way we do in validation
        cleaned_mobile = re.sub(r'[\s\-\(\)]', '', mobile)
        
        cursor.execute('SELECT COUNT(*) FROM members WHERE mobile = ?', (cleaned_mobile,))
        count = cursor.fetchone()[0]
        
        conn.close()
        return count > 0
        
    except Exception as e:
        print(f"Error checking mobile number: {e}")
        return False


def check_email_exists(email: str) -> bool:
    """Check if email already exists in database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM members WHERE email = ?', (email.lower(),))
        count = cursor.fetchone()[0]
        
        conn.close()
        return count > 0
        
    except Exception as e:
        print(f"Error checking email: {e}")
        return False


def get_all_members():
    """Retrieve all members from the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, surname, mobile, email, registration_date 
            FROM members 
            ORDER BY registration_date DESC
        ''')
        
        members = cursor.fetchall()
        conn.close()
        return members
        
    except Exception as e:
        print(f"Error retrieving members: {e}")
        return []


def submit_form(name_input, surname_input, mobile_input, email_input, status_label):
    """Handle form submission with validation."""
    # Get values
    name = name_input.value.strip()
    surname = surname_input.value.strip()
    mobile = mobile_input.value.strip()
    email = email_input.value.strip()
    
    # Validation
    errors = []
    
    if not name:
        errors.append("Name is required")
    
    if not surname:
        errors.append("Surname is required")
    
    if not mobile:
        errors.append("Mobile number is required")
    elif not is_valid_mobile(mobile):
        errors.append("Invalid mobile number format")
    
    if not email:
        errors.append("Email is required")
    elif not is_valid_email(email):
        errors.append("Invalid email format")
    
    # Check for duplicates only if basic validation passes
    if not errors:
        if check_mobile_exists(mobile):
            errors.append("Mobile number is already registered")
        
        if check_email_exists(email):
            errors.append("Email is already registered")
    
    if errors:
        status_label.text = "❌ " + " • ".join(errors)
        status_label.style('color: red')
    else:
        # Save to database
        if save_member_to_db(name, surname, mobile, email):
            status_label.text = f"✅ Welcome {name} {surname}! Registration successful."
            status_label.style('color: green')
            
            # Clear form
            name_input.value = ""
            surname_input.value = ""
            mobile_input.value = ""
            email_input.value = ""
            
            print(f"New member registered: {name} {surname}, {email}, {mobile}")
        else:
            # Database save failed (should be rare now with pre-validation)
            status_label.text = "❌ Registration failed. Please try again."
            status_label.style('color: red')


def create_member_form():
    """Create the member registration form."""
    with ui.card().classes('w-full max-w-md mx-auto p-6'):
        ui.label('Member Registration').classes('text-2xl font-bold text-center mb-6')
        
        # Name input
        name_input = ui.input('Name *').classes('w-full mb-4').props('outlined')
        
        # Surname input  
        surname_input = ui.input('Surname *').classes('w-full mb-4').props('outlined')
        
        # Mobile input
        mobile_input = ui.input('Mobile Number *').classes('w-full mb-4').props('outlined')
        mobile_input.props('placeholder="12345678"')
        
        # Email input
        email_input = ui.input('Email *').classes('w-full mb-4').props('outlined')
        email_input.props('placeholder="your.email@example.com"')
        
        # Status label for validation messages
        status_label = ui.label('').classes('mb-4 min-h-6')
        
        # Submit button
        ui.button('Register Member', 
                 on_click=lambda: submit_form(name_input, surname_input, mobile_input, email_input, status_label)
                 ).classes('w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600')
        
        # Required fields note
        ui.label('* All fields are required').classes('text-sm text-gray-500 mt-4 text-center')


def main():
    """Main application entry point."""
    # Initialize database
    init_database()
    
    # Set page title and configure
    ui.page_title('Member Registration')
    
    # Add some styling
    ui.add_head_html('''
        <style>
            body { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 2rem;
            }
        </style>
    ''')
    
    # Create header
    with ui.row().classes('w-full justify-center mb-8'):
        ui.label('🏢 Member Registration Portal').classes('text-4xl font-bold text-white text-center')
    
    # Create the form
    create_member_form()
    
    # Add footer
    with ui.row().classes('w-full justify-center mt-8'):
        ui.label('Complete all required fields to join our membership').classes('text-white text-center opacity-80')
    
    # Run the app
    # Use host='0.0.0.0' for container deployment, show=False for production
    host = os.getenv('HOST', 'localhost')
    show_browser = os.getenv('SHOW_BROWSER', 'true').lower() == 'true'
    ui.run(title='Member Registration', port=8085, host=host, show=show_browser)


if __name__ in {"__main__", "__mp_main__"}:
    main()
