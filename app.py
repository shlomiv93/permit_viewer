# app.py - שרת Flask לפריסה ב-Render
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime, timedelta
import json

app = Flask(__name__)
CORS(app)

# הגדרת נתיב למסד הנתונים
DATABASE_PATH = os.environ.get('DATABASE_PATH', 'licensing_system.db')

def get_db_connection():
    """יצירת חיבור למסד הנתונים"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # מאפשר גישה לעמודות לפי שם
        return conn
    except Exception as e:
        print(f"שגיאה בחיבור למסד הנתונים: {e}")
        return None

def create_sample_data():
    """יצירת נתוני דמו אם המסד ריק"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # בדיקה אם יש נתונים במסד
        cursor.execute("SELECT COUNT(*) FROM projects")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # הוספת נתוני דמו
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
            print("נתוני דמו נוספו למסד הנתונים")
            
    except Exception as e:
        print(f"שגיאה ביצירת נתוני דמו: {e}")
    finally:
        conn.close()

def init_database():
    """אתחול מסד הנתונים"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
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
        
        # יצירת נתוני דמו אם צריך
        create_sample_data()
        
    except Exception as e:
        print(f"שגיאה באתחול מסד הנתונים: {e}")
    finally:
        conn.close()

@app.route('/')
def index():
    """עמוד בית - הצפיין"""
    return render_template('index.html')

@app.route('/api/projects')
def get_projects():
    """API לקבלת כל הפרויקטים"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "שגיאה בחיבור למסד הנתונים"}), 500
    
    try:
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
        
        return jsonify(projects)
        
    except Exception as e:
        print(f"שגיאה בקבלת פרויקטים: {e}")
        return jsonify({"error": "שגיאה בקבלת נתונים"}), 500
    finally:
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
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "שגיאה בחיבור למסד הנתונים"}), 500
    
    try:
        cursor = conn.cursor()
        
        # רשימת מהנדסים
        cursor.execute("SELECT DISTINCT engineer FROM projects WHERE engineer IS NOT NULL ORDER BY engineer")
        engineers = [row[0] for row in cursor.fetchall()]
        
        # רשימת ראשי צוותים
        cursor.execute("SELECT DISTINCT team_leader FROM projects WHERE team_leader IS NOT NULL ORDER BY team_leader")
        team_leaders = [row[0] for row in cursor.fetchall()]
        
        # רשימת ערים
        cursor.execute("SELECT DISTINCT city FROM projects WHERE city IS NOT NULL ORDER BY city")
        cities = [row[0] for row in cursor.fetchall()]
        
        # רשימת שלבים
        cursor.execute("SELECT DISTINCT stage FROM projects WHERE stage IS NOT NULL ORDER BY stage")
        stages = [row[0] for row in cursor.fetchall()]
        
        return jsonify({
            "engineers": engineers,
            "team_leaders": team_leaders,
            "cities": cities,
            "stages": stages
        })
        
    except Exception as e:
        print(f"שגיאה בקבלת רשימות סינון: {e}")
        return jsonify({"error": "שגיאה בקבלת נתונים"}), 500
    finally:
        conn.close()

@app.route('/health')
def health():
    """endpoint לבדיקת תקינות השרת"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    # אתחול מסד הנתונים
    init_database()
    
    # הפעלת השרת
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
