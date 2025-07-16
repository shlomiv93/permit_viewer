from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from datetime import datetime, timedelta
import json
from functools import lru_cache
import calendar

app = Flask(__name__)

# הגדרת מסד הנתונים
DATABASE_PATH = os.environ.get('DATABASE_URL', 'licensing_system.db')

def get_db_connection():
    """יצירת חיבור למסד הנתונים"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """יצירת מסד הנתונים אם לא קיים"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                request_number TEXT NOT NULL,
                info_file_number TEXT NOT NULL,
                date TEXT NOT NULL,
                opening_date TEXT,
                status_date TEXT,
                committee_date TEXT,
                permit_validity_date TEXT,
                team_leader TEXT NOT NULL,
                engineer TEXT NOT NULL,
                stage TEXT NOT NULL,
                request_types TEXT,
                management_company TEXT,
                entrepreneur_name TEXT,
                architect TEXT,
                city TEXT,
                notes TEXT,
                city_team TEXT,
                info_date_extension INTEGER DEFAULT 0,
                opening_date_extension INTEGER DEFAULT 0,
                status_date_extension INTEGER DEFAULT 0,
                committee_date_extension INTEGER DEFAULT 0,
                permit_validity_date_extension INTEGER DEFAULT 0
            )
        """)
        
        # Check if table is empty and add sample data
        cursor.execute("SELECT COUNT(*) FROM projects")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("Database is empty. Adding sample data...")
            add_sample_data(cursor)
            print("Sample data added successfully!")
        else:
            print(f"Database already contains {count} projects.")
        
        conn.commit()
        conn.close()
        print("Database initialized successfully")
        
    except Exception as e:
        print(f"Database initialization error: {e}")
        # Try to create an empty database at least
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_name TEXT NOT NULL,
                    request_number TEXT NOT NULL,
                    info_file_number TEXT NOT NULL,
                    date TEXT NOT NULL,
                    opening_date TEXT,
                    status_date TEXT,
                    committee_date TEXT,
                    permit_validity_date TEXT,
                    team_leader TEXT NOT NULL,
                    engineer TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    request_types TEXT,
                    management_company TEXT,
                    entrepreneur_name TEXT,
                    architect TEXT,
                    city TEXT,
                    notes TEXT,
                    city_team TEXT,
                    info_date_extension INTEGER DEFAULT 0,
                    opening_date_extension INTEGER DEFAULT 0,
                    status_date_extension INTEGER DEFAULT 0,
                    committee_date_extension INTEGER DEFAULT 0,
                    permit_validity_date_extension INTEGER DEFAULT 0
                )
            """)
            conn.commit()
            conn.close()
            print("Empty database created successfully")
        except Exception as e2:
            print(f"Failed to create empty database: {e2}")

