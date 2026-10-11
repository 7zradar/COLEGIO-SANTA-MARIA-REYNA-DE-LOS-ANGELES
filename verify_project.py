"""Pruebas de integración del piloto; usan una base temporal, no los datos de la demo."""
import http.cookiejar
import json
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
import server


class Client:
    def __init__(self, base):
        self.base = base
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        self.csrf = ""

    def request(self, path, body=None, csrf=True, origin=None):
        headers = {"Content-Type":"application/json"}
        if csrf:
            headers["X-CSRF-Token"] = self.csrf
        if origin:
            headers["Origin"] = origin
        req = urllib.request.Request(self.base+path,data=json.dumps(body).encode() if body is not None else None,headers=headers)
        try:
            response = self.opener.open(req)
        except urllib.error.HTTPError as e:
            response = e
        raw = response.read()
        status = response.status
        response_headers = response.headers
        response.close()
        try:
            result = json.loads(raw)
        except (ValueError,UnicodeDecodeError):
            result = raw
        return status,result,response_headers

    def login(self, username="admin", password="Admin2026!"):
        code,_,_ = self.request("/api/login",{"username":username,"password":password})
        assert code == 200
        state = self.request("/api/state")[1]
        self.csrf = state["csrf"]
        return state


class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="santamaria_qa_")
        server.DB = Path(cls.temp.name)/"demo.sqlite3"
        server.initialize()
        class QuietHandler(server.Handler):
            def log_message(self, *args):
                pass
        cls.http = server.ThreadingHTTPServer(("127.0.0.1",0),QuietHandler)
        cls.base = f"http://127.0.0.1:{cls.http.server_port}"
        cls.thread = threading.Thread(target=cls.http.serve_forever,daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()
        cls.http.server_close()
        cls.thread.join()
        cls.temp.cleanup()

    def client(self,user="admin",password="Admin2026!"):
        c=Client(self.base)
        c.login(user,password)
        return c

    def test_public_pages_assets_and_private_files(self):
        c=Client(self.base)
        for path in ["/","/intranet.html","/app.js","/intranet.js","/assets/logo.png","/assets/foto12.jpg"]:
            self.assertEqual(c.request(path)[0],200,path)
        for path in ["/server.py","/data/santamaria.sqlite3","/assets/../server.py","/README.md"]:
            self.assertEqual(c.request(path)[0],404,path)

    def test_authentication_and_cookie(self):
        c=Client(self.base)
        self.assertEqual(c.request("/api/state")[0],401)
        self.assertEqual(c.request("/api/login",{"username":"admin","password":"wrong"})[0],401)
        code,_,headers=c.request("/api/login",{"username":"ana","password":"Alumno2026!"})
        self.assertEqual(code,200)
        self.assertIn("HttpOnly",headers["Set-Cookie"])
        self.assertIn("SameSite=Strict",headers["Set-Cookie"])

    def test_roles_and_student_privacy(self):
        c=self.client("ana","Alumno2026!")
        state=c.request("/api/state")[1]
        self.assertEqual([s["id"] for s in state["students"]],["E001"])
        self.assertTrue(all(g["student"]=="E001" for g in state["grades"]))
        self.assertTrue(all(co["classroom"]=="5.º A · Primaria" for co in state["courses"]))
        self.assertNotIn("contacts",state)
        self.assertEqual(c.request("/api/grade",{"student":"E001","course":"C01","period":3,"assessment":"Proyecto","grade":19})[0],403)

    def test_admin_grade_visible_in_independent_student_session(self):
        a=self.client();s=self.client("ana","Alumno2026!")
        payload={"student":"E001","course":"C01","period":3,"assessment":"Evaluación bimestral","grade":19}
        self.assertEqual(a.request("/api/grade",payload)[0],200)
        state=s.request("/api/state")[1]
        grade=next(g for g in state["grades"] if g["course"]=="C01" and g["assessment"]=="Evaluación bimestral")
        self.assertEqual(grade["grade"],19)
        server.initialize()
        with server.connect() as db:
            self.assertEqual(db.execute("SELECT grade FROM grades WHERE student='E001' AND assessment='Evaluación bimestral'").fetchone()[0],19)

    def test_grade_range_required_values_and_classroom(self):
        c=self.client()
        base={"student":"E001","course":"C01","period":3,"assessment":"Proyecto"}
        for value in [-1,21,"19",None,True,float('nan')]:
            self.assertEqual(c.request("/api/grade",{**base,"grade":value})[0],400)
        self.assertEqual(c.request("/api/grade",{**base,"course":"C07","grade":18})[0],400)
        self.assertEqual(c.request("/api/grade",{**base,"period":7,"grade":18})[0],400)

    def test_csrf_and_external_origin(self):
        c=self.client()
        body={"title":"Aviso test","body":"Este aviso es una prueba controlada.","audience":"Todos"}
        self.assertEqual(c.request("/api/announcement",body,csrf=False)[0],403)
        self.assertEqual(c.request("/api/announcement",body,origin="https://another.example")[0],403)

    def test_student_creation_login_and_deactivation(self):
        c=self.client()
        body={"name":"Estudiante ficticio de QA","classroom":"5.º A · Primaria","active":1,"username":"qa_alumno","password":"Prueba2026!"}
        self.assertEqual(c.request("/api/student",body)[0],200)
        s=self.client("qa_alumno","Prueba2026!")
        student=s.request("/api/state")[1]["students"][0]
        self.assertEqual(student["name"],body["name"])
        self.assertEqual(c.request("/api/student",{**body,"id":student["id"],"active":0})[0],200)
        self.assertEqual(s.request("/api/state")[0],401)

    def test_course_and_schedule_conflicts(self):
        c=self.client()
        payload={"name":"Curso QA","teacher":"Docente ficticio","classroom":"5.º A · Primaria"}
        self.assertEqual(c.request("/api/course",payload)[0],200)
        course=next(co for co in c.request("/api/state")[1]["courses"] if co["name"]=="Curso QA")
        block={"course":course["id"],"day":0,"start":"08:30","end":"09:30","room":"Laboratorio QA"}
        self.assertEqual(c.request("/api/schedule",block)[0],400)
        block.update(start="13:00",end="14:00")
        self.assertEqual(c.request("/api/schedule",block)[0],200)
        schedule=next(sc for sc in c.request("/api/state")[1]["schedule"] if sc["course"]==course["id"])
        self.assertEqual(c.request("/api/schedule-remove",{"id":schedule["id"]})[0],200)

    def test_task_submission_visible_to_admin_and_update(self):
        s=self.client("ana","Alumno2026!");a=self.client()
        self.assertEqual(s.request("/api/submit",{"task":"T01","answer":"Mi respuesta ficticia para la prueba."})[0],200)
        self.assertEqual(s.request("/api/submit",{"task":"T01","answer":"Mi respuesta ficticia corregida para la prueba."})[0],200)
        answers=a.request("/api/state")[1]["submissions"]
        answer=next(x for x in answers if x["student"]=="E001" and x["task"]=="T01")
        self.assertIn("corregida",answer["answer"])
        self.assertEqual(s.request("/api/submit",{"task":"T04","answer":"Intento de acceder a otro nivel."})[0],403)

    def test_publish_task_validation(self):
        c=self.client()
        payload={"course":"C01","title":"Actividad QA","description":"Descripción de una actividad ficticia.","due":"2026-10-20"}
        self.assertEqual(c.request("/api/task",payload)[0],200)
        self.assertEqual(c.request("/api/task",{**payload,"due":"2026-02-30"})[0],400)
        self.assertEqual(c.request("/api/task",{**payload,"course":"invalid"})[0],400)

    def test_announcements_targeted_by_level(self):
        a=self.client()
        self.assertEqual(a.request("/api/announcement",{"title":"Aviso exclusivo QA","body":"Información ficticia para secundaria.","audience":"Secundaria"})[0],200)
        primary=self.client("ana","Alumno2026!").request("/api/state")[1]
        secondary=self.client("camila","Alumno2026!").request("/api/state")[1]
        self.assertFalse(any(x["title"]=="Aviso exclusivo QA" for x in primary["announcements"]))
        self.assertTrue(any(x["title"]=="Aviso exclusivo QA" for x in secondary["announcements"]))

    def test_contact_tracking_and_handling(self):
        c=Client(self.base)
        body={"name":"Familia ficticia QA","email":"familia@example.test","phone":"999999999","topic":"Primaria","message":"Solicito información para una prueba.","consent":True}
        code,result,_=c.request("/api/contact",body)
        self.assertEqual(code,201)
        a=self.client()
        self.assertTrue(any(x["id"]==result["id"] for x in a.request("/api/state")[1]["contacts"]))
        self.assertEqual(a.request("/api/contact-status",{"id":result["id"],"status":"Atendida"})[0],200)
        self.assertEqual(c.request("/api/contact",{**body,"email":"wrong"})[0],400)
        self.assertEqual(c.request("/api/contact",{**body,"consent":False})[0],400)

    def test_audit_and_logout(self):
        c=self.client()
        c.request("/api/announcement",{"title":"Auditoría QA","body":"Comunicado para comprobar la auditoría.","audience":"Todos"})
        self.assertTrue(any(a["actor"]=="admin" for a in c.request("/api/state")[1]["audit"]))
        self.assertEqual(c.request("/api/logout",{})[0],200)
        self.assertEqual(c.request("/api/state")[0],401)


if __name__=="__main__":
    unittest.main(verbosity=2)
