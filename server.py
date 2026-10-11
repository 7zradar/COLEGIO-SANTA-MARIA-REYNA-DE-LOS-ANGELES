"""Piloto académico Santa María. Python 3.10+, sin dependencias externas."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from http.cookies import SimpleCookie
from pathlib import Path
from urllib.parse import urlsplit, unquote
from datetime import datetime, timedelta
from contextlib import contextmanager
import argparse
import hashlib
import hmac
import json
import mimetypes
import os
import re
import secrets
import sqlite3
import threading
import time

ROOT = Path(__file__).resolve().parent
DB = ROOT / "data" / "santamaria.sqlite3"
SESSIONS = {}
ATTEMPTS = {}
LOCK = threading.Lock()


@contextmanager
def connect():
    db = sqlite3.connect(DB, timeout=15)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    try:
        with db:
            yield db
    finally:
        db.close()


def password_hash(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 180000).hex()


def initialize():
    DB.parent.mkdir(exist_ok=True)
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS students(id TEXT PRIMARY KEY, name TEXT NOT NULL, classroom TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1);
        CREATE TABLE IF NOT EXISTS users(username TEXT PRIMARY KEY, name TEXT NOT NULL, role TEXT NOT NULL, student TEXT REFERENCES students(id), salt TEXT NOT NULL, password TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS courses(id TEXT PRIMARY KEY, name TEXT NOT NULL, teacher TEXT NOT NULL, classroom TEXT NOT NULL, color TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS schedule(id INTEGER PRIMARY KEY, course TEXT NOT NULL REFERENCES courses(id), day INTEGER NOT NULL, start TEXT NOT NULL, end TEXT NOT NULL, room TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS grades(student TEXT REFERENCES students(id), course TEXT REFERENCES courses(id), period INTEGER NOT NULL, assessment TEXT NOT NULL, grade REAL NOT NULL CHECK(grade BETWEEN 0 AND 20), updated TEXT NOT NULL, PRIMARY KEY(student,course,period,assessment));
        CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY, course TEXT NOT NULL REFERENCES courses(id), title TEXT NOT NULL, description TEXT NOT NULL, due TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS submissions(task TEXT REFERENCES tasks(id), student TEXT REFERENCES students(id), answer TEXT NOT NULL, updated TEXT NOT NULL, PRIMARY KEY(task,student));
        CREATE TABLE IF NOT EXISTS announcements(id TEXT PRIMARY KEY,title TEXT NOT NULL,body TEXT NOT NULL,audience TEXT NOT NULL,created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS contacts(id TEXT PRIMARY KEY,name TEXT NOT NULL,email TEXT NOT NULL,phone TEXT NOT NULL,topic TEXT NOT NULL,message TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'Pendiente',created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY,actor TEXT NOT NULL,action TEXT NOT NULL,detail TEXT NOT NULL,created TEXT NOT NULL);
        """)
        if db.execute("SELECT count(*) FROM users").fetchone()[0]:
            return
        students = [("E001", "Ana Torres Mendoza", "5.º A · Primaria"), ("E002", "Luis Rojas Vega", "5.º A · Primaria"), ("E003", "Camila Díaz Flores", "1.º A · Secundaria")]
        db.executemany("INSERT INTO students(id,name,classroom) VALUES(?,?,?)", students)
        for username, name, role, student, password in [
            ("admin", "Coordinación académica", "admin", None, "Admin2026!"),
            ("ana", students[0][1], "student", "E001", "Alumno2026!"),
            ("luis", students[1][1], "student", "E002", "Alumno2026!"),
            ("camila", students[2][1], "student", "E003", "Alumno2026!")]:
            salt = secrets.token_hex(16)
            db.execute("INSERT INTO users VALUES(?,?,?,?,?,?)", (username,name,role,student,salt,password_hash(password,salt)))
        courses = [
            ("C01","Matemática","Patricia García","5.º A · Primaria","red"),
            ("C02","Comunicación","Rosa Medina","5.º A · Primaria","blue"),
            ("C03","Ciencia y Tecnología","Jorge Flores","5.º A · Primaria","green"),
            ("C04","Personal Social","Lucía Salazar","5.º A · Primaria","gold"),
            ("C05","Inglés","Andrea Romero","5.º A · Primaria","purple"),
            ("C06","Arte y Cultura","Elena Ruiz","5.º A · Primaria","orange"),
            ("C07","Matemática","Carlos Soto","1.º A · Secundaria","red"),
            ("C08","Comunicación","Mónica Paredes","1.º A · Secundaria","blue")]
        db.executemany("INSERT INTO courses VALUES(?,?,?,?,?)",courses)
        for day, slots in enumerate([["C01","C02","C03"],["C04","C05","C01"],["C02","C03","C06"],["C01","C04","C05"],["C03","C02","C06"]]):
            for hour, course in enumerate(slots):
                db.execute("INSERT INTO schedule(course,day,start,end,room) VALUES(?,?,?,?,?)",(course,day,f"{8+hour:02}:00",f"{9+hour:02}:00","Aula 5A"))
        for day, course in [(0,"C07"),(2,"C08"),(4,"C07")]:
            db.execute("INSERT INTO schedule(course,day,start,end,room) VALUES(?,?,?,?,?)",(course,day,"08:00","09:00","Aula 1A"))
        for s, _, classroom in students:
            for idx, c in enumerate([x for x in courses if x[3] == classroom]):
                for assessment, shift in [("Práctica 1",0),("Proyecto",1)]:
                    db.execute("INSERT INTO grades VALUES(?,?,?,?,?,?)",(s,c[0],3,assessment,15+(idx%4)+shift,stamp()))
        today = datetime.now().date()
        tasks = [
            ("T01","C01","Fracciones en la vida cotidiana","Resuelve tres situaciones con fracciones y explica el procedimiento que utilizaste.",str(today+timedelta(days=3))),
            ("T02","C02","Leemos y compartimos","Lee un cuento de tu elección. Escribe un resumen y explica qué aprendiste del personaje principal.",str(today+timedelta(days=5))),
            ("T03","C03","Nuestro pequeño ecosistema","Describe las condiciones que necesita una planta para crecer y propone un experimento sencillo.",str(today+timedelta(days=7))),
            ("T04","C07","Números enteros","Plantea y resuelve cinco situaciones con números enteros.",str(today+timedelta(days=4)))]
        db.executemany("INSERT INTO tasks VALUES(?,?,?,?,?)",tasks)
        for title, body, audience in [
            ("Bienvenidos al aula virtual", "Consulta tus cursos, organiza tus actividades y revisa tus calificaciones. Toda la información académica de este entorno es ficticia.", "Todos"),
            ("Lectura en familia", "Esta semana te invitamos a compartir una lectura en casa y conversar sobre lo aprendido. Actividad de demostración.", "Primaria"),
            ("Organiza tu semana", "Revisa tus actividades pendientes antes de comenzar la semana y prepara tus materiales de estudio.", "Todos")]:
            db.execute("INSERT INTO announcements VALUES(?,?,?,?,?)",(uid("A"),title,body,audience,stamp()))


