import pandas as pd
from datetime import datetime
import sqlite3
import os

DB_FILE = "leavedatabase.db"

def get_db_connection():
    """Returns a new or existing database connection."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
    return conn

def init_db():
    """Initializes the SQLite database and creates necessary tables."""
    conn = get_db_connection()
    if conn is None:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Create the users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                name TEXT,
                department TEXT,
                phone TEXT,
                reg_no TEXT
            )
        """)
        
        # Create the leave requests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leave_requests (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                leave_type TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                reason TEXT,
                status TEXT NOT NULL,
                department TEXT NOT NULL,
                FOREIGN KEY (username) REFERENCES users(username)
            )
        """)
        
        # Create the email configuration table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_config (
                id INTEGER PRIMARY KEY,
                sender_email TEXT NOT NULL,
                app_password TEXT NOT NULL
            )
        """)

        # Create the departments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                Deptname TEXT PRIMARY KEY
            )
        """)

        # Check if default departments exist, and if not, add them
        cursor.execute("SELECT COUNT(*) FROM departments")
        if cursor.fetchone()[0] == 0:
            default_departments = [('MCA',), ('MBA',), ('CSE',), ('ECE',), ('IT',)]
            cursor.executemany("INSERT INTO departments (Deptname) VALUES (?)", default_departments)

        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_departments():
    """Fetches all departments from the database."""
    conn = get_db_connection()
    if conn is None:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Deptname FROM departments ORDER BY Deptname")
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Error fetching departments: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_user(username, password, role):
    """Retrieves a user based on username, password, and role."""
    conn = get_db_connection()
    if conn is None:
        return None
        
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ? AND role = ?", (username, password, role))
        user_data = cursor.fetchone()
        return dict(user_data) if user_data else None
    except sqlite3.Error as e:
        print(f"Error retrieving user: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_user_by_email(email):
    """Retrieves a user based on their email."""
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user_data = cursor.fetchone()
        return dict(user_data) if user_data else None
    except sqlite3.Error as e:
        print(f"Error retrieving user by email: {e}")
        return None
    finally:
        if conn:
            conn.close()

def register_student(name, email, username, password, department, phone):
    """Registers a new student user."""
    conn = get_db_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, username, password, role, department, phone) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, email, username, password, "Student", department, phone)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error registering student: {e}")
        return False
    finally:
        if conn:
            conn.close()

def register_staff(name, email, username, password, department, phone):
    """Registers a new staff user."""
    conn = get_db_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, username, password, role, department, phone) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, email, username, password, "Staff", department, phone)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error registering staff: {e}")
        return False
    finally:
        if conn:
            conn.close()

def register_hod(name, email, username, password, department, phone):
    """Registers a new HOD user."""
    conn = get_db_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, username, password, role, department, phone) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, email, username, password, "HOD", department, phone)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error registering HOD: {e}")
        return False
    finally:
        if conn:
            conn.close()
            
def apply_for_leave(username, role, email, leave_type, start_date, end_date, reason):
    """Submits a new leave application."""
    conn = get_db_connection()
    if conn is None:
        return False
        
    try:
        cursor = conn.cursor()
        # Get the user's department
        cursor.execute("SELECT department FROM users WHERE username = ?", (username,))
        department = cursor.fetchone()[0]

        cursor.execute(
            "INSERT INTO leave_requests (username, email, leave_type, start_date, end_date, reason, status, department) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (username, email, leave_type, start_date, end_date, reason, "Pending", department)
        )
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error applying for leave: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_my_leave_requests(username):
    """Retrieves all leave requests for a specific user."""
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        query = "SELECT id, leave_type, start_date, end_date, reason, status FROM leave_requests WHERE username = ?"
        df = pd.read_sql(query, conn, params=(username,))
        return df
    except sqlite3.Error as e:
        print(f"Error fetching my leave requests: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

def get_leave_requests(department, status):
    """
    Fetches leave requests for a specific department and status,
    including user details by joining the users table.
    """
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    
    try:
        if status == "Pending":
            query = """
                SELECT lr.*, u.name, u.role
                FROM leave_requests lr
                JOIN users u ON lr.username = u.username
                WHERE lr.department = ? AND lr.status = ?
            """
            df = pd.read_sql(query, conn, params=(department, "Pending"))
        else: # "Previous" (approved or rejected)
            query = """
                SELECT lr.*, u.name, u.role
                FROM leave_requests lr
                JOIN users u ON lr.username = u.username
                WHERE lr.department = ? AND lr.status != ?
            """
            df = pd.read_sql(query, conn, params=(department, "Pending"))
        return df
    except sqlite3.Error as e:
        print(f"Error fetching leave requests: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()
            
def get_hod_email_by_department(department):
    """Retrieves the email of the HOD for a specific department."""
    conn = get_db_connection()
    if conn is None:
        return None
        
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE department = ? AND role = 'HOD'", (department,))
        result = cursor.fetchone()
        return result[0] if result else None
    except sqlite3.Error as e:
        print(f"Error fetching HOD email: {e}")
        return None
    finally:
        if conn:
            conn.close()

def update_leave_status(leave_id, status):
    """Updates the status of a leave request."""
    conn = get_db_connection()
    if conn is None:
        return False
        
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE leave_requests SET status=? WHERE id=?", (status, leave_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error updating leave status: {e}")
        return False
    finally:
        if conn:
            conn.close()

def update_email_credentials(sender_email, app_password):
    """Saves email credentials in the SQLite database."""
    conn = get_db_connection()
    if conn is None:
        return False
        
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM email_config")
        cursor.execute("INSERT INTO email_config (id, sender_email, app_password) VALUES (?, ?, ?)", (1, sender_email, app_password))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error updating email credentials: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_email_credentials():
    """Retrieves email credentials from the SQLite database."""
    conn = get_db_connection()
    if conn is None:
        return None
        
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT sender_email, app_password FROM email_config WHERE id=1")
        result = cursor.fetchone()
        return {'sender_email': result[0], 'app_password': result[1]} if result else None
    except sqlite3.Error as e:
        print(f"Error fetching email credentials: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_total_leaves_by_role(department):
    """Returns total approved leaves taken by students and staff in a department."""
    conn = get_db_connection()
    totals = {"Student": 0, "Staff": 0}
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.role, COUNT(*) as total
                FROM leave_requests lr
                JOIN users u ON lr.username = u.username
                WHERE lr.department = ? AND lr.status = 'Approved'
                GROUP BY u.role
            """, (department,))
            for row in cursor.fetchall():
                totals[row["role"]] = row["total"]
        except Exception as e:
            print("Error fetching total leaves:", e)
        finally:
            conn.close()
    return totals


def get_leave_summary_by_name(department):
    """Returns approved leave counts by username for students and staff."""
    conn = get_db_connection()
    summary = {"Student": {}, "Staff": {}}
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.username, u.role, COUNT(*) 
            FROM leave_requests lr
            JOIN users u ON lr.username = u.username
            WHERE lr.status='Approved' AND lr.department=? 
            GROUP BY u.username, u.role
        """, (department,))
        rows = cursor.fetchall()
        for username, role, count in rows:
            if role in summary:
                summary[role][username] = count
        conn.close()
    return summary
