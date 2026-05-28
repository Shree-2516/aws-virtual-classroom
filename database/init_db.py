import os
import sys

# Add parent directory to path to allow importing database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_connection import get_db_connection, load_env

def init_db():
    load_env()
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to MySQL database.")
        return

    cursor = conn.cursor()
    
    # Read schema.sql
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')
    if not os.path.exists(schema_path):
        print(f"schema.sql not found at {schema_path}")
        return

    with open(schema_path, 'r') as f:
        schema_sql = f.read()

    # Split schema by semicolon and execute each statement
    # Filter out empty statements
    statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
    
    # Disable foreign key checks temporarily to drop tables in any order
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    cursor.execute("DROP TABLE IF EXISTS uploads;")
    cursor.execute("DROP TABLE IF EXISTS courses;")
    cursor.execute("DROP TABLE IF EXISTS users;")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    
    print("Dropped old tables.")

    for statement in statements:
        try:
            cursor.execute(statement)
        except Exception as e:
            print(f"Error executing statement:\n{statement}\nError: {e}")
            conn.rollback()
            cursor.close()
            conn.close()
            return

    print("Tables created successfully.")

    # Insert default courses
    default_courses = [
        ("AWS Certified Cloud Practitioner (CLF-C02)", "Learn the fundamentals of AWS Cloud, its core services, security, pricing, and basic architecture."),
        ("AWS Certified Solutions Architect - Associate (SAA-C03)", "Deep dive into designing highly available, cost-effective, and fault-tolerant systems on AWS."),
        ("AWS Certified Developer - Associate (DVA-C02)", "Learn how to develop, deploy, and maintain applications written for the Amazon Web Services platform.")
    ]

    for course_name, description in default_courses:
        try:
            cursor.execute(
                "INSERT INTO courses (course_name, description) VALUES (%s, %s) ON DUPLICATE KEY UPDATE description=%s",
                (course_name, description, description)
            )
        except Exception as e:
            print(f"Error inserting default course '{course_name}': {e}")
    
    print("Inserted default AWS courses.")
    conn.commit()
    cursor.close()
    conn.close()
    print("Database initialization complete!")

if __name__ == "__main__":
    init_db()
