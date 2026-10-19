import sqlite3
from pathlib import Path


# --------------------------------------------------
# DATABASE CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "opportunities.db"


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    return conn


# --------------------------------------------------
# INITIALIZE DATABASE
# --------------------------------------------------

def initialize_database():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                organization TEXT NOT NULL,
                description TEXT NOT NULL,
                eligibility TEXT NOT NULL,
                location TEXT NOT NULL,
                deadline TEXT,
                skills TEXT,
                source_url TEXT NOT NULL,
                last_verified TEXT,
                status TEXT NOT NULL DEFAULT 'PENDING REVIEW'
            )
            """
        )


# --------------------------------------------------
# GET OPPORTUNITIES
# --------------------------------------------------

def get_opportunities(approved_only=False):
    query = "SELECT * FROM opportunities"
    parameters = ()

    if approved_only:
        query += """
            WHERE UPPER(TRIM(status)) IN (
                'APPROVED',
                'DEMO - NOT VERIFIED',
                'DEMO — NOT VERIFIED'
            )
        """

    query += " ORDER BY category, title"

    with get_connection() as conn:
        rows = conn.execute(query, parameters).fetchall()

    return [dict(row) for row in rows]


# --------------------------------------------------
# ADD SAMPLE OPPORTUNITIES
# --------------------------------------------------

def add_sample_opportunities():
    sample_opportunities = [
        {
            "title": "Python Programming Practice",
            "category": "Free Course",
            "organization": "Example Learning Platform",
            "description": (
                "A demonstration listing for learning Python "
                "programming fundamentals."
            ),
            "eligibility": "Beginners",
            "location": "Online",
            "deadline": "",
            "skills": "Python, Programming",
            "source_url": "https://www.python.org/",
            "status": "DEMO - NOT VERIFIED",
        },
        {
            "title": "AWS Cloud Learning Resources",
            "category": "Certification",
            "organization": "Amazon Web Services",
            "description": (
                "A demonstration listing for exploring AWS "
                "cloud learning resources."
            ),
            "eligibility": "Students and beginners",
            "location": "Online",
            "deadline": "",
            "skills": "AWS, Cloud Computing",
            "source_url": "https://aws.amazon.com/training/",
            "status": "DEMO - NOT VERIFIED",
        },
        {
            "title": "Python Developer Practice",
            "category": "Internship",
            "organization": "Example Organization",
            "description": (
                "A demonstration internship listing for practicing "
                "Python development skills."
            ),
            "eligibility": "Students with basic Python knowledge",
            "location": "Online",
            "deadline": "",
            "skills": "Python, SQL, Problem Solving",
            "source_url": "https://www.python.org/",
            "status": "DEMO - NOT VERIFIED",
        },
    ]

    with get_connection() as conn:
        for item in sample_opportunities:
            existing = conn.execute(
                """
                SELECT id
                FROM opportunities
                WHERE title = ?
                  AND organization = ?
                """,
                (item["title"], item["organization"]),
            ).fetchone()

            if existing is None:
                conn.execute(
                    """
                    INSERT INTO opportunities (
                        title,
                        category,
                        organization,
                        description,
                        eligibility,
                        location,
                        deadline,
                        skills,
                        source_url,
                        last_verified,
                        status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        item["title"],
                        item["category"],
                        item["organization"],
                        item["description"],
                        item["eligibility"],
                        item["location"],
                        item["deadline"],
                        item["skills"],
                        item["source_url"],
                        None,
                        item["status"],
                    ),
                )


# --------------------------------------------------
# ADD A NEW OPPORTUNITY
# --------------------------------------------------

def add_opportunity(item):
    required_fields = [
        "title",
        "category",
        "organization",
        "description",
        "eligibility",
        "location",
        "source_url",
        "status",
    ]

    for field in required_fields:
        if not str(item.get(field) or "").strip():
            raise ValueError(f"{field} is required.")

    allowed_categories = {
        "Internship",
        "Scholarship",
        "Free Course",
        "Certification",
        "Fresher Job",
    }

    if item["category"] not in allowed_categories:
        raise ValueError("Invalid opportunity category.")

    source_url = item["source_url"].strip()

    if not source_url.startswith(("https://", "http://")):
        raise ValueError(
            "Source URL must start with http:// or https://."
        )

    if item["status"] != "PENDING REVIEW":
        raise ValueError(
            "New submissions must have PENDING REVIEW status."
        )

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO opportunities (
                title,
                category,
                organization,
                description,
                eligibility,
                location,
                deadline,
                skills,
                source_url,
                last_verified,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item["title"].strip(),
                item["category"],
                item["organization"].strip(),
                item["description"].strip(),
                item["eligibility"].strip(),
                item["location"].strip(),
                item.get("deadline", "").strip(),
                item.get("skills", "").strip(),
                source_url,
                None,
                "PENDING REVIEW",
            ),
        )

        return cursor.lastrowid


# --------------------------------------------------
# APPROVE OR REJECT A SUBMISSION
# --------------------------------------------------

def update_opportunity_status(opportunity_id, new_status):
    allowed_statuses = {"APPROVED", "REJECTED"}

    if new_status not in allowed_statuses:
        raise ValueError("Invalid opportunity status.")

    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE opportunities
            SET status = ?
            WHERE id = ?
              AND UPPER(TRIM(status)) = 'PENDING REVIEW'
            """,
            (new_status, opportunity_id),
        )

        return cursor.rowcount > 0
def get_dashboard_stats():
    with get_connection() as conn:
        total = conn.execute(
            "SELECT COUNT(*) FROM opportunities"
        ).fetchone()[0]

        approved = conn.execute(
            """
            SELECT COUNT(*)
            FROM opportunities
            WHERE UPPER(TRIM(status)) = 'APPROVED'
            """
        ).fetchone()[0]

        pending = conn.execute(
            """
            SELECT COUNT(*)
            FROM opportunities
            WHERE UPPER(TRIM(status)) = 'PENDING REVIEW'
            """
        ).fetchone()[0]

        rejected = conn.execute(
            """
            SELECT COUNT(*)
            FROM opportunities
            WHERE UPPER(TRIM(status)) = 'REJECTED'
            """
        ).fetchone()[0]

    return {
        "total": total,
        "approved": approved,
        "pending": pending,
        "rejected": rejected,
    }


def get_category_counts():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT category, COUNT(*) AS total
            FROM opportunities
            GROUP BY category
            ORDER BY total DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]