def stamp():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def uid(prefix):
    return prefix + secrets.token_hex(4).upper()


class Invalid(Exception):
    def __init__(self, message, status=400):
        self.message, self.status = message, status


def field(data, key, minimum=1, maximum=100):
    value = data.get(key)
    if not isinstance(value,str) or not minimum <= len(value.strip()) <= maximum:
        raise Invalid(f"Revisa el campo {key}: debe contener entre {minimum} y {maximum} caracteres.")
    return value.strip()


def choice(data, key, values):
    value = data.get(key)
    if value not in values:
        raise Invalid(f"Selecciona un valor válido para {key}.")
    return value


def rows(db, query, args=()):
    return [dict(r) for r in db.execute(query,args).fetchall()]


class Handler(BaseHTTPRequestHandler):
    def reply(self, code, data, cookie=None):
        body = json.dumps(data,ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Cache-Control","no-store")
        self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("Content-Length",str(len(body)))
        if cookie:
            self.send_header("Set-Cookie",cookie)
        self.end_headers()
        self.wfile.write(body)

    def body(self):
        try:
            size = int(self.headers.get("Content-Length","0"))
            if size < 1 or size > 20000:
                raise ValueError()
            data = json.loads(self.rfile.read(size))
            if not isinstance(data,dict):
                raise ValueError()
            return data
        except (ValueError,UnicodeDecodeError):
            raise Invalid("La solicitud no tiene un formato válido.")

    def session(self):
        cookie = SimpleCookie()
        try:
            cookie.load(self.headers.get("Cookie",""))
        except Exception:
            raise Invalid("Inicia sesión para continuar.",401)
        token = cookie.get("sm_session")
        with LOCK:
            session = SESSIONS.get(token.value if token else "")
            if not session or session["expires"] < time.time():
                raise Invalid("Tu sesión terminó. Inicia sesión para continuar.",401)
            session = dict(session)
        with connect() as db:
            user = db.execute("SELECT u.*,s.active FROM users u LEFT JOIN students s ON s.id=u.student WHERE username=?",(session["user"]["username"],)).fetchone()
        if not user or (user["role"] == "student" and not user["active"]):
            raise Invalid("Esta cuenta está inactiva.",401)
        session["user"] = {k:user[k] for k in ("username","name","role","student")}
        return session

    def do_GET(self):
        path = urlsplit(self.path).path
        if path.startswith("/api/"):
            try:
                if path != "/api/state":
                    raise Invalid("Recurso no encontrado.",404)
                session = self.session()
                user = session["user"]
                with connect() as db:
                    admin = user["role"] == "admin"
                    classroom = None if admin else db.execute("SELECT classroom FROM students WHERE id=?",(user["student"],)).fetchone()[0]
                    courses = rows(db,"SELECT * FROM courses" if admin else "SELECT * FROM courses WHERE classroom=?",() if admin else (classroom,))
                    ids = [c["id"] for c in courses]
                    params = ",".join("?" for _ in ids) or "NULL"
                    grades = rows(db,"SELECT * FROM grades" if admin else f"SELECT * FROM grades WHERE student=? AND course IN ({params})",() if admin else (user["student"],*ids))
                    tasks = rows(db,f"SELECT * FROM tasks WHERE course IN ({params}) ORDER BY due",ids)
                    schedule = rows(db,f"SELECT * FROM schedule WHERE course IN ({params}) ORDER BY day,start",ids)
                    announcements = rows(db,"SELECT * FROM announcements ORDER BY created DESC,rowid DESC" if admin else "SELECT * FROM announcements WHERE audience IN ('Todos',?) ORDER BY created DESC,rowid DESC",() if admin else ("Primaria" if "Primaria" in classroom else "Secundaria",))
                    result = {"user":user,"csrf":session["csrf"],"classroom":classroom,"students":rows(db,"SELECT * FROM students ORDER BY name" if admin else "SELECT * FROM students WHERE id=?",() if admin else (user["student"],)),"courses":courses,"grades":grades,"tasks":tasks,"schedule":schedule,"announcements":announcements,"submissions":rows(db,"SELECT * FROM submissions" if admin else "SELECT * FROM submissions WHERE student=?",() if admin else (user["student"],))}
                    if admin:
                        result["contacts"] = rows(db,"SELECT * FROM contacts ORDER BY created DESC")
                        result["audit"] = rows(db,"SELECT * FROM audit ORDER BY id DESC LIMIT 12")
                self.reply(200,result)
            except Invalid as e:
                self.reply(e.status,{"error":e.message})
            return
        # Only explicit public assets are served; the database and sources stay private.
        path = unquote(path).lstrip("/") or "index.html"
        allowed = {"index.html","intranet.html","styles.css","intranet.css","app.js","intranet.js"}
        file = (ROOT / path).resolve()
        if not (path in allowed or (path.startswith("assets/") and file.is_relative_to(ROOT / "assets") and file.suffix.lower() in {".png",".jpg",".jpeg",".svg",".webp"})) or not file.is_file():
            self.send_error(404)
            return
        body = file.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type",mimetypes.guess_type(file.name)[0] or "application/octet-stream")
        self.send_header("Content-Length",str(len(body)))
        self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("Referrer-Policy","strict-origin-when-cross-origin")
        self.send_header("Content-Security-Policy","default-src 'self'; img-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        try:
            self.mutate()
        except Invalid as e:
            self.reply(e.status,{"error":e.message})
        except sqlite3.IntegrityError:
            self.reply(400,{"error":"El registro no es válido o ya existe. Revisa los datos."})
        except Exception as e:
            print("Error interno:",type(e).__name__,flush=True)
            self.reply(500,{"error":"No pudimos guardar los cambios. Intenta nuevamente."})

    def mutate(self):
        origin = self.headers.get("Origin")
        if origin and origin != "http://" + self.headers.get("Host",""):
            raise Invalid("Origen de solicitud no permitido.",403)
        if self.headers.get("Content-Type","").split(";")[0] != "application/json":
            raise Invalid("Se requiere una solicitud JSON.",415)
        path = urlsplit(self.path).path
        data = self.body()
        if path == "/api/login":
            username = field(data,"username",1,50).lower()
            password = field(data,"password",1,100)
            key = (self.client_address[0],username)
            with LOCK:
                recent = [x for x in ATTEMPTS.get(key,[]) if x > time.time()-60]
                if len(recent) >= 8:
                    raise Invalid("Demasiados intentos. Espera un minuto.",429)
                ATTEMPTS[key] = recent+[time.time()]
            with connect() as db:
                user = db.execute("SELECT u.*,s.active FROM users u LEFT JOIN students s ON s.id=u.student WHERE username=?",(username,)).fetchone()
            if not user or not hmac.compare_digest(password_hash(password,user["salt"]),user["password"]) or (user["role"] == "student" and not user["active"]):
                raise Invalid("Usuario o contraseña incorrectos, o cuenta inactiva.",401)
            token = secrets.token_urlsafe(32)
            session = {"user":{k:user[k] for k in ("username","name","role","student")},"csrf":secrets.token_urlsafe(24),"expires":time.time()+7200}
            with LOCK:
                for expired in [k for k,v in SESSIONS.items() if v["expires"] < time.time()]:
                    del SESSIONS[expired]
                SESSIONS[token] = session
                ATTEMPTS.pop(key,None)
            self.reply(200,{"ok":True},f"sm_session={token}; HttpOnly; SameSite=Strict; Path=/; Max-Age=7200")
            return
        if path == "/api/contact":
            name = field(data,"name",3,80)
            email = field(data,"email",3,120)
            if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+",email):
                raise Invalid("Escribe un correo electrónico válido.")
            phone = data.get("phone","")
            if not isinstance(phone,str) or (phone and not re.fullmatch(r"[0-9 +()\-]{6,14}",phone)):
                raise Invalid("Revisa el teléfono de contacto.")
            topic = choice(data,"topic",["Inicial","Primaria","Secundaria","Información institucional","Otro"])
            message = field(data,"message",12,1000)
            if data.get("consent") is not True:
                raise Invalid("Confirma el uso de datos de demostración.")
            ref = uid("SM-")
            with connect() as db:
                db.execute("INSERT INTO contacts(id,name,email,phone,topic,message,created) VALUES(?,?,?,?,?,?,?)",(ref,name,email,phone,topic,message,stamp()))
            self.reply(201,{"id":ref,"message":"Consulta registrada en el entorno de demostración."})
            return
        session = self.session()
        if not hmac.compare_digest(self.headers.get("X-CSRF-Token",""),session["csrf"]):
            raise Invalid("Actualiza la página antes de guardar los cambios.",403)
        user = session["user"]
        if path == "/api/logout":
            cookie = SimpleCookie(self.headers.get("Cookie",""))
            with LOCK:
                SESSIONS.pop(cookie["sm_session"].value,None)
            self.reply(200,{"ok":True},"sm_session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0")
            return
        with connect() as db:
            if path == "/api/submit":
                if user["role"] != "student":
                    raise Invalid("Esta operación corresponde al estudiante.",403)
                task = field(data,"task",1,30)
                exists = db.execute("SELECT 1 FROM tasks t JOIN courses c ON c.id=t.course JOIN students s ON s.classroom=c.classroom WHERE t.id=? AND s.id=?",(task,user["student"])).fetchone()
                if not exists:
                    raise Invalid("No tienes acceso a esta tarea.",403)
                answer = field(data,"answer",10,4000)
                db.execute("INSERT INTO submissions VALUES(?,?,?,?) ON CONFLICT(task,student) DO UPDATE SET answer=excluded.answer,updated=excluded.updated",(task,user["student"],answer,stamp()))
                action, detail = "Entrega de tarea",task
            else:
                if user["role"] != "admin":
                    raise Invalid("No tienes permisos para realizar esta operación.",403)
                if path == "/api/grade":
                    student, course = field(data,"student",1,30),field(data,"course",1,30)
                    if not db.execute("SELECT 1 FROM students s JOIN courses c ON s.classroom=c.classroom WHERE s.id=? AND c.id=? AND s.active=1",(student,course)).fetchone():
                        raise Invalid("Selecciona un curso que corresponda al aula del estudiante activo.")
                    grade = data.get("grade")
                    if isinstance(grade,bool) or not isinstance(grade,(int,float)) or not 0 <= grade <= 20:
                        raise Invalid("La nota debe ser un número entre 0 y 20.")
                    period = choice(data,"period",[1,2,3,4])
                    assessment = choice(data,"assessment",["Práctica 1","Proyecto","Evaluación bimestral"])
                    db.execute("INSERT INTO grades VALUES(?,?,?,?,?,?) ON CONFLICT(student,course,period,assessment) DO UPDATE SET grade=excluded.grade,updated=excluded.updated",(student,course,period,assessment,grade,stamp()))
                    action,detail = "Calificación guardada",f"{student} · {course} · B{period} · {assessment}: {grade}"
                elif path == "/api/student":
                    student = data.get("id") or uid("E")
                    name = field(data,"name",3,80)
                    classroom = choice(data,"classroom",["5.º A · Primaria","1.º A · Secundaria"])
                    active = choice(data,"active",[0,1])
                    prior = db.execute("SELECT * FROM students WHERE id=?",(student,)).fetchone()
                    if prior and prior["classroom"] != classroom and db.execute("SELECT 1 FROM grades WHERE student=? LIMIT 1",(student,)).fetchone():
                        raise Invalid("Este estudiante tiene notas registradas. Conserva su aula para mantener el historial.")
                    db.execute("INSERT INTO students VALUES(?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name,classroom=excluded.classroom,active=excluded.active",(student,name,classroom,active))
                    if prior:
                        db.execute("UPDATE users SET name=? WHERE student=?",(name,student))
                    else:
                        username = field(data,"username",3,30).lower()
                        if not re.fullmatch(r"[a-z0-9._-]+",username):
                            raise Invalid("El usuario solo puede contener letras sin tilde, números, punto, guion o guion bajo.")
                        password = field(data,"password",8,100)
                        salt = secrets.token_hex(16)
                        db.execute("INSERT INTO users VALUES(?,?,?,?,?,?)",(username,name,"student",student,salt,password_hash(password,salt)))
                    action,detail = "Estudiante actualizado" if prior else "Estudiante registrado",student
                elif path == "/api/course":
                    course = data.get("id") or uid("C")
                    name,teacher = field(data,"name",3,60),field(data,"teacher",3,60)
                    classroom = choice(data,"classroom",["5.º A · Primaria","1.º A · Secundaria"])
                    prior = db.execute("SELECT * FROM courses WHERE id=?",(course,)).fetchone()
                    if prior and prior["classroom"] != classroom:
                        raise Invalid("Conserva el aula del curso; crea otro curso para un aula diferente.")
                    db.execute("INSERT INTO courses VALUES(?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name,teacher=excluded.teacher",(course,name,teacher,classroom,"blue"))
                    action,detail = "Curso guardado",course
                elif path == "/api/schedule":
                    course = field(data,"course",1,30)
                    if not db.execute("SELECT 1 FROM courses WHERE id=?",(course,)).fetchone():
                        raise Invalid("Selecciona un curso válido.")
                    day = choice(data,"day",list(range(5)))
                    start,end = field(data,"start",5,5),field(data,"end",5,5)
                    if not all(re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d",v) for v in [start,end]) or start >= end:
                        raise Invalid("La hora final debe ser posterior a la inicial.")
                    room = field(data,"room",2,40)
                    clash = db.execute("SELECT 1 FROM schedule sc JOIN courses c ON c.id=sc.course WHERE sc.day=? AND sc.start<? AND sc.end>? AND (sc.room=? OR c.classroom=(SELECT classroom FROM courses WHERE id=?))",(day,end,start,room,course)).fetchone()
                    if clash:
                        raise Invalid("Ese bloque coincide con una clase del aula o salón seleccionado.")
                    db.execute("INSERT INTO schedule(course,day,start,end,room) VALUES(?,?,?,?,?)",(course,day,start,end,room))
                    action,detail = "Horario agregado",course
                elif path == "/api/task":
                    course = field(data,"course",1,30)
                    if not db.execute("SELECT 1 FROM courses WHERE id=?",(course,)).fetchone():
                        raise Invalid("Selecciona un curso válido.")
                    due = field(data,"due",10,10)
                    try:
                        datetime.strptime(due,"%Y-%m-%d")
                    except ValueError:
                        raise Invalid("Selecciona una fecha válida.")
                    task = uid("T")
                    db.execute("INSERT INTO tasks VALUES(?,?,?,?,?)",(task,course,field(data,"title",3,100),field(data,"description",10,1500),due))
                    action,detail = "Tarea publicada",task
                elif path == "/api/schedule-remove":
                    block = data.get("id")
                    if not isinstance(block,int) or db.execute("DELETE FROM schedule WHERE id=?",(block,)).rowcount != 1:
                        raise Invalid("Bloque de horario no encontrado.",404)
                    action,detail = "Bloque de horario eliminado",str(block)
                elif path == "/api/announcement":
                    ref = uid("A")
                    db.execute("INSERT INTO announcements VALUES(?,?,?,?,?)",(ref,field(data,"title",3,100),field(data,"body",10,1500),choice(data,"audience",["Todos","Primaria","Secundaria"]),stamp()))
                    action,detail = "Comunicado publicado",ref
                elif path == "/api/contact-status":
                    ref = field(data,"id",1,30)
                    status = choice(data,"status",["Pendiente","Atendida"])
                    if db.execute("UPDATE contacts SET status=? WHERE id=?",(status,ref)).rowcount != 1:
                        raise Invalid("Consulta no encontrada.",404)
                    action,detail = "Estado de consulta actualizado",ref
                else:
                    raise Invalid("Operación no encontrada.",404)
            db.execute("INSERT INTO audit(actor,action,detail,created) VALUES(?,?,?,?)",(user["username"],action,detail,stamp()))
        self.reply(200,{"ok":True,"message":action+" correctamente."})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Portal e intranet Santa María · demostración local")
    parser.add_argument("--port",type=int,default=8000)
    parser.add_argument("--db",type=Path,help="Base de datos alternativa para pruebas")
    args = parser.parse_args()
    if args.db:
        DB = args.db.resolve()
    initialize()
    server = ThreadingHTTPServer(("127.0.0.1",args.port),Handler)
    print(f"Santa María disponible en http://127.0.0.1:{args.port} · Ctrl+C para detener",flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
