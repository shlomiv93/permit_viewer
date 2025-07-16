# מערכת ניהול רישוי - ממשק אינטרנטי

ממשק אינטרנטי מלא לצפייה במערכת ניהול הרישוי, בנוי עם Flask ומותאם לפריסה ב-Render.

## תכונות עיקריות

### 📊 תצוגות מרכזיות
- **כל הפרויקטים** - תצוגה מרכזית של כל הפרויקטים במערכת
- **ראשי צוותים** - קיבוץ פרויקטים לפי ראשי צוותים
- **צוותי עירייה** - תצוגה מיוחדת לפרויקטים בשלבים רלוונטיים לעירייה
- **פרטי פרויקט** - תצוגה מפורטת של פרויקט בודד

### 🎨 עיצוב מתקדם
- עיצוב עתידני ואטרקטיוי עם גרדיאנטים
- תמיכה מלאה בעברית וכיוון RTL
- צביעה דינמית לפי סטטוס התאריכים
- אנימציות חלקות ואפקטי hover
- רספונסיבי למכשירים ניידים

### 🔍 פונקציונליות חיפוש וסינון
- חיפוש טקסט חופשי בכל השדות
- סינון לפי שלבי רישוי
- מיון לפי עמודות שונות
- סינון לפי ראש צוות או צוות עירייה

### 📅 מערכת תאריכים מתקדמת
- חישוב מדויק של ימי עסקים
- תמיכה בהארכות תאריכים
- צביעה אוטומטית לפי סטטוס תאריכים:
  - **ורוד** - תאריך פתיחת בקשה מתקרב לפקיעה
  - **כתום** - תיק מידע מתקרב לפקיעה
  - **צהוב** - תאריך תוקף היתר פג
  - **כחול** - תאריך החלטת ועדה מתקרב לפקיעה

## מבנה הפרויקט

```
licensing-web/
├── app.py                 # אפליקציית Flask הראשית
├── templates/             # תבניות HTML
│   ├── base.html         # תבנית בסיס
│   ├── index.html        # עמוד הבית
│   ├── team_leaders.html # ראשי צוותים
│   ├── city_teams.html   # צוותי עירייה
│   └── project_detail.html # פרטי פרויקט
├── requirements.txt       # תלויות Python
├── render.yaml           # הגדרות Render
├── runtime.txt           # גרסת Python
└── README.md             # תיעוד
```

## התקנה והרצה מקומית

### דרישות מוקדמות
- Python 3.11+
- pip

### שלבי התקנה

1. **שכפול הפרויקט**
```bash
git clone <repository-url>
cd licensing-web
```

2. **יצירת סביבה וירטואלית**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# או
venv\Scripts\activate     # Windows
```

3. **התקנת תלויות**
```bash
pip install -r requirements.txt
```

4. **הרצת האפליקציה**
```bash
python app.py
```

האתר יהיה זמין בכתובת: `http://localhost:5000`

## פריסה ב-Render

### הכנה לפריסה

1. **יצירת repository ב-GitHub** עם כל הקבצים
2. **חיבור ל-Render** והגדרת Web Service חדש
3. **בחירת הגדרות**:
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

### משתני סביבה (אופציונלי)

```
DATABASE_URL=licensing_system.db  # נתיב למסד הנתונים
PORT=5000                         # פורט (Render יגדיר אוטומטית)
```

### הוספת נתונים

הממשק יוצר מסד נתונים ריק אוטומטית. להוספת נתונים:

1. **ייבוא מהמערכת המקורית** - העתק את קובץ `licensing_system.db`
2. **הוספה ידנית** - השתמש בכלי SQLite
3. **API להוספה** - פיתח endpoint להוספת נתונים

## API נוסף

### `/api/stats`
מחזיר נתונים סטטיסטיים בפורמט JSON:
```json
{
  "total_projects": 150,
  "stages_stats": [...],
  "city_teams_stats": [...],
  "team_leaders_stats": [...]
}
```

## טכנולוגיות

- **Backend**: Flask (Python)
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Database**: SQLite
- **Deployment**: Render
- **Icons**: Font Awesome
- **Fonts**: Google Fonts (Rubik)

## תכונות נוספות

### אבטחה
- הגנה מפני SQL Injection
- Sanitization של קלטים
- Headers אבטחה

### ביצועים
- Caching של חישובי תאריכים
- אופטימיזציה של שאילתות SQL
- Lazy loading של תמונות

### נגישות
- תמיכה מלאה ב-RTL
- ניווט במקלדת
- צבעים נגישים
- Alt texts

## פתרון בעיות נפוצות

### בעיית חיבור למסד נתונים
```python
# וודא שהקובץ licensing_system.db קיים
# או שהמשתנה DATABASE_URL מוגדר נכון
```

### בעיית encoding עברית
```python
# וודא שהקובץ נשמר ב-UTF-8
# הגדר charset במסד הנתונים
```

### בעיית performance
```python
# הוסף אינדקסים למסד הנתונים:
# CREATE INDEX idx_stage ON projects(stage);
# CREATE INDEX idx_team_leader ON projects(team_leader);
```

## תמיכה והרחבות

המערכת בנויה בצורה מודולרית ומאפשרת הרחבות קלות:

- הוספת שדות חדשים
- יצירת דוחות נוספים  
- אינטגרציה עם מערכות חיצוניות
- הוספת התראות ואימיילים

## רישיון

פרויקט פנימי לארגון. כל הזכויות שמורות.

---

**פותח במיוחד עבור מערכת ניהול הרישוי**  
גרסה 1.0 - תאריך עדכון אחרון: דצמבר 2024
