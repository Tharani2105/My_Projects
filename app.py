from flask import Flask, request, redirect, url_for, render_template_string
import mysql.connector
import datetime

app = Flask(__name__)

# ---------------- DATABASE CONFIG ----------------
DB_CONFIG = {
    'host': 'localhost',
    'database': 'Hospital',
    'user': 'root',
    'password': 'tharani'
}

# ---------------- DB CONNECTION ----------------
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# ---------------- HOME / DASHBOARD ----------------
@app.route('/')
def home():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM patients")
    patients_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM doctors")
    doctors_count = cur.fetchone()[0]

    today = datetime.date.today()
    cur.execute("SELECT COUNT(*) FROM appointments WHERE DATE(appointment_date) = %s", (today,))
    appointments_today = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM patients WHERE discharge_date = %s", (today,))
    discharges_today = cur.fetchone()[0]
    conn.close()

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Hospital Dashboard</title>
<style>
body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background:#eef2f7; margin:0; padding:0 20px; }
header { background:#007bff; color:white; padding:15px 20px; border-radius:8px; margin-bottom:20px; }
header h1 { margin:0 0 10px 0; }
nav a { margin-right:15px; color:white; text-decoration:none; font-weight:bold; }
nav a:hover { text-decoration:underline; }
.dashboard-cards { display:flex; flex-wrap:wrap; gap:20px; margin-top:20px; }
.card { flex:1 1 200px; background:#fff; border-radius:10px; padding:20px; text-align:center; box-shadow:0 4px 8px rgba(0,0,0,0.1); transition:transform 0.2s; }
.card:hover { transform:translateY(-5px); }
.card h3 { margin:0 0 10px 0; font-size:1.2em; }
.card p { font-size:2em; font-weight:bold; }
.patients { background:#ffadad; color:#800000; }
.doctors { background:#ffd6a5; color:#805000; }
.appointments { background:#caffbf; color:#006400; }
.discharges { background:#9bf6ff; color:#004d80; }
</style>
</head>
<body>
<header>
<h1>🏥 Hospital Management System</h1>
<nav>
<a href="{{ url_for('home') }}">Home</a>
<a href="{{ url_for('view_patients') }}">Patients</a>
<a href="{{ url_for('view_doctors') }}">Doctors</a>
<a href="{{ url_for('view_appointments') }}">Appointments</a>
<a href="{{ url_for('discharge') }}">Discharge</a>
<a href="{{ url_for('emergency') }}">Emergency</a>
</nav>
</header>

<h2>🏥 Dashboard</h2>
<div class="dashboard-cards">
    <div class="card patients"><h3>Patients</h3><p>{{patients_count}}</p></div>
    <div class="card doctors"><h3>Doctors</h3><p>{{doctors_count}}</p></div>
    <div class="card appointments"><h3>Appointments Today</h3><p>{{appointments_today}}</p></div>
    <div class="card discharges"><h3>Discharges Today</h3><p>{{discharges_today}}</p></div>
</div>
</body>
</html>
""", patients_count=patients_count, doctors_count=doctors_count,
       appointments_today=appointments_today, discharges_today=discharges_today)

# ---------------- PATIENTS ----------------
@app.route('/patients')
def view_patients():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patients")
    patients = cur.fetchall()
    conn.close()
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Patients</title>
<style>
body{font-family:Arial; background:#eef2f7; margin:0; padding:20px;}
table{width:100%; border-collapse:collapse; background:white;}
th,td{padding:10px; border:1px solid #ddd; text-align:left;}
th{background:#007bff; color:white;}
a{color:#007bff; text-decoration:none;}
a:hover{text-decoration:underline;}
button{padding:6px 12px; border:none; background:#28a745; color:white; cursor:pointer; border-radius:5px;}
button:hover{background:#218838;}
</style>
<script>
function confirmDelete(name){return confirm('Delete '+name+'?');}
function confirmAdd(){return confirm('Add this record?');}
</script>
</head>
<body>
<h2>Patients</h2>
<a href="{{ url_for('add_patient') }}"><button>Add Patient</button></a>
<table>
<tr><th>ID</th><th>Name</th><th>Age</th><th>Gender</th><th>Phone</th><th>Address</th><th>Discharge</th><th>Action</th></tr>
{% for p in patients %}
<tr>
<td>{{p[0]}}</td><td>{{p[1]}}</td><td>{{p[2]}}</td><td>{{p[3]}}</td>
<td>{{p[4]}}</td><td>{{p[5]}}</td><td>{{p[6]}}</td>
<td><a href="{{ url_for('delete_patient', pid=p[0]) }}" onclick="return confirmDelete('{{p[1]}}')">Delete</a></td>
</tr>
{% endfor %}
</table>
<a href="{{ url_for('home') }}">Back</a>
</body>
</html>
""", patients=patients)

@app.route('/add-patient', methods=['GET','POST'])
def add_patient():
    if request.method=='POST':
        d=request.form
        discharge=d['discharge'] or None
        conn=get_connection()
        cur=conn.cursor()
        cur.execute("INSERT INTO patients (name,age,gender,phone,address,discharge_date) VALUES (%s,%s,%s,%s,%s,%s)",
                    (d['name'],d['age'],d['gender'],d['phone'],d['address'],discharge))
        conn.commit()
        conn.close()
        return redirect(url_for('view_patients'))
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Add Patient</title>
<style>
body{font-family:Arial; background:#eef2f7; padding:20px;}
input,button{margin:5px 0; padding:5px;}
button{background:#28a745; color:white; border:none; border-radius:5px; cursor:pointer;}
button:hover{background:#218838;}
</style>
<script>function confirmAdd(){return confirm('Add this patient?');}</script>
</head>
<body>
<h2>Add Patient</h2>
<form method="post" onsubmit="return confirmAdd()">
Name: <input name="name" required><br>
Age: <input name="age" type="number" required><br>
Gender: <input name="gender" required><br>
Phone: <input name="phone" required><br>
Address: <input name="address" required><br>
Discharge Date: <input type="date" name="discharge"><br>
<button type="submit">Add Patient</button>
</form>
<a href="{{ url_for('view_patients') }}">Back</a>
</body>
</html>
""")

@app.route('/delete-patient/<int:pid>')
def delete_patient(pid):
    conn=get_connection()
    cur=conn.cursor()
    cur.execute("DELETE FROM patients WHERE pat_id=%s",(pid,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_patients'))

# ---------------- DOCTORS ----------------
@app.route('/doctors')
def view_doctors():
    conn=get_connection()
    cur=conn.cursor()
    cur.execute("SELECT * FROM doctors")
    doctors=cur.fetchall()
    conn.close()
    return render_template_string("""
<!DOCTYPE html>
<html>
<head><title>Doctors</title>
<style>body{font-family:Arial;background:#eef2f7;padding:20px;}table{width:100%;border-collapse:collapse;background:white;}th,td{padding:10px;border:1px solid #ddd;}th{background:#007bff;color:white;}button{padding:6px 12px;border:none;background:#28a745;color:white;cursor:pointer;border-radius:5px;}button:hover{background:#218838;}</style></head>
<body>
<h2>Doctors</h2>
<a href="{{ url_for('add_doctor') }}"><button>Add Doctor</button></a>
<table>
<tr><th>ID</th><th>Name</th><th>Specialization</th><th>Phone</th><th>Email</th></tr>
{% for d in doctors %}
<tr>
<td>{{d[0]}}</td><td>{{d[1]}}</td><td>{{d[2]}}</td><td>{{d[3]}}</td><td>{{d[4]}}</td>
</tr>
{% endfor %}
</table>
<a href="{{ url_for('home') }}">Back</a>
</body>
</html>
""", doctors=doctors)

@app.route('/add-doctor', methods=['GET','POST'])
def add_doctor():
    if request.method=='POST':
        d=request.form
        conn=get_connection()
        cur=conn.cursor()
        cur.execute("INSERT INTO doctors (name,specialization,phone,email) VALUES (%s,%s,%s,%s)",
                    (d['name'],d['spec'],d['phone'],d['email']))
        conn.commit()
        conn.close()
        return redirect(url_for('view_doctors'))
    return render_template_string("""
<!DOCTYPE html>
<html>
<head><title>Add Doctor</title>
<style>body{font-family:Arial;background:#eef2f7;padding:20px;}input,button{margin:5px 0;padding:5px;}button{background:#28a745;color:white;border:none;border-radius:5px;cursor:pointer;}button:hover{background:#218838;}</style>
<script>function confirmAdd(){return confirm('Add this doctor?');}</script>
</head>
<body>
<h2>Add Doctor</h2>
<form method="post" onsubmit="return confirmAdd()">
Name: <input name="name" required><br>
Specialization: <input name="spec" required><br>
Phone: <input name="phone" required><br>
Email: <input name="email" type="email" required><br>
<button type="submit">Add Doctor</button>
</form>
<a href="{{ url_for('view_doctors') }}">Back</a>
</body>
</html>
""")

# ---------------- APPOINTMENTS ----------------
@app.route('/appointments')
def view_appointments():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.appt_id, p.name, d.name, a.appointment_date, a.reason
        FROM appointments a
        JOIN patients p ON a.pat_id = p.pat_id
        JOIN doctors d ON a.doc_id = d.doc_id
    """)
    appts = cur.fetchall()
    conn.close()
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Appointments</title>
<style>
body{font-family:Arial;background:#eef2f7;padding:20px;}
table{width:100%;border-collapse:collapse;background:white;}
th,td{padding:10px;border:1px solid #ddd;}
th{background:#007bff;color:white;}
button{padding:6px 12px;border:none;background:#28a745;color:white;cursor:pointer;border-radius:5px;}
button:hover{background:#218838;}
</style>
</head>
<body>
<h2>Appointments</h2>
<a href="{{ url_for('add_appointment') }}"><button>Add Appointment</button></a>
<table>
<tr><th>ID</th><th>Patient</th><th>Doctor</th><th>Date & Time</th><th>Reason</th></tr>
{% for a in appts %}
<tr>
<td>{{a[0]}}</td><td>{{a[1]}}</td><td>{{a[2]}}</td><td>{{a[3]}}</td><td>{{a[4]}}</td>
</tr>
{% endfor %}
</table>
<a href="{{ url_for('home') }}">Back</a>
</body>
</html>
""", appts=appts)

@app.route('/add-appointment', methods=['GET','POST'])
def add_appointment():
    if request.method=='POST':
        d=request.form
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO appointments (pat_id, doc_id, appointment_date, reason)
            VALUES (%s, %s, %s, %s)
        """, (d['pid'], d['did'], d['date'], d['reason']))
        conn.commit()
        conn.close()
        return redirect(url_for('view_appointments'))

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Schedule Appointment</title>
<style>
body{font-family:Arial;background:#eef2f7;padding:20px;}
input,button{margin:5px 0;padding:5px;}
button{background:#28a745;color:white;border:none;border-radius:5px;cursor:pointer;}
button:hover{background:#218838;}
</style>
<script>
function confirmAdd(){return confirm('Schedule this appointment?');}
</script>
</head>
<body>
<h2>Schedule Appointment</h2>
<form method="post" onsubmit="return confirmAdd()">
Patient ID: <input name="pid" type="number" required><br>
Doctor ID: <input name="did" type="number" required><br>
Date & Time: <input type="datetime-local" name="date" required><br>
Reason: <input name="reason" required><br>
<button type="submit">Schedule</button>
</form>
<a href="{{ url_for('view_appointments') }}">Back</a>
</body>
</html>
""")

# ---------------- DISCHARGE ----------------
@app.route('/discharge')
def discharge():
    conn=get_connection()
    cur=conn.cursor()
    cur.execute("""
        SELECT pat_id, name, discharge_date
        FROM patients
        WHERE discharge_date <= CURDATE()
    """)
    rows=cur.fetchall()
    conn.close()
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Patients Due for Discharge</title>
<style>
body{font-family:Arial;background:#eef2f7;padding:20px;}
ul{background:white;padding:10px;list-style:none;}
li{padding:5px;}
</style>
</head>
<body>
<h2>Patients Due for Discharge</h2>
<ul>
{% for r in rows %}
<li>{{r[1]}} - {{r[2]}}</li>
{% endfor %}
</ul>
<a href="{{ url_for('home') }}">Back</a>
</body>
</html>
""", rows=rows)

# ---------------- EMERGENCY ----------------
@app.route('/emergency')
def emergency():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT d.doc_id,d.name,d.specialization
        FROM doctors d
        LEFT JOIN appointments a ON d.doc_id=a.doc_id
        WHERE a.appt_id IS NULL
    """)
    doctors = cur.fetchall()
    conn.close()
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Available Doctors (Emergency)</title>
<style>
body{font-family:Arial;background:#eef2f7;padding:20px;}
ul{background:white;padding:10px;list-style:none;}
li{padding:5px;}
</style>
</head>
<body>
<h2>Available Doctors (Emergency)</h2>
<ul>
{% for d in doctors %}
<li>{{d[1]}} - {{d[2]}}</li>
{% endfor %}
</ul>
<a href="{{ url_for('home') }}">Back</a>
</body>
</html>
""", doctors=doctors)

# ---------------- RUN ----------------
if __name__=="__main__":
    app.run(debug=True)
