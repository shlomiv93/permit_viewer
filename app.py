# app.py - שרת Flask לפריסה ב-Render
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime, timedelta
import json
import sys

# יצירת אפליקציית Flask
app = Flask(__name__)
CORS(app)

# הגדרת נתיב למסד הנתונים - קודם נבדוק אם הקובץ קיים
def find_database_path():
    """מחפש את מסד הנתונים במיקומים שונים"""
    possible_paths = [
        'licensing_system.db',
        './licensing_system.db',
        os.path.join(os.getcwd(), 'licensing_system.db')
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"מסד נתונים נמצא ב: {path}")
            return path
    
    print("מסד נתונים לא נמצא, יווצר חדש")
    return 'licensing_system.db'

DATABASE_PATH = find_database_path()

print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print(f"Database path: {DATABASE_PATH}")

def get_db_connection():
    """יצירת חיבור למסד הנתונים"""
    try:
        if not os.path.exists(DATABASE_PATH):
            print(f"מסד הנתונים לא נמצא ב: {DATABASE_PATH}")
            return None
            
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # מאפשר גישה לעמודות לפי שם
        return conn
    except Exception as e:
        print(f"שגיאה בחיבור למסד הנתונים: {e}")
        print(f"נתיב מסד הנתונים: {DATABASE_PATH}")
        print(f"תיקיית עבודה: {os.getcwd()}")
        import traceback
        print(traceback.format_exc())
        return NoneDATABASE_PATH} לא קיים, מחפש מסד נתונים...")
            
            # חיפוש אחר קובץ licensing_system.db
            current_dir = os.getcwd()
            possible_paths = [
                'licensing_system.db',
                './licensing_system.db',
                'database/licensing_system.db',
                'data/licensing_system.db',
                os.path.join(current_dir, 'licensing_system.db')
            ]
            
            found_db = None
            for path in possible_paths:
                if os.path.exists(path):
                    found_db = path
                    print(f"מסד נתונים נמצא ב: {path}")
                    break
            
            if found_db:
                global DATABASE_PATH
                DATABASE_PATH = found_db
        
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # מאפשר גישה לעמודות לפי שם
        return conn
    except Exception as e:
        print(f"שגיאה בחיבור למסד הנתונים: {e}")
        print(f"נתיב מסד הנתונים: {DATABASE_PATH}")
        print(f"תיקיית עבודה: {os.getcwd()}")
        print(f"קבצים בתיקייה: {os.listdir('.')}")
        import traceback
        print(traceback.format_exc())
        return None

