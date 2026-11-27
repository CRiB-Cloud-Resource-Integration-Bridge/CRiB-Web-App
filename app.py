"""CRiB Assessment 2: server-rendered, user-scoped application."""
import hashlib
import hmac
import os
import re
import secrets
import sqlite3
import time
from functools import wraps
from pathlib import Path
from flask import (Flask, abort, flash, g, redirect, render_template, request,
                   session, url_for, send_file)
from werkzeug.security import generate_password_hash, check_password_hash
from services.providers.mock import MockProvider
from services.providers.google_drive import GoogleDrive, GoogleError, OAuthConfig

def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("CRIB_SECRET_KEY"),
        DATABASE=os.environ.get("CRIB_DATABASE", str(Path(app.instance_path) / "crib.sqlite3")),
        SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("CRIB_HTTPS") == "1",
        MAX_CONTENT_LENGTH=16 * 1024,
        GOOGLE_CLIENT_ID=os.environ.get("GOOGLE_CLIENT_ID"),
        GOOGLE_CLIENT_SECRET=os.environ.get("GOOGLE_CLIENT_SECRET"),
        GOOGLE_REDIRECT_URI=os.environ.get("GOOGLE_REDIRECT_URI"),
        CRIB_TOKEN_KEY=os.environ.get("CRIB_TOKEN_KEY"),
    )
    if config:
        app.config.update(config)
    if not app.secret_key:
        raise RuntimeError("Set CRIB_SECRET_KEY to a randomly generated secret.")
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    oauth = OAuthConfig.from_config(app.config)
    app.jinja_env.globals["google_enabled"] = oauth is not None

    def db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"], timeout=10)
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys=ON")
        return g.db

    with app.app_context():
        db().executescript((Path(__file__).parent / "database/schema.sql").read_text())
        db().commit()
        db().close()

    @app.teardown_appcontext
    def close_db(_error):
        connection = g.pop("db", None)
        if connection is not None:
            connection.close()

    def digest(value):
        return hashlib.sha256(value.encode()).hexdigest()

    def csrf_token():
        if "csrf" not in session:
            session["csrf"] = secrets.token_urlsafe(32)
        return session["csrf"]

    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.before_request
    def load_user():
        g.user = None
        token = session.get("sid")
        if token:
            g.user = db().execute(
                "SELECT u.id,u.name,u.email FROM users u JOIN sessions s ON s.user_id=u.id "
                "WHERE s.token_hash=? AND s.expires_at>?", (digest(token), int(time.time()))
            ).fetchone()
        if request.method == "POST":
            supplied = request.form.get("csrf", "")
            if not hmac.compare_digest(supplied.encode(), session.get("csrf", "-").encode()):
                abort(400, "Invalid form token. Reload the page and try again.")

    @app.after_request
    def headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'"
        if request.endpoint != "static":
            response.headers["Cache-Control"] = "no-store"
        return response

    def protected(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if g.user is None:
                return redirect(url_for("signin"))
            return fn(*args, **kwargs)
        return wrapper

    def google_connection():
        return db().execute("SELECT * FROM google_connections WHERE user_id=?", (g.user["id"],)).fetchone()

    def connection():
        return google_connection() or db().execute("SELECT * FROM connections WHERE user_id=?", (g.user["id"],)).fetchone()

    def provider():
        connected = connection()
        if not connected:
            abort(403, "Connect a provider before accessing resources.")
        if connected["provider"] == "google":
            if oauth is None:
                raise GoogleError("Google Drive is not configured. Disconnect or contact the demo administrator.")
            user_id = g.user["id"]
            def save_tokens(tokens):
                # Do not recreate a connection after another request disconnects it.
                db().execute("UPDATE google_connections SET tokens=? WHERE user_id=? AND tokens=?",
                             (oauth.encrypt(tokens), user_id, connected["tokens"]))
                db().commit()
            return GoogleDrive(oauth, oauth.decrypt(connected["tokens"]), save_tokens)
        return MockProvider(g.user["id"])

    def provider_label():
        connected = connection()
        return "Google Drive" if connected and connected["provider"] == "google" else "Demo storage"

    def start_session(user_id):
        old = session.get("sid")
        if old:
            db().execute("DELETE FROM sessions WHERE token_hash=?", (digest(old),))
        token = secrets.token_urlsafe(32)
        now = int(time.time())
        db().execute("DELETE FROM sessions WHERE expires_at<=?", (now,))
        db().execute("INSERT INTO sessions VALUES (?,?,?)", (digest(token), user_id, now+43200))
        db().commit()
        session.clear()
        session["sid"] = token

    @app.get("/")
    def landing():
        return render_template("app.html", page="landing")

    @app.get("/health")
    def health():
        db().execute("SELECT 1")
        return {"status": "ok"}

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if g.user:
            return redirect(url_for("dashboard"))
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            if not (1 <= len(name) <= 80 and len(email) <= 254 and re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email)):
                flash("Enter a valid name and email.", "error")
            elif not (12 <= len(password) <= 128 and re.search(r"[\d\W]", password)):
                flash("Use 12–128 characters including a number or symbol.", "error")
            else:
                try:
                    cur = db().execute("INSERT INTO users(name,email,password_hash) VALUES(?,?,?)",
                                       (name, email, generate_password_hash(password)))
                    db().commit()
                except sqlite3.IntegrityError:
                    flash("Could not create this account. Try signing in.", "error")
                else:
                    start_session(cur.lastrowid)
                    return redirect(url_for("dashboard"))
        return render_template("app.html", page="signup")

    @app.route("/signin", methods=["GET", "POST"])
    def signin():
        if g.user:
            return redirect(url_for("dashboard"))
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()[:254]
            password = request.form.get("password", "")
            now = int(time.time())
            attempt = db().execute("SELECT * FROM login_attempts WHERE email=?", (email,)).fetchone()
            count = attempt["count"] if attempt and attempt["until"] > now else 0
            if count >= 5:
                flash("Too many attempts. Try again in 15 minutes.", "error")
                return render_template("app.html", page="signin"), 429
            user = db().execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
            if user and len(password) <= 128 and check_password_hash(user["password_hash"], password):
                db().execute("DELETE FROM login_attempts WHERE email=?", (email,))
                start_session(user["id"])
                return redirect(url_for("dashboard"))
            db().execute("DELETE FROM login_attempts WHERE until<=?", (now,))
            db().execute("INSERT INTO login_attempts VALUES(?,?,?) ON CONFLICT(email) DO UPDATE SET count=excluded.count,until=excluded.until",
                         (email, count+1, now+900))
            db().commit()
            flash("Email or password is incorrect.", "error")
        return render_template("app.html", page="signin")

    @app.post("/logout")
    @protected
    def logout():
        db().execute("DELETE FROM sessions WHERE token_hash=?", (digest(session["sid"]),))
        db().commit()
        session.clear()
        flash("You have signed out.")
        return redirect(url_for("landing"))

    @app.get("/dashboard")
    @protected
    def dashboard():
        connected = connection()
        return render_template("app.html", page="dashboard", connected=connected)

    @app.get("/providers")
    @protected
    def providers():
        return render_template("app.html", page="providers", connected=connection())

    @app.post("/providers/mock/connect")
    @protected
    def connect():
        if google_connection():
            flash("Disconnect Google Drive before switching providers.", "error")
            return redirect(url_for("providers"))
        session.pop("google_oauth", None)
        db().execute("INSERT OR IGNORE INTO connections(user_id,provider) VALUES (?,?)", (g.user["id"], "mock"))
        db().commit()
        flash("Demo provider connected. No Google account was accessed.")
        return redirect(url_for("files"))

    @app.post("/providers/google/connect")
    @protected
    def google_connect():
        if oauth is None:
            abort(403, "Google Drive is not configured.")
        if connection() and connection()["provider"] == "mock":
            flash("Disconnect demo storage before connecting Google Drive.", "error")
            return redirect(url_for("providers"))
        state = secrets.token_urlsafe(32)
        verifier = secrets.token_urlsafe(64)
        session["google_oauth"] = {"state": state, "verifier": verifier,
                                  "user": g.user["id"], "time": int(time.time())}
        return redirect(oauth.authorization_url(state, verifier))

    @app.get("/oauth/google/callback")
    @protected
    def google_callback():
        pending = session.pop("google_oauth", None)
        state = request.args.get("state", "")
        if (oauth is None or not pending or pending["user"] != g.user["id"]
                or int(time.time()) - pending["time"] > 600
                or not hmac.compare_digest(state.encode(), pending["state"].encode())):
            abort(400, "Invalid or expired authorization request. Start again from providers.")
        if request.args.get("error") or not request.args.get("code"):
            flash("Google authorization was cancelled or denied.", "error")
            return redirect(url_for("providers"))
        tokens = oauth.exchange(request.args["code"], pending["verifier"])
        db().execute("DELETE FROM connections WHERE user_id=?", (g.user["id"],))
        db().execute("INSERT INTO google_connections(user_id,provider,tokens) VALUES(?,?,?) "
                     "ON CONFLICT(user_id) DO UPDATE SET tokens=excluded.tokens",
                     (g.user["id"], "google", oauth.encrypt(tokens)))
        db().commit()
        flash("Google Drive connected with read-only access.")
        return redirect(url_for("files"))

    @app.post("/providers/disconnect")
    @protected
    def disconnect():
        existing = google_connection()
        session.pop("google_oauth", None)
        db().execute("DELETE FROM connections WHERE user_id=?", (g.user["id"],))
        db().execute("DELETE FROM google_connections WHERE user_id=?", (g.user["id"],))
        db().commit()
        if existing:
            try:
                if oauth is None:
                    raise GoogleError("OAuth not configured.")
                oauth.revoke(oauth.decrypt(existing["tokens"]))
            except GoogleError:
                flash("Disconnected locally. Google revocation could not be confirmed; remove CRiB from your Google Account connections if needed.", "error")
                return redirect(url_for("dashboard"))
        flash("Provider disconnected.")
        return redirect(url_for("dashboard"))

    @app.get("/files")
    @protected
    def files():
        if not connection():
            return redirect(url_for("providers"))
        adapter = provider()
        folder = request.args.get("folder", "root")
        query = request.args.get("q", "").strip()[:100]
        kind = request.args.get("kind", "")
        if kind not in ("", "folder", "file"):
            abort(400, "Unknown filter.")
        current = None if folder == "root" else adapter.get(folder)
        if folder != "root" and (not current or current["kind"] != "folder"):
            abort(404, "Folder not found.")
        rows = adapter.list(folder, query, kind)
        return render_template("app.html", page="files", rows=rows, folder=folder,
                               current=current, query=query, kind=kind, provider_label=provider_label())

    @app.get("/files/<file_id>")
    @protected
    def details(file_id):
        item = provider().get(file_id)
        if not item:
            abort(404, "Resource not found.")
        if item["kind"] == "folder":
            return redirect(url_for("files", folder=file_id))
        return render_template("app.html", page="details", item=item)

    @app.get("/files/<file_id>/download")
    @protected
    def download(file_id):
        adapter = provider()
        item = adapter.get(file_id)
        if not item:
            abort(404, "Resource not found.")
        if not item["downloadable"]:
            abort(403, "This resource cannot be downloaded.")
        return send_file(adapter.download(file_id), download_name=item["name"],
                         mimetype="application/octet-stream", as_attachment=True)

    @app.errorhandler(GoogleError)
    def google_error(error):
        return render_template("app.html", page="error", error=str(error), provider_error=True), 502

    @app.errorhandler(400)
    @app.errorhandler(403)
    @app.errorhandler(404)
    def client_error(error):
        return render_template("app.html", page="error", error=error.description), error.code

    @app.errorhandler(500)
    def server_error(_error):
        return render_template("app.html", page="error", error="Something went wrong. Please try again."), 500

    return app

if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=int(os.environ.get("PORT", "8000")))
