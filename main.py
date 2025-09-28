from nicegui import ui
import re
import sqlite3
import os
import requests
from datetime import datetime

# Database path - can be overridden with environment variable
DB_PATH = os.getenv('DATABASE_PATH', 'members.db')

# Mailgun configuration - set these environment variables
MAILGUN_DOMAIN = os.getenv('MAILGUN_DOMAIN')
MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY')
FROM_EMAIL = os.getenv('FROM_EMAIL', f'noreply@{MAILGUN_DOMAIN}' if MAILGUN_DOMAIN else 'noreply@example.com')
MAILGUN_BASE_URL = f'https://api.mailgun.net/v3/{MAILGUN_DOMAIN}'


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


def send_confirmation_email(name: str, surname: str, email: str, mobile: str) -> bool:
    """Send confirmation email using Mailgun API."""
    
    # Skip email sending if Mailgun is not configured
    if not MAILGUN_DOMAIN or not MAILGUN_API_KEY:
        print("Mailgun not configured - skipping email")
        return True  # Return True to not block registration
    
    try:
        # Email content
        subject = "Welcome! Registration Confirmed"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=true">
            <title>Registration Confirmation</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; color: white; text-align: center; margin-bottom: 30px;">
                <h1 style="margin: 0; font-size: 28px;">🎉 Welcome to Our Community!</h1>
                <p style="margin: 10px 0 0 0; font-size: 18px; opacity: 0.9;">Registration Successful</p>
            </div>
            
            <div style="padding: 20px; background: #f8f9fa; border-radius: 8px; margin-bottom: 20px;">
                <h2 style="color: #333; margin-top: 0;">Hello {name} {surname}!</h2>
                <p style="font-size: 16px;">Thank you for registering with us. Your membership has been confirmed successfully.</p>
                
                <div style="background: white; padding: 15px; border-radius: 5px; border-left: 4px solid #667eea; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #667eea;">Your Registration Details:</h3>
                    <p style="margin: 5px 0;"><strong>Name:</strong> {name} {surname}</p>
                    <p style="margin: 5px 0;"><strong>Email:</strong> {email}</p>
                    <p style="margin: 5px 0;"><strong>Mobile:</strong> {mobile}</p>
                    <p style="margin: 5px 0;"><strong>Registration Date:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
                
                <p style="color: #666; font-size: 14px; border-top: 1px solid #ddd; padding-top: 15px; margin-top: 20px;">
                    If you have any questions or need assistance, please don't hesitate to contact us.
                </p>
            </div>
            
            <div style="text-align: center; color: #888; font-size: 12px;">
                <p>This is an automated confirmation email. Please do not reply to this message.</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to Our Community!
        
        Hello {name} {surname}!
        
        Thank you for registering with us. Your membership has been confirmed successfully.
        
        Registration Details:
        - Name: {name} {surname}
        - Email: {email}
        - Mobile: {mobile}
        - Registration Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        
        If you have any questions or need assistance, please contact us.
        
        This is an automated confirmation email.
        """
        
        # Mailgun API request
        response = requests.post(
            f"{MAILGUN_BASE_URL}/messages",
            auth=("api", MAILGUN_API_KEY),
            data={
                "from": f"Member Registration <{FROM_EMAIL}>",
                "to": [email],
                "subject": subject,
                "text": text_content,
                "html": html_content
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"Confirmation email sent successfully to {email}")
            return True
        else:
            print(f"Failed to send email to {email}. Status: {response.status_code}, Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Email sending failed due to network error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error sending email: {e}")
        return False


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
            # Send confirmation email
            email_sent = send_confirmation_email(name, surname, email, mobile)
            
            if email_sent:
                status_label.text = f"✅ Welcome {name} {surname}! Registration successful. Confirmation email sent."
            else:
                status_label.text = f"✅ Welcome {name} {surname}! Registration successful. (Email delivery failed)"
            
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
