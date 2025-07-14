#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
סקריפט להמרת נתוני מערכת הרישוי מ-SQLite ל-JSON
מיועד לשימוש עם המערכת הסטטית ב-HTML
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
import sys

def connect_to_database(db_path):
    """חיבור למסד הנתונים"""
    try:
        conn = sqlite3.connect(db_path)
        print(f"✅ התחברתי בהצלחה למסד הנתונים: {db_path}")
        return conn
    except sqlite3.Error as e:
        print(f"❌ שגיאה בחיבור למסד הנתונים: {e}")
        return None

def get_projects_from_db(conn):
    """שליפת כל הפרויקטים ממסד הנתונים"""
    try:
        cursor = conn.cursor()
        
        # שליפת כל הנתונים מטבלת הפרויקטים
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
        
        # קבלת שמות העמודות
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        print(f"✅ נמצאו {len(rows)} פרויקטים במסד הנתונים")
        
        return columns, rows
        
    except sqlite3.Error as e:
        print(f"❌ שגיאה בשליפת נתונים: {e}")
        return [], []

def calculate_project_status(project_data):
    """חישוב סטטוס פרויקט לצביעה"""
    try:
        stage = project_data.get('stage', '') or ''
        opening_date = project_data.get('opening_date', '') or ''
        committee_date = project_data.get('committee_date', '') or ''
        permit_date = project_data.get('permit_validity_date', '') or ''
        info_date = project_data.get('date', '') or ''
        
        # לוגיקה פשוטה לקביעת סטטוס
        if stage == "נפתח לפני החלטת ועדה":
            if opening_date and is_date_approaching_expiry(opening_date, 15):
                return 'approaching'
        
        if permit_date and is_permit_expired(permit_date):
            return 'warning'
            
        if opening_date and is_date_approaching_expiry(opening_date, 15):
            return 'approaching'
            
        if committee_date and is_committee_date_expiring(committee_date):
            return 'committee_expiring'
            
        if info_date and is_info_date_expiring(info_date):
            return 'info_expiring'
            
        return 'normal'
        
    except Exception as e:
        print(f"⚠️ שגיאה בחישוב סטטוס פרויקט: {e}")
        return 'normal'

def is_date_approaching_expiry(date_str, days_before=15):
    """בדיקה אם תאריך מתקרב לפקיעה"""
    try:
        if not date_str:
            return False
            
        # ניסיון לפרסר תאריך במספר פורמטים
        date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
        target_date = None
        
        for fmt in date_formats:
            try:
                target_date = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue
                
        if not target_date:
            return False
            
        current_date = datetime.now()
        
        # חישוב 45 ימי עסקים (בערך 65 ימים רגילים)
        business_target = target_date + timedelta(days=65)
        
        if business_target.date() <= current_date.date():
            return False
            
        days_remaining = (business_target.date() - current_date.date()).days
        return 0 < days_remaining <= days_before
        
    except Exception:
        return False

def is_permit_expired(date_str):
    """בדיקה אם היתר פג תוקף (שנה אחרי הנפקה)"""
    try:
        if not date_str:
            return False
            
        date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
        permit_date = None
        
        for fmt in date_formats:
            try:
                permit_date = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue
                
        if not permit_date:
            return False
            
        current_date = datetime.now()
        expiry_date = permit_date + timedelta(days=365)
        return current_date.date() > expiry_date.date()
        
    except Exception:
        return False

def is_committee_date_expiring(date_str):
    """בדיקה אם תאריך ועדה מתקרב לפקיעה (2 שנים)"""
    try:
        if not date_str:
            return False
            
        date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
        committee_date = None
        
        for fmt in date_formats:
            try:
                committee_date = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue
                
        if not committee_date:
            return False
            
        current_date = datetime.now()
        target_date = committee_date + timedelta(days=730)  # 2 שנים
        days_remaining = (target_date - current_date).days
        return 0 < days_remaining <= 180  # 6 חודשים לפני פקיעה
        
    except Exception:
        return False

def is_info_date_expiring(date_str):
    """בדיקה אם תיק מידע מתקרב לפקיעה (2 שנים)"""
    try:
        if not date_str:
            return False
            
        date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
        info_date = None
        
        for fmt in date_formats:
            try:
                info_date = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue
                
        if not info_date:
            return False
            
        current_date = datetime.now()
        target_date = info_date + timedelta(days=730)  # 2 שנים
        days_remaining = (target_date - current_date).days
        return days_remaining <= 120  # 4 חודשים לפני פקיעה
        
    except Exception:
        return False

def convert_to_json_format(columns, rows):
    """המרת הנתונים לפורמט JSON"""
    projects = []
    
    for row in rows:
        # יצירת מילון עבור כל פרויקט
        project = {}
        for i, column in enumerate(columns):
            value = row[i] if i < len(row) else None
            # המרת None ל-string ריק לנוחות הצגה
            project[column] = value if value is not None else ""
        
        # הוספת סטטוס מחושב
        project['status'] = calculate_project_status(project)
        
        projects.append(project)
    
    return {
        "metadata": {
            "export_date": datetime.now().isoformat(),
            "total_projects": len(projects),
            "source": "licensing_system.db"
        },
        "projects": projects
    }

def create_data_directory():
    """יצירת תיקיית data אם לא קיימת"""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"✅ נוצרה תיקייה: {data_dir}")
    return data_dir

