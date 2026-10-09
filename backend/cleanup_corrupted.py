#!/usr/bin/env python3
"""Clean up corrupted student records."""

from database import get_connection

conn = get_connection()
cursor = conn.cursor()

print("\nCleaning up corrupted records...")

# Delete corrupted Kent, Avril, and Archie
delete_ids = ['S001', 'S002', 'S003']
for student_id in delete_ids:
    try:
        cursor.execute("DELETE FROM parent_notifications WHERE student_id=%s", (student_id,))
        cursor.execute("DELETE FROM campus_logs WHERE student_id=%s", (student_id,))
        cursor.execute("DELETE FROM students WHERE student_id=%s", (student_id,))
        print(f"  [OK] Deleted student {student_id}")
    except Exception as e:
        print(f"  [ERROR] Could not delete {student_id}: {e}")

conn.commit()
conn.close()

print("\nDone! Now you can register fresh students with proper photos.\n")