def add_sample_data(cursor):
    """הוספת נתונים לדוגמה"""
    sample_projects = [
        ('פרויקט מגורים רמת גן', 'RG-2024-001', 'TIK-001-2024', '2024-01-15', '2024-02-01', 
         '2024-02-15', '2024-03-01', '2024-04-01', 'דוד כהן', 'שרה לוי', 'הליך פתיחה', 
         'בנייה חדשה', 'חברת ניהול אלפא', 'משה ישראלי', 'רחל אדריכלית', 'רמת גן', 
         'פרויקט דוגמה ראשון', 'מרכז'),
        ('מתחם מסחרי תל אביב', 'TA-2024-002', 'TIK-002-2024', '2024-01-20', '2024-02-10', 
         '2024-02-25', '2024-03-15', '2024-04-15', 'מיכאל גולן', 'יוסי מהנדס', 'נפתח לפני החלטת ועדה', 
         'היתר בניה', 'חברת ניהול בטא', 'אברהם יזם', 'דני אדריכל', 'תל אביב', 
         'פרויקט מסחרי גדול במרכז העיר', 'דרום'),
        ('שיפוץ בית ספר חיפה', 'HF-2024-003', 'TIK-003-2024', '2024-02-01', '2024-02-20', 
         '2024-03-05', '2024-03-25', '2024-05-01', 'רות מנהלת', 'עמי טכנאי', 'בדיקה סופית', 
         'שינויים במהלך הביצוע (סמכות מה"ע)', 'חברת ניהול גמא', 'עיריית חיפה', 
         'נועה מתכננת', 'חיפה', 'שיפוץ כיתות לימוד ומעבדות', 'צפון'),
        ('פארק ציבורי באר שבע', 'BS-2024-004', 'TIK-004-2024', '2024-02-10', '2024-03-01', 
         '2024-03-15', '2024-04-01', '2024-05-15', 'אלי ראש צוות', 'נירה מהנדסת', 'נמסר היתר', 
         'היתר שינויים', 'חברת ניהול דלתא', 'קרן קיימת לישראל', 'גיל נופי', 'באר שבע', 
         'פארק עירוני חדש עם מתקני ספורט', 'מזרח'),
        ('מגדל משרדים נתניה', 'NT-2024-005', 'TIK-005-2024', '2024-02-15', '2024-03-10', 
         '2024-03-25', '2024-04-10', '2024-06-01', 'דוד כהן', 'מאיה בודקת', 'בדיקה מרחבית אחרי ועדה', 
         'תמא 38', 'חברת ניהול הה', 'חברת בנייה גדולה', 'יעקב מעצב', 'נתניה', 
         'מגדל 25 קומות במרכז העיר', 'פרויקטים מיוחדים')
    ]
    
    for project in sample_projects:
        cursor.execute("""
            INSERT INTO projects (
                project_name, request_number, info_file_number, date, opening_date,
                status_date, committee_date, permit_validity_date, team_leader,
                engineer, stage, request_types, management_company, entrepreneur_name,
                architect, city, notes, city_team
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, project)
    
    print(f"Added {len(sample_projects)} sample projects to the database.")

# שלבי הרישוי
LICENSING_STAGES = [
    "הכל",
    "הליך פתיחה", 
    "נפתח לפני החלטת ועדה",
    "בדיקה מרחבית אחרי ועדה",
    "בדיקת תכן",
    "בדיקה סופית",
    "אגרות והשבחה",
    "נמסר היתר"
]

# צוותי עירייה
CITY_TEAMS = ["מרכז", "דרום", "צפון", "מזרח", "פרויקטים מיוחדים", "צוות מיוחד", "אחר"]

@lru_cache(maxsize=1000)
def calculate_business_days(start_date_str, business_days_to_add):
    """חישוב ימי עסקים פשוט"""
    try:
        if not start_date_str:
            return ""
        
        if '\n' in start_date_str:
            start_date_str = start_date_str.split('\n')[0]
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        current_date = start_date
        days_added = 0
        
        while days_added < business_days_to_add:
            current_date += timedelta(days=1)
            # ימי עבודה: ראשון-חמישי (0-4)
            if current_date.weekday() < 5:
                days_added += 1
        
        return current_date.strftime('%Y-%m-%d')
    except:
        return ""

def format_date_with_extension(original_date_str, extension_value, field_type):
    """עיצוב תאריך עם הארכה"""
    if not original_date_str:
        return ""
    
    try:
        original_date = datetime.strptime(original_date_str, '%Y-%m-%d')
        
        # תאריך יעד ספציפי
        if extension_value < -100000000:
            date_number = abs(extension_value + 100000000)
            year = date_number // 10000
            month = (date_number % 10000) // 100
            day = date_number % 100
            try:
                target_date = datetime(year, month, day)
                return f"{original_date_str}<br>(תאריך יעד: {target_date.strftime('%Y-%m-%d')})"
            except ValueError:
                pass
        
        # 90 ימי עסקים מיוחד
        elif extension_value == -90:
            if field_type == 'opening':
                target_date_str = calculate_business_days(original_date_str, 90)
                return f"{original_date_str}<br>(90 ימי עסקים: {target_date_str})"
            else:
                base_date = calculate_base_date_by_type(original_date, field_type)
                target_date_str = calculate_business_days(base_date.strftime('%Y-%m-%d'), 90)
                return f"{original_date_str}<br>({get_base_description(field_type)} + 90 ימי עסקים: {target_date_str})"
        
        # ימי עסקים רגילים
        elif extension_value < -1000:
            business_days = abs(extension_value) - 1000
            base_date = calculate_base_date_by_type(original_date, field_type)
            target_date_str = calculate_business_days(base_date.strftime('%Y-%m-%d'), business_days)
            return f"{original_date_str}<br>({get_base_description(field_type)} + {business_days} ימי עסקים: {target_date_str})"
        
        # הארכה רגילה בימים
        elif extension_value > 0:
            base_date = calculate_base_date_by_type(original_date, field_type)
            final_target = original_date + timedelta(days=extension_value)
            base_days = (base_date - original_date).days
            extension_days = extension_value - base_days
            
            if extension_days > 0:
                return f"{original_date_str}<br>({get_base_description(field_type)} + {extension_days} ימים: {final_target.strftime('%Y-%m-%d')})"
            else:
                return f"{original_date_str}<br>({get_base_description(field_type)}: {final_target.strftime('%Y-%m-%d')})"
        
        # אין הארכה
        else:
            return format_base_date_by_type(original_date_str, field_type)
    
    except Exception as e:
        return original_date_str

def calculate_base_date_by_type(original_date, field_type):
    """חישוב תאריך בסיסי לפי סוג השדה"""
    if field_type == 'opening':
        business_target = calculate_business_days(original_date.strftime('%Y-%m-%d'), 45)
        return datetime.strptime(business_target, '%Y-%m-%d') if business_target else original_date + timedelta(days=180)
    elif field_type in ['info', 'committee']:
        return original_date + timedelta(days=730)
    elif field_type == 'permit':
        return original_date + timedelta(days=1095)
    else:
        return original_date + timedelta(days=180)

def format_base_date_by_type(original_date_str, field_type):
    """עיצוב תאריך בסיסי ללא הארכה"""
    if not original_date_str:
        return ""
    
    try:
        original_date = datetime.strptime(original_date_str, '%Y-%m-%d')
        base_date = calculate_base_date_by_type(original_date, field_type)
        
        if field_type == 'opening':
            business_target = calculate_business_days(original_date_str, 45)
            return f"{original_date_str}<br>(45 ימי עסקים: {business_target})"
        elif field_type in ['info', 'committee']:
            return f"{original_date_str}<br>(2 שנים: {base_date.strftime('%Y-%m-%d')})"
        elif field_type == 'permit':
            return f"{original_date_str}<br>(3 שנים: {base_date.strftime('%Y-%m-%d')})"
        else:
            return original_date_str
    except:
        return original_date_str

def get_base_description(field_type):
    """קבלת תיאור הבסיס לפי סוג השדה"""
    if field_type == 'opening':
        return "45 ימי עסקים"
    elif field_type in ['info', 'committee']:
        return "2 שנים"
    elif field_type == 'permit':
        return "3 שנים"
    else:
        return "בסיס"

def check_date_expired_with_extensions(date_str):
    """בדיקה אם תאריך פג תוקף כולל הארכות"""
    try:
        if not date_str:
            return False
        
        current_date = datetime.now()
        
        # בדיקה אם יש הארכה
        if '<br>' in date_str and ':' in date_str:
            lines = date_str.split('<br>')
            if len(lines) >= 2:
                import re
                date_match = re.search(r':\s*(\d{4}-\d{2}-\d{2})', lines[1])
                if date_match:
                    target_date_str = date_match.group(1)
                    target_date = datetime.strptime(target_date_str, '%Y-%m-%d')
                    return current_date.date() > target_date.date()
        
        # אין הארכה - בדוק התאריך המקורי
        date_part = date_str.split('<br>')[0] if '<br>' in date_str else date_str
        if len(date_part) < 8:
            return False
        
        record_date = datetime.strptime(date_part, '%Y-%m-%d')
        target_date = calculate_business_days(date_part, 45)
        if target_date:
            target_date_obj = datetime.strptime(target_date, '%Y-%m-%d')
            return current_date.date() > target_date_obj.date()
        
        return False
    except:
        return False

def check_date_approaching_expiry_with_extensions(date_str, days_before=15):
    """בדיקה אם תאריך מתקרב לפקיעה"""
    try:
        if not date_str:
            return False
        
        current_date = datetime.now()
        
        # בדיקה אם יש הארכה
        if '<br>' in date_str and ':' in date_str:
            lines = date_str.split('<br>')
            if len(lines) >= 2:
                import re
                date_match = re.search(r':\s*(\d{4}-\d{2}-\d{2})', lines[1])
                if date_match:
                    target_date_str = date_match.group(1)
                    target_date = datetime.strptime(target_date_str, '%Y-%m-%d')
                    
                    if target_date.date() <= current_date.date():
                        return False
                    
                    days_remaining = (target_date.date() - current_date.date()).days
                    return 0 < days_remaining <= days_before
        
        # אין הארכה
        date_part = date_str.split('<br>')[0] if '<br>' in date_str else date_str
        if len(date_part) < 8:
            return False
        
        record_date = datetime.strptime(date_part, '%Y-%m-%d')
        target_date = calculate_business_days(date_part, 45)
        if target_date:
            target_date_obj = datetime.strptime(target_date, '%Y-%m-%d')
            days_remaining = (target_date_obj.date() - current_date.date()).days
            return 0 < days_remaining <= days_before
        
        return False
    except:
        return False

def check_permit_expired_with_extensions(date_str):
    """בדיקה אם תוקף היתר פג"""
    try:
        if not date_str:
            return False
        
        current_date = datetime.now()
        
        # בדיקה אם יש הארכה
        if '<br>' in date_str and ':' in date_str:
            lines = date_str.split('<br>')
            if len(lines) >= 2:
                import re
                date_match = re.search(r':\s*(\d{4}-\d{2}-\d{2})', lines[1])
                if date_match:
                    target_date_str = date_match.group(1)
                    target_date = datetime.strptime(target_date_str, '%Y-%m-%d')
                    return current_date.date() > target_date.date()
        
        # אין הארכה
        date_part = date_str.split('<br>')[0] if '<br>' in date_str else date_str
        if len(date_part) < 8:
            return False
        
        permit_date = datetime.strptime(date_part, '%Y-%m-%d')
        expiry_date = permit_date + timedelta(days=365)
        return current_date.date() > expiry_date.date()
    except:
        return False

def check_info_date_expiring(date_str):
    """בדיקה אם תיק מידע מתקרב לפקיעה"""
    try:
        if not date_str:
            return False
        
        current_date = datetime.now()
        
        # בדיקה אם יש הארכה
        if '<br>' in date_str and ':' in date_str:
            lines = date_str.split('<br>')
            if len(lines) >= 2:
                import re
                date_match = re.search(r':\s*(\d{4}-\d{2}-\d{2})', lines[1])
                if date_match:
                    target_date_str = date_match.group(1)
                    target_date = datetime.strptime(target_date_str, '%Y-%m-%d')
                    days_remaining = (target_date - current_date).days
                    return days_remaining <= 120
        
        # אין הארכה
        date_part = date_str.split('<br>')[0] if '<br>' in date_str else date_str
        if len(date_part) < 8:
            return False
        
        record_date = datetime.strptime(date_part, '%Y-%m-%d')
        expiry_date = record_date + timedelta(days=730)
        days_remaining = (expiry_date - current_date).days
        return days_remaining <= 120
    except:
        return False

def check_committee_date_expiring(date_str):
    """בדיקה אם תאריך ועדה מתקרב לפקיעה"""
    try:
        if not date_str:
            return False
        
        current_date = datetime.now()
        
        # בדיקה אם יש הארכה
        if '<br>' in date_str and ':' in date_str:
            lines = date_str.split('<br>')
            if len(lines) >= 2:
                import re
                date_match = re.search(r':\s*(\d{4}-\d{2}-\d{2})', lines[1])
                if date_match:
                    target_date_str = date_match.group(1)
                    target_date = datetime.strptime(target_date_str, '%Y-%m-%d')
                    days_remaining = (target_date - current_date).days
                    return 0 < days_remaining <= 180
        
        # אין הארכה
        date_part = date_str.split('<br>')[0] if '<br>' in date_str else date_str
        if len(date_part) < 8:
            return False
        
        committee_date = datetime.strptime(date_part, '%Y-%m-%d')
        expiry_date = committee_date + timedelta(days=730)
        days_remaining = (expiry_date - current_date).days
        return 0 < days_remaining <= 180
    except:
        return False

def get_row_color_class(record):
    """קביעת מחלקת CSS לצביעת השורה"""
    stage = record.get('stage', '')
    
    # עיצוב התאריכים
    opening_date_text = ""
    if record.get('opening_date'):
        opening_date_text = format_date_with_extension(
            record['opening_date'], 
            record.get('opening_date_extension', 0), 
            'opening'
        )
    
    committee_date_text = ""
    if record.get('committee_date'):
        committee_date_text = format_date_with_extension(
            record['committee_date'], 
            record.get('committee_date_extension', 0), 
            'committee'
        )
    
    permit_date_text = ""
    if record.get('permit_validity_date'):
        permit_date_text = format_date_with_extension(
            record['permit_validity_date'], 
            record.get('permit_validity_date_extension', 0), 
            'permit'
        )
    
    info_date_text = ""
    if record.get('date'):
        info_date_text = format_date_with_extension(
            record['date'], 
            record.get('info_date_extension', 0), 
            'info'
        )
    
    # צביעה לפי עדיפות
    if stage == "נפתח לפני החלטת ועדה":
        if opening_date_text and (check_date_approaching_expiry_with_extensions(opening_date_text, 15) or
                                  check_date_expired_with_extensions(opening_date_text)):
            return "approaching"
    
    if permit_date_text and check_permit_expired_with_extensions(permit_date_text):
        return "warning"
    
    if opening_date_text and check_date_approaching_expiry_with_extensions(opening_date_text, 15):
        return "approaching"
    
    if committee_date_text and check_committee_date_expiring(committee_date_text):
        return "committee_expiring"
    
    if info_date_text and check_info_date_expiring(info_date_text):
        return "info_expiring"
    
    return ""

@app.route('/')
def index():
    """עמוד הבית - הצגת כל הפרויקטים"""
    conn = get_db_connection()
    
    # קבלת פרמטרי חיפוש ומיון
    search = request.args.get('search', '')
    stage_filter = request.args.get('stage', 'הכל')
    sort_by = request.args.get('sort', 'project_name')
    
    # בניית שאילתה
    query = """
        SELECT 
            id, project_name, request_number, info_file_number,
            date, opening_date, status_date, committee_date, permit_validity_date,
            team_leader, stage, request_types, engineer, management_company,
            entrepreneur_name, architect, city, notes,
            info_date_extension, opening_date_extension, status_date_extension,
            committee_date_extension, permit_validity_date_extension, city_team
        FROM projects
        WHERE 1=1
    """
    
    params = []
    
    # סינון לפי שלב
    if stage_filter != 'הכל':
        query += " AND stage = ?"
        params.append(stage_filter)
    
    # חיפוש
    if search:
        query += """ AND (
            LOWER(project_name) LIKE ? OR 
            LOWER(request_number) LIKE ? OR
            LOWER(info_file_number) LIKE ? OR
            LOWER(city) LIKE ? OR
            LOWER(engineer) LIKE ? OR
            LOWER(team_leader) LIKE ? OR
            LOWER(entrepreneur_name) LIKE ? OR
            LOWER(architect) LIKE ? OR
            LOWER(notes) LIKE ?
        )"""
        search_param = f'%{search.lower()}%'
        params.extend([search_param] * 9)
    
    # מיון
    if sort_by in ['project_name', 'request_number', 'date', 'opening_date', 'stage', 'engineer', 'team_leader']:
        query += f" ORDER BY {sort_by}"
    else:
        query += " ORDER BY project_name"
    
    projects = conn.execute(query, params).fetchall()
    
    # עיצוב התאריכים ועדכון צבעים
    formatted_projects = []
    for project in projects:
        project_dict = dict(project)
        
        # עיצוב התאריכים
        if project_dict.get('date'):
            project_dict['formatted_info_date'] = format_date_with_extension(
                project_dict['date'], 
                project_dict.get('info_date_extension', 0), 
                'info'
            )
        
        if project_dict.get('opening_date'):
            project_dict['formatted_opening_date'] = format_date_with_extension(
                project_dict['opening_date'], 
                project_dict.get('opening_date_extension', 0), 
                'opening'
            )
        
        if project_dict.get('committee_date'):
            project_dict['formatted_committee_date'] = format_date_with_extension(
                project_dict['committee_date'], 
                project_dict.get('committee_date_extension', 0), 
                'committee'
            )
        
        if project_dict.get('permit_validity_date'):
            project_dict['formatted_permit_date'] = format_date_with_extension(
                project_dict['permit_validity_date'], 
                project_dict.get('permit_validity_date_extension', 0), 
                'permit'
            )
        
        # קביעת צבע השורה
        project_dict['row_color'] = get_row_color_class(project_dict)
        
        formatted_projects.append(project_dict)
    
    conn.close()
    
    return render_template('index.html', 
                         projects=formatted_projects,
                         stages=LICENSING_STAGES,
                         current_stage=stage_filter,
                         search=search,
                         sort_by=sort_by,
                         project_count=len(formatted_projects))

@app.route('/team-leaders')
def team_leaders():
    """עמוד ראשי צוותים"""
    conn = get_db_connection()
    
    # קבלת ראשי צוותים ייחודיים
    team_leaders = conn.execute("""
        SELECT DISTINCT team_leader 
        FROM projects 
        WHERE team_leader IS NOT NULL AND team_leader != '' 
        ORDER BY team_leader
    """).fetchall()
    
    team_leader_filter = request.args.get('team_leader', '')
    
    # בניית שאילתה
    query = """
        SELECT 
            id, project_name, request_number, info_file_number,
            date, opening_date, status_date, committee_date, permit_validity_date,
            team_leader, stage, request_types, engineer, management_company,
            entrepreneur_name, architect, city, notes,
            info_date_extension, opening_date_extension, status_date_extension,
            committee_date_extension, permit_validity_date_extension, city_team
        FROM projects
    """
    
    params = []
    if team_leader_filter:
        query += " WHERE team_leader = ?"
        params.append(team_leader_filter)
    
    query += " ORDER BY team_leader, project_name"
    
    projects = conn.execute(query, params).fetchall()
    
    # קיבוץ לפי ראש צוות
    projects_by_leader = {}
    for project in projects:
        project_dict = dict(project)
        
        # עיצוב התאריכים
        if project_dict.get('date'):
            project_dict['formatted_info_date'] = format_date_with_extension(
                project_dict['date'], 
                project_dict.get('info_date_extension', 0), 
                'info'
            )
        
        if project_dict.get('opening_date'):
            project_dict['formatted_opening_date'] = format_date_with_extension(
                project_dict['opening_date'], 
                project_dict.get('opening_date_extension', 0), 
                'opening'
            )
        
        if project_dict.get('committee_date'):
            project_dict['formatted_committee_date'] = format_date_with_extension(
                project_dict['committee_date'], 
                project_dict.get('committee_date_extension', 0), 
                'committee'
            )
        
        if project_dict.get('permit_validity_date'):
            project_dict['formatted_permit_date'] = format_date_with_extension(
                project_dict['permit_validity_date'], 
                project_dict.get('permit_validity_date_extension', 0), 
                'permit'
            )
        
        # קביעת צבע השורה
        project_dict['row_color'] = get_row_color_class(project_dict)
        
        leader = project_dict['team_leader']
        if leader not in projects_by_leader:
            projects_by_leader[leader] = []
        projects_by_leader[leader].append(project_dict)
    
    conn.close()
    
    return render_template('team_leaders.html',
                         projects_by_leader=projects_by_leader,
                         team_leaders=[tl['team_leader'] for tl in team_leaders],
                         current_team_leader=team_leader_filter)

@app.route('/city-teams')
def city_teams():
    """עמוד צוותי עירייה"""
    conn = get_db_connection()
    
    city_team_filter = request.args.get('city_team', '')
    
    # שלבים רלוונטיים לצוותי העירייה
    relevant_stages = ["נפתח לפני החלטת ועדה", "בדיקה סופית"]
    
    query = """
        SELECT 
            id, project_name, request_number, info_file_number,
            date, opening_date, status_date, committee_date, permit_validity_date,
            team_leader, stage, request_types, engineer, management_company,
            entrepreneur_name, architect, city, notes,
            info_date_extension, opening_date_extension, status_date_extension,
            committee_date_extension, permit_validity_date_extension, city_team
        FROM projects
        WHERE stage IN (?, ?)
    """
    
    params = relevant_stages.copy()
    
    if city_team_filter:
        query += " AND city_team = ?"
        params.append(city_team_filter)
    
    query += " ORDER BY city_team, engineer, stage, opening_date"
    
    projects = conn.execute(query, params).fetchall()
    
    # קיבוץ לפי צוות עירייה ומהנדס
    projects_by_team = {}
    for project in projects:
        project_dict = dict(project)
        
        # עיצוב התאריכים
        if project_dict.get('opening_date'):
            project_dict['formatted_opening_date'] = format_date_with_extension(
                project_dict['opening_date'], 
                project_dict.get('opening_date_extension', 0), 
                'opening'
            )
        
        if project_dict.get('committee_date'):
            project_dict['formatted_committee_date'] = format_date_with_extension(
                project_dict['committee_date'], 
                project_dict.get('committee_date_extension', 0), 
                'committee'
            )
        
        # קביעת צבע השורה - מיוחד לצוותי עירייה
        stage = project_dict.get('stage', '')
        if stage == "נפתח לפני החלטת ועדה":
            project_dict['row_color'] = "stage_committee"
        elif stage == "בדיקה סופית":
            project_dict['row_color'] = "stage_final"
        else:
            project_dict['row_color'] = ""
        
        team = project_dict.get('city_team', 'לא מוגדר')
        engineer = project_dict.get('engineer', 'לא מוגדר')
        
        if team not in projects_by_team:
            projects_by_team[team] = {}
        if engineer not in projects_by_team[team]:
            projects_by_team[team][engineer] = []
        
        projects_by_team[team][engineer].append(project_dict)
    
    conn.close()
    
    return render_template('city_teams.html',
                         projects_by_team=projects_by_team,
                         city_teams=CITY_TEAMS,
                         current_city_team=city_team_filter,
                         relevant_stages=relevant_stages)

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    """פרטי פרויקט בודד"""
    conn = get_db_connection()
    
    project = conn.execute("""
        SELECT 
            id, project_name, request_number, info_file_number,
            date, opening_date, status_date, committee_date, permit_validity_date,
            team_leader, stage, request_types, engineer, management_company,
            entrepreneur_name, architect, city, notes,
            info_date_extension, opening_date_extension, status_date_extension,
            committee_date_extension, permit_validity_date_extension, city_team
        FROM projects
        WHERE id = ?
    """, (project_id,)).fetchone()
    
    conn.close()
    
    if not project:
        return "פרויקט לא נמצא", 404
    
    project_dict = dict(project)
    
    # עיצוב התאריכים
    if project_dict.get('date'):
        project_dict['formatted_info_date'] = format_date_with_extension(
            project_dict['date'], 
            project_dict.get('info_date_extension', 0), 
            'info'
        )
    
    if project_dict.get('opening_date'):
        project_dict['formatted_opening_date'] = format_date_with_extension(
            project_dict['opening_date'], 
            project_dict.get('opening_date_extension', 0), 
            'opening'
        )
    
    if project_dict.get('committee_date'):
        project_dict['formatted_committee_date'] = format_date_with_extension(
            project_dict['committee_date'], 
            project_dict.get('committee_date_extension', 0), 
            'committee'
        )
    
    if project_dict.get('permit_validity_date'):
        project_dict['formatted_permit_date'] = format_date_with_extension(
            project_dict['permit_validity_date'], 
            project_dict.get('permit_validity_date_extension', 0), 
            'permit'
        )
    
    return render_template('project_detail.html', project=project_dict)

@app.route('/api/stats')
def api_stats():
    """API לנתונים סטטיסטיים"""
    conn = get_db_connection()
    
    # סטטיסטיקות כלליות
    total_projects = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
    
    # לפי שלבים
    stages_stats = conn.execute("""
        SELECT stage, COUNT(*) as count
        FROM projects
        GROUP BY stage
        ORDER BY count DESC
    """).fetchall()
    
    # לפי צוותי עירייה
    city_teams_stats = conn.execute("""
        SELECT city_team, COUNT(*) as count
        FROM projects
        WHERE city_team IS NOT NULL
        GROUP BY city_team
        ORDER BY count DESC
    """).fetchall()
    
    # לפי ראשי צוותים
    team_leaders_stats = conn.execute("""
        SELECT team_leader, COUNT(*) as count
        FROM projects
        WHERE team_leader IS NOT NULL
        GROUP BY team_leader
        ORDER BY count DESC
    """).fetchall()
    
    conn.close()
    
    return jsonify({
        'total_projects': total_projects,
        'stages_stats': [dict(row) for row in stages_stats],
        'city_teams_stats': [dict(row) for row in city_teams_stats],
        'team_leaders_stats': [dict(row) for row in team_leaders_stats]
    })

# Initialize database when the module is imported
init_database()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
