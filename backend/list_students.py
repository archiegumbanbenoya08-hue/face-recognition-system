import database

students = database.get_students()
print('Registered students:')
for s in students:
    print(f'  {s["student_id"]}: {s["first_name"]} {s["last_name"]}')