def create_sample_data_direct(conn):
    """יצירת נתוני דמו ישירות"""
    try:
        cursor = conn.cursor()
        
        sample_projects = [
            (
                "פרויקט מגורים דוגמה 1", "2024/001", "INFO-001", "2023-01-15",
                "2023-02-01", "2023-03-01", "2023-04-01", "2024-01-01",
                "ישראל כהן", "דנה לוי", "הליך פתיחה", "בנייה חדשה",
                "חברת ניהול א'", "יוסי פרויקטים", "אדריכל בכיר", "תל אביב",
                "פרויקט חשוב במיוחד", "מרכז", 0, 0, 0, 0, 0
            ),
            (
                "פרויקט תמא 38 דוגמה", "2024/002", "INFO-002", "2023-06-15",
                "2023-07-01", "2023-08-01", "2023-09-01", "2024-06-01",
                "מיכל דוד", "אבי שמש", "נפתח לפני החלטת ועדה", "תמא 38",
                "חברת ניהול ב'", "שרה בנייה", "אדריכל מומחה", "ירושלים",
                "דורש בדיקה מיוחדת", "דרום", 0, 0, 0, 0, 0
            ),
            (
                "מגדל מגורים חדש", "2024/003", "INFO-003", "2024-01-10",
                "2024-02-15", "2024-03-20", "2024-04-25", "2025-01-10",
                "רונית ברק", "עמית גל", "בדיקה מרחבית אחרי ועדה", "בנייה חדשה",
                "חברת ניהול ג'", "דוד יזמות", "סטודיו אדריכלות", "חיפה",
                "פרויקט של 20 קומות", "צפון", 0, 0, 0, 0, 0
            ),
            (
                "פרויקט חידוש עירוני", "2024/004", "INFO-004", "2024-03-01",
                "2024-04-01", "2024-05-01", "2024-06-01", "2025-03-01",
                "ליאור זהב", "מיכל רוזן", "בדיקת תכן", "היתר שינויים",
                "חברת פיתוח ד'", "רחל נכסים", "משרד אדריכלות מוביל", "באר שבע",
                "פרויקט חידוש אזור מרכזי", "דרום", 30, 0, 0, 60, 0
            ),
            (
                "מתחם מסחרי חדש", "2024/005", "INFO-005", "2024-04-15",
                "2024-05-15", "2024-06-15", "2024-07-15", "2025-04-15",
                "ענת שחר", "יונתן כהן", "בדיקה סופית", "בנייה חדשה",
                "חברת ניהול ה'", "משה יזמות", "אדריכל יצירתי", "נתניה",
                "מתחם מסחרי ומשרדים", "מרכז", 0, 45, 0, 0, 90
            ),
            (
                "פרויקט תמא 38 מתקדם", "2024/006", "INFO-006", "2024-01-20",
                "2024-02-20", "2024-03-25", "2024-04-30", "2025-01-20",
                "אלון ברק", "שירה לוי", "אגרות והשבחה", "תמא 38",
                "חברת ניהול ו'", "אבי פיתוח", "סטודיו עיצוב", "פתח תקווה",
                "פרויקט תמא מורכב", "מרכז", 60, 0, 0, 120, 0
            ),
            (
                "בניין מגורים יוקרה", "2024/007", "INFO-007", "2023-12-01",
                "2024-01-05", "2024-02-10", "2024-03-15", "2024-12-01",
                "נועה כהן", "רועי דוד", "נמסר היתר", "בנייה חדשה",
                "חברת פרמיום", "גיל נכסים", "אדריכל מפורסם", "רמת גן",
                "בניין יוקרה 15 קומות", "מרכז", 0, 0, 0, 0, 180
            ),
            (
                "פרויקט שיקום מבנה", "2024/008", "INFO-008", "2024-05-01",
                "2024-06-01", "2024-07-01", "2024-08-01", "2025-05-01",
                "דני שטרן", "מיה אלון", "הליך פתיחה", "היתר שינויים",
                "חברת שיקום", "לי שימור", "מומחה שימור", "יפו",
                "שיקום מבנה היסטורי", "מרכז", 0, 15, 0, 0, 0
            )
        ]
        
        cursor.executemany("""
            INSERT INTO projects (
                project_name, request_number, info_file_number, date,
                opening_date, status_date, committee_date, permit_validity_date,
                team_leader, engineer, stage, request_types,
                management_company, entrepreneur_name, architect, city,
                notes, city_team, info_date_extension, opening_date_extension,
                status_date_extension, committee_date_extension, permit_validity_date_extension
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_projects)
        
        conn.commit()
        print(f"נוספו {len(sample_projects)} פרויקטי דמו למסד הנתונים")
        
    except Exception as e:
        print(f"שגיאה ביצירת נתוני דמו: {e}")
        import traceback
        print(traceback.format_exc())

def init_database():
    """אתחול מסד הנתונים"""
    try:
        print(f"מאתחל מסד נתונים ב: {DATABASE_PATH}")
        
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # יצירת טבלה אם לא קיימת
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
        print("מסד הנתונים אותחל בהצלחה")
        
        # בדיקה אם יש נתונים במסד
        cursor.execute("SELECT COUNT(*) FROM projects")
        count = cursor.fetchone()[0]
        print(f"מספר פרויקטים במסד: {count}")
        
        if count == 0:
            print("מוסיף נתוני דמו...")
            create_sample_data_direct(conn)
        
        conn.close()
        print("אתחול מסד הנתונים הושלם")
        
    except Exception as e:
        print(f"שגיאה באתחול מסד הנתונים: {e}")
        import traceback
        print(traceback.format_exc())

# אתחול מסד הנתונים כשהמודול נטען
def initialize_on_startup():
    """אתחול שרץ בעת טעינת המודול"""
    print("מאתחל מסד נתונים בעת הטעינה...")
    try:
        # בדיקה מפורטת של מיקום הקובץ
        current_dir = os.getcwd()
        print(f"תיקיית עבודה נוכחית: {current_dir}")
        
        # בדיקת קבצים בתיקייה הנוכחית
        files_in_current = os.listdir('.')
        print(f"קבצים בתיקייה הנוכחית: {files_in_current}")
        
        # בדיקת קיום מסד הנתונים
        if os.path.exists(DATABASE_PATH):
            size = os.path.getsize(DATABASE_PATH)
            print(f"מסד נתונים נמצא ב: {DATABASE_PATH} (גודל: {size} בתים)")
            
            # בדיקת תוכן המסד
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            # בדיקת טבלאות
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"טבלאות במסד: {tables}")
            
            if 'projects' in tables:
                cursor.execute("SELECT COUNT(*) FROM projects")
                count = cursor.fetchone()[0]
                print(f"מספר פרויקטים במסד: {count}")
                
                # הדפסת דוגמת פרויקט
                cursor.execute("SELECT project_name, stage FROM projects LIMIT 3")
                samples = cursor.fetchall()
                print(f"דוגמאות פרויקטים: {samples}")
            else:
                print("טבלת projects לא נמצאה - מאתחל טבלאות...")
                init_database()
            
            conn.close()
        else:
            print("מסד נתונים לא נמצא - יווצר חדש")
            init_database()
        
        print("אתחול מסד הנתונים הושלם בהצלחה")
    except Exception as e:
        print(f"שגיאה באתחול מסד הנתונים: {e}")
        import traceback
        print(traceback.format_exc())
        
        # במקרה של שגיאה, נסה ליצור מסד חדש
        try:
            print("מנסה ליצור מסד נתונים חדש...")
            init_database()
        except Exception as e2:
            print(f"שגיאה גם ביצירת מסד חדש: {e2}")

# הפעלת אתחול
initialize_on_startup()

# Routes
@app.route('/')
def index():
    """עמוד בית - הצפיין"""
    print("מגיש עמוד בית")
    return render_template('index.html')

@app.route('/api/projects')
def get_projects():
    """API לקבלת כל הפרויקטים"""
    print("מקבל בקשה לפרויקטים...")
    
    # בדיקה אם מסד הנתונים קיים
    if not os.path.exists(DATABASE_PATH):
        print(f"מסד הנתונים לא נמצא ב: {DATABASE_PATH}")
        print("מנסה לאתחל מסד הנתונים...")
        init_database()
    
    conn = get_db_connection()
    if not conn:
        print("לא הצלחתי להתחבר למסד הנתונים")
        return jsonify({"error": "שגיאה בחיבור למסד הנתונים"}), 500
    
    try:
        cursor = conn.cursor()
        
        # בדיקה אם הטבלה קיימת
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects'")
        if not cursor.fetchone():
            print("טבלת projects לא קיימת - מאתחל מסד נתונים")
            conn.close()
            init_database()
            conn = get_db_connection()
            cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                id, project_name, request_number, info_file_number,
                date, opening_date, status_date, committee_date, permit_validity_date,
                team_leader, engineer, stage, request_types,
                management_company, entrepreneur_name, architect, city, notes,
                city_team, info_date_extension, opening_date_extension,
                status_date_extension, committee_date_extension, permit_validity_date_extension
            FROM projects
            ORDER BY project_name
        """)
        
        projects = []
        for row in cursor.fetchall():
            project = dict(row)
            projects.append(project)
        
        print(f"מחזיר {len(projects)} פרויקטים")
        response = jsonify(projects)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
        
    except Exception as e:
        print(f"שגיאה בקבלת פרויקטים: {e}")
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": "שגיאה בקבלת נתונים", "details": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/projects/<int:project_id>')
def get_project(project_id):
    """API לקבלת פרויקט ספציפי"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "שגיאה בחיבור למסד הנתונים"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM projects WHERE id = ?
        """, (project_id,))
        
        row = cursor.fetchone()
        if row:
            project = dict(row)
            return jsonify(project)
        else:
            return jsonify({"error": "פרויקט לא נמצא"}), 404
            
    except Exception as e:
        print(f"שגיאה בקבלת פרויקט: {e}")
        return jsonify({"error": "שגיאה בקבלת נתונים"}), 500
    finally:
        conn.close()

