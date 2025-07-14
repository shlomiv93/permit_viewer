from flask import Flask, render_template, jsonify, request, send_file
import sqlite3
import os
from datetime import datetime, timedelta
import json
import tempfile
import pandas as pd
from functools import lru_cache
import calendar
from workalendar.asia import Israel

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# הגדרת נתיב מסד הנתונים - בדיקה אם קיים ברנדר
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get('DATABASE_URL', os.path.join(BASE_DIR, 'licensing_system.db'))


# יצירת אובייקט לוח שנה ישראלי
israel_calendar = Israel()


def init_database():
    """יצירת מסד נתונים ריק אם לא קיים"""
    if not os.path.exists(DB_PATH):
        print(f"יוצר מסד נתונים חדש ב: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # יצירת טבלת הפרויקטים
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT,
                request_number TEXT,
                info_file_number TEXT,
                date TEXT,
                opening_date TEXT,
                status_date TEXT,
                committee_date TEXT,
                permit_validity_date TEXT,
                team_leader TEXT,
                stage TEXT,
                request_types TEXT,
                engineer TEXT,
                management_company TEXT,
                entrepreneur_name TEXT,
                architect TEXT,
                city TEXT,
                notes TEXT,
                info_date_extension INTEGER DEFAULT 0,
                opening_date_extension INTEGER DEFAULT 0,
                status_date_extension INTEGER DEFAULT 0,
                committee_date_extension INTEGER DEFAULT 0,
                permit_validity_date_extension INTEGER DEFAULT 0,
                city_team TEXT
            )
        """)
        
        # הוספת נתונים דמה לבדיקה
        cursor.execute("""
            INSERT INTO projects (
                project_name, request_number, info_file_number, date, opening_date,
                team_leader, stage, engineer, city
            ) VALUES (
                'פרויקט לדוגמה', '2024/001', 'TIK001', '2024-01-15', '2024-02-01',
                'יוסי כהן', 'נפתח לפני החלטת ועדה', 'דנה לוי', 'תל אביב'
            )
        """)
        
        conn.commit()
        conn.close()
        print("מסד הנתונים נוצר בהצלחה")


class DatabaseManager:
    """מנהל מסד הנתונים"""

    @staticmethod
    def get_connection():
        """יצירת חיבור למסד הנתונים"""
        try:
            return sqlite3.connect(DB_PATH)
        except Exception as e:
            print(f"שגיאה בחיבור למסד הנתונים: {e}")
            # נסה ליצור מסד נתונים חדש
            init_database()
            return sqlite3.connect(DB_PATH)

    @staticmethod
    def get_all_projects():
        """שליפת כל הפרויקטים"""
        try:
            conn = DatabaseManager.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT 
                    id, project_name, request_number, info_file_number,
                    date, opening_date, status_date, committee_date, permit_validity_date, 
                    team_leader, stage, request_types, engineer, management_company, 
                    entrepreneur_name, architect, city, notes,
                    info_date_extension, opening_date_extension, status_date_extension,
                    committee_date_extension, permit_validity_date_extension, city_team
                FROM projects
                ORDER BY project_name
            """)

            projects = cursor.fetchall()
            conn.close()
            return projects
        except Exception as e:
            print(f"שגיאה בשליפת פרויקטים: {e}")
            return []

    @staticmethod
    def get_projects_by_stage(stage):
        """שליפת פרויקטים לפי שלב"""
        try:
            conn = DatabaseManager.get_connection()
            cursor = conn.cursor()

            if stage == "הכל":
                return DatabaseManager.get_all_projects()

            cursor.execute("""
                SELECT 
                    id, project_name, request_number, info_file_number,
                    date, opening_date, status_date, committee_date, permit_validity_date, 
                    team_leader, stage, request_types, engineer, management_company, 
                    entrepreneur_name, architect, city, notes,
                    info_date_extension, opening_date_extension, status_date_extension,
                    committee_date_extension, permit_validity_date_extension, city_team
                FROM projects
                WHERE stage = ?
                ORDER BY project_name
            """, (stage,))

            projects = cursor.fetchall()
            conn.close()
            return projects
        except Exception as e:
            print(f"שגיאה בשליפת פרויקטים לפי שלב: {e}")
            return []

    @staticmethod
    def search_projects(search_term):
        """חיפוש פרויקטים"""
        try:
            conn = DatabaseManager.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT 
                    id, project_name, request_number, info_file_number,
                    date, opening_date, status_date, committee_date, permit_validity_date, 
                    team_leader, stage, request_types, engineer, management_company, 
                    entrepreneur_name, architect, city, notes,
                    info_date_extension, opening_date_extension, status_date_extension,
                    committee_date_extension, permit_validity_date_extension, city_team
                FROM projects 
                WHERE LOWER(project_name) LIKE ? 
                   OR LOWER(request_number) LIKE ?
                   OR LOWER(info_file_number) LIKE ?
                   OR LOWER(city) LIKE ?
                   OR LOWER(engineer) LIKE ?
                   OR LOWER(team_leader) LIKE ?
                   OR LOWER(entrepreneur_name) LIKE ?
                   OR LOWER(architect) LIKE ?
                   OR LOWER(notes) LIKE ?
                ORDER BY project_name
            """, tuple([f'%{search_term.lower()}%'] * 9))

            projects = cursor.fetchall()
            conn.close()
            return projects
        except Exception as e:
            print(f"שגיאה בחיפוש פרויקטים: {e}")
            return []

    @staticmethod
    def get_team_leaders():
        """שליפת ראשי צוותים"""
        try:
            conn = DatabaseManager.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT DISTINCT team_leader 
                FROM projects 
                WHERE team_leader IS NOT NULL AND team_leader != '' 
                ORDER BY team_leader
            """)

            leaders = [row[0] for row in cursor.fetchall()]
            conn.close()
            return leaders
        except Exception as e:
            print(f"שגיאה בשליפת ראשי צוותים: {e}")
            return []

    @staticmethod
    def get_city_teams():
        """שליפת צוותי עירייה"""
        try:
            conn = DatabaseManager.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT DISTINCT city_team 
                FROM projects 
                WHERE city_team IS NOT NULL AND city_team != '' 
                ORDER BY city_team
            """)

            teams = [row[0] for row in cursor.fetchall()]
            conn.close()
            return teams
        except Exception as e:
            print(f"שגיאה בשליפת צוותי עירייה: {e}")
            return []


class DateFormatter:
    """מחלקה לעיצוב תאריכים"""

    @staticmethod
    @lru_cache(maxsize=1000)
    def calculate_business_days(start_date_str, business_days_to_add):
        """חישוב ימי עסקים"""
        if not start_date_str:
            return ""

        try:
            if '\n' in start_date_str:
                start_date_str = start_date_str.split('\n')[0]

            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            result_date = israel_calendar.add_working_days(start_date, business_days_to_add)
            return result_date.strftime('%Y-%m-%d')
        except Exception as e:
            print(f"שגיאה בחישוב ימי עסקים: {e}")
            return ""

    @staticmethod
    def format_date_with_extension(date_str, extension_value, field_type):
        """עיצוב תאריך עם הארכה"""
        if not date_str:
            return ""

        try:
            original_date = datetime.strptime(date_str, '%Y-%m-%d')

            # תאריך יעד ספציפי
            if extension_value < -100000000:
                date_number = abs(extension_value + 100000000)
                year = date_number // 10000
                month = (date_number % 10000) // 100
                day = date_number % 100

                try:
                    target_date = datetime(year, month, day)
                    return f"{date_str}\n(תאריך יעד: {target_date.strftime('%Y-%m-%d')})"
                except ValueError:
                    return DateFormatter.format_base_date_by_type(date_str, field_type)

            # 90 ימי עסקים מיוחד
            elif extension_value == -90:
                if field_type == 'opening':
                    target_date_str = DateFormatter.calculate_business_days(date_str, 90)
                    return f"{date_str}\n(90 ימי עסקים: {target_date_str})"
                else:
                    base_date = DateFormatter.calculate_base_date_by_type(original_date, field_type)
                    target_date_str = DateFormatter.calculate_business_days(base_date.strftime('%Y-%m-%d'), 90)
                    return f"{date_str}\n({DateFormatter.get_base_description(field_type)} + 90 ימי עסקים: {target_date_str})"

            # ימי עסקים רגילים
            elif extension_value < -1000:
                business_days = abs(extension_value) - 1000
                base_date = DateFormatter.calculate_base_date_by_type(original_date, field_type)
                target_date_str = DateFormatter.calculate_business_days(base_date.strftime('%Y-%m-%d'), business_days)
                return f"{date_str}\n({DateFormatter.get_base_description(field_type)} + {business_days} ימי עסקים: {target_date_str})"

            # הארכה רגילה בימים
            elif extension_value > 0:
                base_date = DateFormatter.calculate_base_date_by_type(original_date, field_type)
                final_target = original_date + timedelta(days=extension_value)

                base_days = (base_date - original_date).days
                extension_days = extension_value - base_days

                if extension_days > 0:
                    return f"{date_str}\n({DateFormatter.get_base_description(field_type)} + {extension_days} ימים: {final_target.strftime('%Y-%m-%d')})"
                else:
                    return f"{date_str}\n({DateFormatter.get_base_description(field_type)}: {final_target.strftime('%Y-%m-%d')})"

            # אין הארכה
            else:
                return DateFormatter.format_base_date_by_type(date_str, field_type)

        except Exception as e:
            print(f"שגיאה בעיצוב תאריך: {e}")
            return date_str

    @staticmethod
    def calculate_base_date_by_type(original_date, field_type):
        """חישוב תאריך בסיסי לפי סוג השדה"""
        if field_type == 'opening':
            business_target = DateFormatter.calculate_business_days(original_date.strftime('%Y-%m-%d'), 45)
            return datetime.strptime(business_target, '%Y-%m-%d') if business_target else original_date + timedelta(
                days=180)
        elif field_type in ['info', 'committee']:
            return original_date + timedelta(days=730)
        elif field_type == 'permit':
            return original_date + timedelta(days=1095)
        else:
            return original_date + timedelta(days=180)

    @staticmethod
    def format_base_date_by_type(date_str, field_type):
        """עיצוב תאריך בסיסי ללא הארכה"""
        if not date_str:
            return ""

        try:
            original_date = datetime.strptime(date_str, '%Y-%m-%d')
            base_date = DateFormatter.calculate_base_date_by_type(original_date, field_type)

            if field_type == 'opening':
                business_target = DateFormatter.calculate_business_days(date_str, 45)
                return f"{date_str}\n(45 ימי עסקים: {business_target})"
            elif field_type in ['info', 'committee']:
                return f"{date_str}\n(2 שנים: {base_date.strftime('%Y-%m-%d')})"
            elif field_type == 'permit':
                return f"{date_str}\n(3 שנים: {base_date.strftime('%Y-%m-%d')})"
            else:
                return date_str

        except Exception as e:
            print(f"שגיאה בעיצוב תאריך בסיסי: {e}")
            return date_str

    @staticmethod
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


class ProjectProcessor:
    """מעבד נתוני פרויקטים"""

    @staticmethod
    def process_project_data(projects):
        """עיבוד נתוני פרויקטים להצגה ברשת"""
        processed_projects = []

        for project in projects:
            try:
                # המרת טאפל לרשימה לשינוי
                project_data = list(project)

                # עיצוב תאריכים עם הארכות
                if project_data[4]:  # date (info date)
                    info_extension = project_data[18] if len(project_data) > 18 and project_data[18] else 0
                    project_data[4] = DateFormatter.format_date_with_extension(project_data[4], info_extension, 'info')

                if project_data[5]:  # opening_date
                    opening_extension = project_data[19] if len(project_data) > 19 and project_data[19] else 0
                    project_data[5] = DateFormatter.format_date_with_extension(project_data[5], opening_extension,
                                                                               'opening')

                if project_data[7]:  # committee_date
                    committee_extension = project_data[21] if len(project_data) > 21 and project_data[21] else 0
                    project_data[7] = DateFormatter.format_date_with_extension(project_data[7], committee_extension,
                                                                               'committee')

                if project_data[8]:  # permit_validity_date
                    permit_extension = project_data[22] if len(project_data) > 22 and project_data[22] else 0
                    project_data[8] = DateFormatter.format_date_with_extension(project_data[8], permit_extension, 'permit')

                # הוספת סטטוס צביעה
                project_data.append(ProjectProcessor.get_project_status(project_data))

                processed_projects.append(project_data)
            except Exception as e:
                print(f"שגיאה בעיבוד פרויקט: {e}")
                continue

        return processed_projects

    @staticmethod
    def get_project_status(project_data):
        """קבלת סטטוס פרויקט לצביעה"""
        try:
            current_stage = project_data[10] if len(project_data) > 10 else ""
            opening_date = project_data[5] if len(project_data) > 5 else ""
            committee_date = project_data[7] if len(project_data) > 7 else ""
            permit_date = project_data[8] if len(project_data) > 8 else ""
            info_date = project_data[4] if len(project_data) > 4 else ""

            # בדיקת עדיפויות צביעה
            if current_stage == "נפתח לפני החלטת ועדה":
                if opening_date and (ProjectProcessor.check_date_approaching_expiry(opening_date, 15) or
                                     ProjectProcessor.check_date_expired(opening_date)):
                    return "approaching"

            if permit_date and ProjectProcessor.check_permit_expired(permit_date):
                return "warning"

            if opening_date and ProjectProcessor.check_date_approaching_expiry(opening_date, 15):
                return "approaching"

            if committee_date and ProjectProcessor.check_committee_date_expiring(committee_date):
                return "committee_expiring"

            if info_date and ProjectProcessor.check_info_date_expiring(info_date):
                return "info_expiring"

            return "normal"
        except Exception as e:
            print(f"שגיאה בקבלת סטטוס פרויקט: {e}")
            return "normal"

    @staticmethod
    def check_date_approaching_expiry(date_str, days_before=15):
        """בדיקה אם תאריך מתקרב לפקיעה"""
        try:
            if not date_str:
                return False

            current_date = datetime.now()

            if '\n' in date_str and '(' in date_str:
                lines = date_str.split('\n')
                if len(lines) >= 2:
                    target_line = lines[1].strip()
                    import re
                    date_match = re.search(r':\s*(\d{4}-\d{2}-\d{2})', target_line)
                    if date_match:
                        target_date_str = date_match.group(1)
                        target_date = datetime.strptime(target_date_str, '%Y-%m-%d')

                        if target_date.date() <= current_date.date():
                            return False

                        days_remaining = (target_date.date() - current_date.date()).days
                        return 0 < days_remaining <= days_before

            return False
        except Exception:
            return False

    @staticmethod
    def check_date_expired(date_str):
        """בדיקה אם תאריך פג תוקף"""
        try:
            if not date_str:
                return False

            current_date = datetime.now()

            if '\n' in date_str and '(' in date_str:
                lines = date_str.split('\n')
                if len(lines) >= 2:
                    target_line = lines[1].strip()
                    import re
                    date_match = re.search(r':\s*(\d{4}-\d{2}-\d{2})', target_line)
                    if date_match:
                        target_date_str = date_match.group(1)
                        target_date = datetime.strptime(target_date_str, '%Y-%m-%d')
                        return current_date.date() > target_date.date()

            return False
        except Exception:
            return False

    @staticmethod
    def check_permit_expired(date_str):
        """בדיקה אם היתר פג תוקף"""
        try:
            if not date_str:
                return False

            if '\n' in date_str:
                date_part = date_str.split('\n')[0]
            else:
                date_part = date_str

            date_part = date_part.strip()

            if not date_part or len(date_part) < 8:
                return False

            current_date = datetime.now()
            permit_date = datetime.strptime(date_part, '%Y-%m-%d')
            expiry_date = permit_date + timedelta(days=365)
            return current_date.date() > expiry_date.date()
        except Exception:
            return False

    @staticmethod
    def check_committee_date_expiring(date_str):
        """בדיקה אם תאריך ועדה מתקרב לפקיעה"""
        try:
            if not date_str:
                return False

            current_date = datetime.now()

            if '\n' in date_str and '(' in date_str:
                lines = date_str.split('\n')
                if len(lines) >= 2:
                    target_line = lines[1].strip()
                    import re
                    date_match = re.search(r':\s*(\d{4}-\d{2}-\d{2})', target_line)
                    if date_match:
                        target_date_str = date_match.group(1)
                        target_date = datetime.strptime(target_date_str, '%Y-%m-%d')
                        days_remaining = (target_date - current_date).days
                        return 0 < days_remaining <= 180

            return False
        except Exception:
            return False

    @staticmethod
    def check_info_date_expiring(date_str):
        """בדיקה אם תיק מידע מתקרב לפקיעה"""
        try:
            if not date_str:
                return False

            current_date = datetime.now()

            if '\n' in date_str and '(' in date_str:
                lines = date_str.split('\n')
                if len(lines) >= 2:
                    target_line = lines[1].strip()
                    import re
                    date_match = re.search(r':\s*(\d{4}-\d{2}-\d{2})', target_line)
                    if date_match:
                        target_date_str = date_match.group(1)
                        target_date = datetime.strptime(target_date_str, '%Y-%m-%d')
                        days_remaining = (target_date - current_date).days
                        return days_remaining <= 120

            return False
        except Exception:
            return False


# נתיבי האפליקציה
@app.route('/')
def index():
    """עמוד ראשי"""
    return render_template('index.html')


@app.route('/api/projects')
def get_projects():
    """API לקבלת פרויקטים"""
    try:
        stage = request.args.get('stage', 'הכל')
        search = request.args.get('search', '')

        if search:
            projects = DatabaseManager.search_projects(search)
        else:
            projects = DatabaseManager.get_projects_by_stage(stage)

        processed_projects = ProjectProcessor.process_project_data(projects)

        return jsonify({
            'success': True,
            'projects': processed_projects,
            'count': len(processed_projects)
        })
    except Exception as e:
        print(f"שגיאה ב-API פרויקטים: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/team-leaders')
def get_team_leaders():
    """API לקבלת ראשי צוותים"""
    try:
        leaders = DatabaseManager.get_team_leaders()
        return jsonify({
            'success': True,
            'team_leaders': leaders
        })
    except Exception as e:
        print(f"שגיאה ב-API ראשי צוותים: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/city-teams')
def get_city_teams():
    """API לקבלת צוותי עירייה"""
    try:
        teams = DatabaseManager.get_city_teams()
        return jsonify({
            'success': True,
            'city_teams': teams
        })
    except Exception as e:
        print(f"שגיאה ב-API צוותי עירייה: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/projects/team-leader/<team_leader>')
def get_projects_by_team_leader(team_leader):
    """API לקבלת פרויקטים לפי ראש צוות"""
    try:
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                id, project_name, request_number, info_file_number,
                date, opening_date, status_date, committee_date, permit_validity_date, 
                team_leader, stage, request_types, engineer, management_company, 
                entrepreneur_name, architect, city, notes,
                info_date_extension, opening_date_extension, status_date_extension,
                committee_date_extension, permit_validity_date_extension, city_team
            FROM projects
            WHERE team_leader = ?
            ORDER BY project_name
        """, (team_leader,))

        projects = cursor.fetchall()
        conn.close()

        processed_projects = ProjectProcessor.process_project_data(projects)

        return jsonify({
            'success': True,
            'projects': processed_projects,
            'count': len(processed_projects)
        })
    except Exception as e:
        print(f"שגיאה בפרויקטים לפי ראש צוות: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/projects/city-team/<city_team>')
def get_projects_by_city_team(city_team):
    """API לקבלת פרויקטים לפי צוות עירייה"""
    try:
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()

        # שלב 1: קבלת בודקים בצוות
        cursor.execute("""
            SELECT DISTINCT engineer 
            FROM projects 
            WHERE city_team = ? AND engineer IS NOT NULL AND engineer != '' 
            AND stage IN ('נפתח לפני החלטת ועדה', 'בדיקה סופית')
            ORDER BY engineer
        """, (city_team,))

        inspectors = [row[0] for row in cursor.fetchall()]

        # שלב 2: קבלת פרויקטים לכל בודק
        result = {}
        for inspector in inspectors:
            cursor.execute("""
                SELECT 
                    id, project_name, request_number, opening_date, committee_date,
                    team_leader, request_types, engineer, management_company, 
                    architect, notes, stage
                FROM projects
                WHERE city_team = ? AND engineer = ? AND stage IN ('נפתח לפני החלטת ועדה', 'בדיקה סופית')
                ORDER BY 
                    CASE 
                        WHEN stage = 'נפתח לפני החלטת ועדה' THEN 0
                        WHEN stage = 'בדיקה סופית' THEN 1
                        ELSE 2
                    END,
                    opening_date,
                    project_name
            """, (city_team, inspector))

            projects = cursor.fetchall()
            result[inspector] = projects

        conn.close()

        return jsonify({
            'success': True,
            'inspectors': result
        })
    except Exception as e:
        print(f"שגיאה בפרויקטים לפי צוות עירייה: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/export/excel')
def export_excel():
    """ייצוא לאקסל"""
    try:
        stage = request.args.get('stage', 'הכל')
        projects = DatabaseManager.get_projects_by_stage(stage)

        # יצירת DataFrame
        columns = [
            'שם הפרויקט', 'מס בקשה', 'מספר תיק מידע',
            'תאריך קבלת תיק מידע', 'תאריך פתיחת בקשה',
            'תאריך סטטוס רישוי', 'תאריך החלטת ועדה',
            'תאריך תוקף היתר', 'שלב רישוי', 'מהות הבקשה',
            'מהנדס רישוי אחראי', 'חברת ניהול', 'שם היזם',
            'אדריכל אחראי', 'ראש צוות', 'עיר', 'הערות'
        ]

        # המרת נתונים לפורמט המתאים לאקסל
        excel_data = []
        for project in projects:
            row = list(project[1:18])  # דילוג על ID ולקיחת העמודות הרלוונטיות
            excel_data.append(row)

        df = pd.DataFrame(excel_data, columns=columns)

        # יצירת קובץ זמני
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        df.to_excel(temp_file.name, index=False, engine='openpyxl')

        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=f'פרויקטים_{stage}_{datetime.now().strftime("%Y-%m-%d")}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        print(f"שגיאה בייצוא לאקסל: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Health check endpoint for Render
@app.route('/health')
def health_check():
    """בדיקת תקינות השרת"""
    try:
        # בדיקה שמסד הנתונים זמין
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM projects")
        count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'projects_count': count
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # הכנת מסד הנתונים
    init_database()
    
    # קבלת פורט מהסביבה (Render משתמש בזה)
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    # הפעלת השרת
    app.run(debug=False, host=host, port=port)
