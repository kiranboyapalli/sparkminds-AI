import requests

base = 'https://sparkminds-ai.up.railway.app'
print('1. Checking unauthenticated session:')
r1 = requests.get(f'{base}/api/auth/session')
print(f'Status: {r1.status_code}')
assert r1.status_code == 401

print('2. Registering live test student:')
reg = {
    'student_id': 'stu_live_prod_test_2',
    'full_name': 'Live Student',
    'age': 13,
    'grade': 8,
    'school_board': 'CBSE',
    'date_of_birth': '2013-05-20',
    'password_or_pin': 'SecurePass2026',
    'device_name': 'Live Tester Laptop'
}
r2 = requests.post(f'{base}/api/auth/register', json=reg)
stu_data = r2.json().get('student', {})
print(f'Status: {r2.status_code}, Student Age: {stu_data.get("age")}')
assert r2.status_code == 200 and stu_data.get('age') == 13
token = r2.json()['session_token']

print('3. Patching age to 16 with date of birth:')
r3 = requests.patch(
    f'{base}/api/students/stu_live_prod_test_2/profile',
    json={'age': 16, 'date_of_birth': '2010-05-20'},
    headers={'X-SparkMinds-Token': token}
)
updated_stu = r3.json().get('student', {})
print(f'Status: {r3.status_code}, Updated Student Age: {updated_stu.get("age")}, DOB: {updated_stu.get("date_of_birth")}')
assert r3.status_code == 200 and updated_stu.get('age') == 16
assert updated_stu.get('date_of_birth') == '2010-05-20'

print('4. Signing in from simulated second device (Tablet):')
r4 = requests.post(
    f'{base}/api/auth/login',
    json={'identifier': 'stu_live_prod_test_2', 'password_or_pin': 'SecurePass2026', 'device_name': 'Tablet'}
)
bundle = r4.json().get('cloud_sync_bundle', {})
bundle_stu = bundle.get('student', {})
print(f'Status: {r4.status_code}, Multi-Device Synced Age: {bundle_stu.get("age")}, DOB: {bundle_stu.get("date_of_birth")}')
assert bundle_stu.get('age') == 16
assert bundle_stu.get('date_of_birth') == '2010-05-20'

print('5. Verifying clean HTML from live site:')
r5 = requests.get(f'{base}/')
assert 'sample flashcards' not in r5.text.lower()
print('SUCCESS: All live production tests passed flawlessly on https://sparkminds-ai.up.railway.app!')