def save_json_file(data, output_path):
    """שמירת הקובץ JSON"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        file_size = os.path.getsize(output_path)
        print(f"✅ הקובץ נשמר בהצלחה: {output_path}")
        print(f"📁 גודל הקובץ: {file_size:,} בתים")
        return True
        
    except Exception as e:
        print(f"❌ שגיאה בשמירת הקובץ: {e}")
        return False

def create_csv_backup(data, data_dir):
    """יצירת גיבוי CSV נוסף"""
    try:
        import csv
        
        csv_path = os.path.join(data_dir, "projects.csv")
        projects = data.get('projects', [])
        
        if not projects:
            return
            
        # כותרות העמודות
        headers = [
            'שם הפרויקט', 'מס בקשה', 'מספר תיק מידע', 'תאריך קבלת תיק מידע',
            'תאריך פתיחת בקשה', 'תאריך סטטוס רישוי', 'תאריך החלטת ועדה',
            'תאריך תוקף היתר', 'ראש צוות', 'שלב רישוי', 'מהות הבקשה',
            'מהנדס רישוי אחראי', 'חברת ניהול', 'שם היזם', 'אדריכל אחראי',
            'עיר', 'הערות', 'צוות עירייה'
        ]
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            
            for project in projects:
                row = [
                    project.get('project_name', ''),
                    project.get('request_number', ''),
                    project.get('info_file_number', ''),
                    project.get('date', ''),
                    project.get('opening_date', ''),
                    project.get('status_date', ''),
                    project.get('committee_date', ''),
                    project.get('permit_validity_date', ''),
                    project.get('team_leader', ''),
                    project.get('stage', ''),
                    project.get('request_types', ''),
                    project.get('engineer', ''),
                    project.get('management_company', ''),
                    project.get('entrepreneur_name', ''),
                    project.get('architect', ''),
                    project.get('city', ''),
                    project.get('notes', ''),
                    project.get('city_team', '')
                ]
                writer.writerow(row)
        
        print(f"✅ נוצר גם קובץ CSV: {csv_path}")
        
    except Exception as e:
        print(f"⚠️ שגיאה ביצירת קובץ CSV: {e}")

def print_statistics(data):
    """הדפסת סטטיסטיקות על הנתונים"""
    projects = data.get('projects', [])
    total = len(projects)
    
    if total == 0:
        print("⚠️ לא נמצאו פרויקטים")
        return
    
    # ספירת פרויקטים לפי שלב
    stages = {}
    statuses = {}
    
    for project in projects:
        stage = project.get('stage', 'לא מוגדר')
        status = project.get('status', 'normal')
        
        stages[stage] = stages.get(stage, 0) + 1
        statuses[status] = statuses.get(status, 0) + 1
    
    print("\n📊 סטטיסטיקות:")
    print(f"   סה\"כ פרויקטים: {total}")
    print("\n📈 פילוח לפי שלבים:")
    for stage, count in sorted(stages.items()):
        print(f"   • {stage}: {count}")
    
    print("\n🎯 פילוח לפי סטטוס:")
    status_names = {
        'normal': 'רגיל',
        'approaching': 'דחוף',
        'warning': 'אזהרה',
        'committee_expiring': 'ועדה פגה',
        'info_expiring': 'מידע פג'
    }
    
    for status, count in sorted(statuses.items()):
        status_name = status_names.get(status, status)
        print(f"   • {status_name}: {count}")

def main():
    """פונקציה ראשית"""
    print("🚀 התחלת המרת נתוני מערכת הרישוי\n")
    
    # בדיקת קיום קובץ מסד הנתונים
    db_path = "licensing_system.db"
    if not os.path.exists(db_path):
        print(f"❌ קובץ מסד הנתונים לא נמצא: {db_path}")
        print("   ודא שהקובץ נמצא באותה תיקייה כמו הסקריפט הזה")
        sys.exit(1)
    
    # חיבור למסד הנתונים
    conn = connect_to_database(db_path)
    if not conn:
        sys.exit(1)
    
    try:
        # שליפת נתונים
        columns, rows = get_projects_from_db(conn)
        if not rows:
            print("❌ לא נמצאו נתונים במסד הנתונים")
            sys.exit(1)
        
        # המרה לפורמט JSON
        print("🔄 ממיר נתונים לפורמט JSON...")
        json_data = convert_to_json_format(columns, rows)
        
        # יצירת תיקיית נתונים
        data_dir = create_data_directory()
        
        # שמירת קובץ JSON
        json_path = os.path.join(data_dir, "projects.json")
        if save_json_file(json_data, json_path):
            # יצירת גיבוי CSV
            create_csv_backup(json_data, data_dir)
            
            # הדפסת סטטיסטיקות
            print_statistics(json_data)
            
            print(f"\n🎉 ההמרה הושלמה בהצלחה!")
            print(f"📄 קובץ JSON: {json_path}")
            print(f"📄 קובץ CSV: {os.path.join(data_dir, 'projects.csv')}")
            print("\n📋 הוראות שימוש:")
            print("   1. העלה את התיקייה 'data' לגיט")
            print("   2. העלה את קובץ index.html לגיט")
            print("   3. הפעל את האתר (GitHub Pages / Netlify / Vercel)")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