@app.route('/api/stats')
def get_stats():
    """API לקבלת סטטיסטיקות"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "שגיאה בחיבור למסד הנתונים"}), 500
    
    try:
        cursor = conn.cursor()
        
        # סטטיסטיקות כלליות
        cursor.execute("SELECT COUNT(*) as total FROM projects")
        total = cursor.fetchone()[0]
        
        # סטטיסטיקות לפי שלב
        cursor.execute("""
            SELECT stage, COUNT(*) as count 
            FROM projects 
            GROUP BY stage
        """)
        stages_stats = {row[0]: row[1] for row in cursor.fetchall()}
        
        # סטטיסטיקות לפי עיר
        cursor.execute("""
            SELECT city, COUNT(*) as count 
            FROM projects 
            GROUP BY city 
            ORDER BY count DESC
        """)
        cities_stats = {row[0]: row[1] for row in cursor.fetchall()}
        
        return jsonify({
            "total_projects": total,
            "stages": stages_stats,
            "cities": cities_stats
        })
        
    except Exception as e:
        print(f"שגיאה בקבלת סטטיסטיקות: {e}")
        return jsonify({"error": "שגיאה בקבלת נתונים"}), 500
    finally:
        conn.close()

@app.route('/api/filters')
def get_filters():
    """API לקבלת רשימות לסינון"""
    print("מקבל בקשה לרשימות סינון...")
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "שגיאה בחיבור למסד הנתונים"}), 500
    
    try:
        cursor = conn.cursor()
        
        # רשימת מהנדסים
        cursor.execute("SELECT DISTINCT engineer FROM projects WHERE engineer IS NOT NULL AND engineer != '' ORDER BY engineer")
        engineers = [row[0] for row in cursor.fetchall()]
        
        # רשימת ראשי צוותים
        cursor.execute("SELECT DISTINCT team_leader FROM projects WHERE team_leader IS NOT NULL AND team_leader != '' ORDER BY team_leader")
        team_leaders = [row[0] for row in cursor.fetchall()]
        
        # רשימת ערים
        cursor.execute("SELECT DISTINCT city FROM projects WHERE city IS NOT NULL AND city != '' ORDER BY city")
        cities = [row[0] for row in cursor.fetchall()]
        
        # רשימת שלבים
        cursor.execute("SELECT DISTINCT stage FROM projects WHERE stage IS NOT NULL AND stage != '' ORDER BY stage")
        stages = [row[0] for row in cursor.fetchall()]
        
        result = {
            "engineers": engineers,
            "team_leaders": team_leaders,
            "cities": cities,
            "stages": stages
        }
        
        print(f"מחזיר רשימות סינון: {len(engineers)} מהנדסים, {len(team_leaders)} ראשי צוותים, {len(cities)} ערים, {len(stages)} שלבים")
        
        response = jsonify(result)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
        
    except Exception as e:
        print(f"שגיאה בקבלת רשימות סינון: {e}")
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": "שגיאה בקבלת נתונים", "details": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/health')
def health():
    """endpoint לבדיקת תקינות השרת"""
    try:
        # בדיקה בסיסית
        status = {"status": "healthy", "timestamp": datetime.now().isoformat()}
        
        # בדיקת מסד נתונים
        if os.path.exists(DATABASE_PATH):
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM projects")
                count = cursor.fetchone()[0]
                status["database"] = "connected"
                status["projects_count"] = count
                conn.close()
            else:
                status["database"] = "connection_failed"
        else:
            status["database"] = "not_found"
            
        response = jsonify(status)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
        
    except Exception as e:
        error_status = {
            "status": "error", 
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }
        response = jsonify(error_status)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 500

@app.route('/files')
def list_files():
    """endpoint לרשימת קבצים - עזרה לדיבאג"""
    try:
        current_dir = os.getcwd()
        files = {}
        
        # קבצים בתיקייה הנוכחית
        files['current_directory'] = current_dir
        files['files_in_current'] = os.listdir('.')
        
        # חיפוש קבצי DB
        db_files = []
        for root, dirs, filenames in os.walk('.'):
            for filename in filenames:
                if filename.endswith('.db'):
                    full_path = os.path.join(root, filename)
                    size = os.path.getsize(full_path)
                    db_files.append({
                        'path': full_path,
                        'size': size,
                        'exists': os.path.exists(full_path)
                    })
        
        files['database_files'] = db_files
        files['current_database_path'] = DATABASE_PATH
        files['database_exists'] = os.path.exists(DATABASE_PATH)
        
        response = jsonify(files)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
        
    except Exception as e:
        error_info = {
            "error": str(e),
            "current_directory": os.getcwd()
        }
        response = jsonify(error_info)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 500
    """endpoint לדיבאג"""
    try:
        debug_info = {
            "timestamp": datetime.now().isoformat(),
            "database_path": DATABASE_PATH,
            "database_exists": os.path.exists(DATABASE_PATH),
            "working_directory": os.getcwd(),
            "directory_contents": os.listdir('.'),
            "database_size": os.path.getsize(DATABASE_PATH) if os.path.exists(DATABASE_PATH) else 0,
        }
        
        # נסה להתחבר למסד הנתונים
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            # בדיקת טבלאות
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            debug_info["tables"] = tables
            
            # אם יש טבלת projects
            if 'projects' in tables:
                cursor.execute("SELECT COUNT(*) FROM projects")
                count = cursor.fetchone()[0]
                debug_info["projects_count"] = count
                
                # דוגמה לפרויקט
                cursor.execute("SELECT * FROM projects LIMIT 1")
                sample = cursor.fetchone()
                if sample:
                    debug_info["sample_project"] = dict(sample)
            
            conn.close()
            debug_info["database_connection"] = "success"
        else:
            debug_info["database_connection"] = "failed"
            
        response = jsonify(debug_info)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
        
    except Exception as e:
        error_info = {
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "database_path": DATABASE_PATH,
            "working_directory": os.getcwd(),
        }
        import traceback
        error_info["traceback"] = traceback.format_exc()
        
        response = jsonify(error_info)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response

@app.errorhandler(404)
def not_found(error):
    """טיפול בשגיאות 404"""
    return jsonify({"error": "הנתיב לא נמצא", "path": request.path}), 404

@app.errorhandler(500)
def internal_error(error):
    """טיפול בשגיאות 500"""
    return jsonify({"error": "שגיאה פנימית בשרת", "details": str(error)}), 500

@app.before_request
def log_request():
    """רישום כל בקשה"""
    print(f"=== בקשה: {request.method} {request.path} ===")
    print(f"User-Agent: {request.headers.get('User-Agent', 'לא זמין')}")
    print(f"IP: {request.remote_addr}")

@app.after_request
def log_response(response):
    """רישום תגובה"""
    print(f"=== תגובה: {response.status_code} ===")
    return response

if __name__ == '__main__':
    print("מתחיל השרת במצב פיתוח...")
    print(f"תיקיית עבודה: {os.getcwd()}")
    print(f"נתיב מסד נתונים: {DATABASE_PATH}")
    print(f"קבצים בתיקייה: {os.listdir('.')}")
    
    # בדיקה אם קובץ מסד הנתונים קיים
    if os.path.exists(DATABASE_PATH):
        print(f"מסד הנתונים קיים. גודל: {os.path.getsize(DATABASE_PATH)} בתים")
    else:
        print("מסד הנתונים לא קיים - יווצר אוטומטית")
    
    # הפעלת השרת
    port = int(os.environ.get('PORT', 5000))
    print(f"מפעיל שרת על פורט {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
else:
    print("האפליקציה נטענה במצב production")
    print(f"תיקיית עבודה: {os.getcwd()}")
    print(f"נתיב מסד נתונים: {DATABASE_PATH}")
    
    # רישום routes זמינים
    print("Routes זמינים:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint}")
    
    # בדיקה אם קובץ מסד הנתונים קיים
    if os.path.exists(DATABASE_PATH):
        print(f"מסד הנתונים קיים. גודל: {os.path.getsize(DATABASE_PATH)} בתים")
    else:
        print("מסד הנתונים לא קיים - יווצר אוטומטית")
