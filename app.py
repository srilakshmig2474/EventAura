from flask import (



    Flask,



    render_template,



    request,



    redirect,



    url_for,



    flash,



    send_file,
    session



)



import psycopg2



import os



import uuid



import qrcode



import smtplib



from email.message import EmailMessage



from datetime import datetime



from dotenv import load_dotenv



from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps



from reportlab.pdfgen import canvas



from reportlab.lib.pagesizes import A4, landscape



from reportlab.lib.utils import ImageReader



# ============================================================



# LOAD ENVIRONMENT VARIABLES



# ============================================================



load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))



# ============================================================



# FLASK APPLICATION



# ============================================================



app = Flask(__name__)



app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-secret-key-before-deployment")


def login_required(view_function):
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        if not session.get("organizer_email"):
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        return view_function(*args, **kwargs)

    return wrapped_view


# ============================================================



# FOLDERS



# ============================================================



UPLOAD_FOLDER = "uploads"



CERTIFICATE_FOLDER = "certificates"



QR_FOLDER = os.path.join("static", "qr_codes")



os.makedirs(UPLOAD_FOLDER, exist_ok=True)



os.makedirs(CERTIFICATE_FOLDER, exist_ok=True)



os.makedirs(QR_FOLDER, exist_ok=True)



# ============================================================



# ALLOWED TEMPLATE FILES



# ============================================================



ALLOWED_TEMPLATE_EXTENSIONS = {



    "png",



    "jpg",



    "jpeg"



}



def allowed_template(filename):



    return (



        "." in filename



        and filename.rsplit(".", 1)[1].lower()



        in ALLOWED_TEMPLATE_EXTENSIONS



    )



# ============================================================



# DATABASE CONNECTION



# ============================================================



def get_db_connection():



    connection = psycopg2.connect(



        host=os.getenv("DB_HOST"),



        port=os.getenv("DB_PORT"),



        database=os.getenv("DB_NAME"),



        user=os.getenv("DB_USER"),



        password=os.getenv("DB_PASSWORD")



    )



    return connection



# ============================================================



# HOME PAGE



# ============================================================



def ensure_auth_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS organizer_accounts (
            account_id SERIAL PRIMARY KEY,
            full_name VARCHAR(150) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)


@app.route("/")
def home():
    if session.get("organizer_email"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("organizer_email"):
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        connection = cursor = None
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            ensure_auth_table(cursor)
            connection.commit()
            cursor.execute("SELECT full_name, password_hash FROM organizer_accounts WHERE LOWER(email)=%s", (email,))
            account = cursor.fetchone()
            if account and check_password_hash(account[1], password):
                session.clear()
                session["organizer_email"] = email
                session["organizer_name"] = account[0]
                return redirect(url_for("dashboard"))
            flash("Invalid email or password.", "error")
        except Exception:
            if connection: connection.rollback()
            app.logger.exception("Login failed")
            flash("Unable to log in. Check the database connection and try again.", "error")
        finally:
            if cursor: cursor.close()
            if connection: connection.close()
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if session.get("organizer_email"):
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        if not full_name or not email or not password:
            flash("Please complete all required fields.", "error")
        elif len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")
        elif password != confirm_password:
            flash("Passwords do not match.", "error")
        else:
            connection = cursor = None
            try:
                connection = get_db_connection()
                cursor = connection.cursor()
                ensure_auth_table(cursor)
                cursor.execute("INSERT INTO organizer_accounts (full_name, email, password_hash) VALUES (%s, %s, %s)",
                               (full_name, email, generate_password_hash(password)))
                connection.commit()
                session.clear()
                session["organizer_email"] = email
                session["organizer_name"] = full_name
                flash("Account created. Welcome to EventAura!", "success")
                return redirect(url_for("dashboard"))
            except psycopg2.errors.UniqueViolation:
                if connection: connection.rollback()
                flash("An account with this email already exists. Please log in.", "error")
            except Exception:
                if connection: connection.rollback()
                app.logger.exception("Signup failed")
                flash("Could not create your account. Please try again.", "error")
            finally:
                if cursor: cursor.close()
                if connection: connection.close()
    return render_template("signup.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/home")
@login_required
def organizer_home():
    return render_template("index.html")



# ============================================================



# CREATE EVENT



# ============================================================



@app.route("/create-event", methods=["POST"])



@login_required
def create_event():



    organization_name = request.form["organization_name"]



    organization_type = request.form["organization_type"]



    organization_email = session["organizer_email"]



    event_name = request.form["event_name"]



    event_type = request.form["event_type"]



    description = request.form["description"]



    event_date = request.form["event_date"]



    venue = request.form["venue"]



    connection = None



    cursor = None



    try:



        connection = get_db_connection()



        cursor = connection.cursor()



        cursor.execute(



            """



            INSERT INTO organizations



            (



                organization_name,



                organization_type,



                email



            )



            VALUES (%s, %s, %s)



            RETURNING organization_id;



            """,



            (



                organization_name,



                organization_type,



                organization_email



            )



        )



        organization_id = cursor.fetchone()[0]



        cursor.execute(



            """



            INSERT INTO events



            (



                organization_id,



                event_name,



                event_type,



                description,



                event_date,



                venue



            )



            VALUES (%s, %s, %s, %s, %s, %s)



            RETURNING event_id;



            """,



            (



                organization_id,



                event_name,



                event_type,



                description,



                event_date,



                venue



            )



        )



        event_id = cursor.fetchone()[0]



        connection.commit()



        flash(



            f"Event created successfully! Event ID: {event_id}",



            "success"



        )



        return redirect(url_for("dashboard"))



    except Exception as error:



        if connection:



            connection.rollback()



        flash(



            f"Error creating event: {error}",



            "error"



        )



        return redirect(url_for("home"))



    finally:



        if cursor:



            cursor.close()



        if connection:



            connection.close()



# ============================================================



# EVENT DASHBOARD



# ============================================================



@app.route("/dashboard")



@login_required
def dashboard():



    connection = None



    cursor = None



    try:



        connection = get_db_connection()



        cursor = connection.cursor()



        cursor.execute(



            """



            SELECT



                e.event_id,



                e.event_name,



                e.event_type,



                e.description,



                e.event_date,



                e.venue,



                o.organization_name,



                o.organization_type,



                o.email,



                COUNT(DISTINCT r.registration_id)



                    AS total_registrations,



                COUNT(



                    DISTINCT CASE



                        WHEN a.attendance_status = 'Present'



                        THEN a.attendance_id



                    END



                ) AS total_attendees



            FROM events e



            JOIN organizations o



                ON e.organization_id = o.organization_id



            LEFT JOIN registrations r



                ON e.event_id = r.event_id



            LEFT JOIN attendance a



                ON r.registration_id = a.registration_id



            
            WHERE LOWER(o.email) = %s

            GROUP BY



                e.event_id,



                e.event_name,



                e.event_type,



                e.description,



                e.event_date,



                e.venue,



                o.organization_name,



                o.organization_type,



                o.email



            ORDER BY e.event_date DESC;



            """, (session["organizer_email"],)
        )

        events = cursor.fetchall()



        return render_template(



            "dashboard.html",



            events=events



        )



    except Exception as error:



        flash(



            f"Error loading dashboard: {error}",



            "error"



        )



        return redirect(url_for("home"))



    finally:



        if cursor:



            cursor.close()



        if connection:



            connection.close()



# ============================================================



# EVENT DETAILS



# ============================================================



@app.route("/event/<int:event_id>/edit", methods=["GET", "POST"])
@login_required
def edit_event(event_id):
    """Edit an event and its organization details without disturbing registrations."""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT e.event_id, e.organization_id, e.event_name, e.event_type,
                   e.description, e.event_date, e.venue, o.organization_name,
                   o.organization_type, o.email
            FROM events e JOIN organizations o ON e.organization_id=o.organization_id
            WHERE e.event_id=%s
        """, (event_id,))
        event = cursor.fetchone()
        if not event:
            flash("Event not found.", "error")
            return redirect(url_for("dashboard"))
        if event[9].strip().lower() != session["organizer_email"].strip().lower():
            flash("You do not have permission to manage this event.", "error")
            return redirect(url_for("dashboard"))
        if request.method == "GET":
            return render_template("edit_event.html", event=event)

        fields = {
            "organization_name": request.form.get("organization_name", "").strip(),
            "organization_type": request.form.get("organization_type", "").strip(),
            "organization_email": session["organizer_email"],
            "event_name": request.form.get("event_name", "").strip(),
            "event_type": request.form.get("event_type", "").strip(),
            "description": request.form.get("description", "").strip(),
            "event_date": request.form.get("event_date", "").strip(),
            "venue": request.form.get("venue", "").strip(),
        }
        if not all(fields[k] for k in ("organization_name", "organization_type", "organization_email", "event_name", "event_type", "event_date", "venue")):
            flash("Please fill in all required fields.", "error")
            return render_template("edit_event.html", event=event, form_data=fields)
        cursor.execute("""UPDATE organizations SET organization_name=%s, organization_type=%s, email=%s WHERE organization_id=%s""",
                       (fields["organization_name"], fields["organization_type"], fields["organization_email"], event[1]))
        cursor.execute("""UPDATE events SET event_name=%s, event_type=%s, description=%s, event_date=%s, venue=%s WHERE event_id=%s""",
                       (fields["event_name"], fields["event_type"], fields["description"], fields["event_date"], fields["venue"], event_id))
        connection.commit()
        flash("Event details updated successfully.", "success")
        return redirect(url_for("event_details", event_id=event_id))
    except Exception as error:
        if connection: connection.rollback()
        app.logger.exception("Could not edit event %s", event_id)
        flash(f"Could not update event: {error}", "error")
        return redirect(url_for("dashboard"))
    finally:
        if cursor: cursor.close()
        if connection: connection.close()


@app.route("/event/<int:event_id>/delete", methods=["POST"])
@login_required
def delete_event(event_id):
    """Permanently delete an organizer-owned event after re-authentication."""
    connection = None
    cursor = None
    try:
        # Require the organizer to re-enter their account credentials for this destructive action.
        author_email = request.form.get("author_email", "").strip().lower()
        author_password = request.form.get("author_password", "")
        logged_in_email = session.get("organizer_email", "").strip().lower()

        if not author_email or not author_password:
            flash("Deletion cancelled: author email and password are required.", "error")
            return redirect(url_for("dashboard"))

        if author_email != logged_in_email:
            flash("The author email must match the currently logged-in organizer.", "error")
            return redirect(url_for("dashboard"))

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT password_hash FROM organizer_accounts WHERE LOWER(email)=%s",
            (author_email,),
        )
        account = cursor.fetchone()
        if not account or not check_password_hash(account[0], author_password):
            flash("Incorrect author email or password. The event was not deleted.", "error")
            return redirect(url_for("dashboard"))

        cursor.execute(
            "SELECT organization_id FROM events WHERE event_id=%s",
            (event_id,),
        )
        event_row = cursor.fetchone()
        if not event_row:
            flash("Event not found.", "error")
            return redirect(url_for("dashboard"))

        organization_id = event_row[0]
        cursor.execute(
            "SELECT email FROM organizations WHERE organization_id=%s",
            (organization_id,),
        )
        owner_row = cursor.fetchone()
        if not owner_row or owner_row[0].strip().lower() != author_email:
            flash("You do not have permission to delete this event.", "error")
            return redirect(url_for("dashboard"))

        # Permanently remove linked event records in foreign-key-safe order.
        # This intentionally deletes attendance and certificate records for this event.
        cursor.execute(
            "DELETE FROM attendance WHERE registration_id IN "
            "(SELECT registration_id FROM registrations WHERE event_id=%s)",
            (event_id,),
        )
        cursor.execute(
            "DELETE FROM certificates WHERE registration_id IN "
            "(SELECT registration_id FROM registrations WHERE event_id=%s)",
            (event_id,),
        )
        cursor.execute("DELETE FROM registrations WHERE event_id=%s", (event_id,))
        cursor.execute("DELETE FROM certificate_templates WHERE event_id=%s", (event_id,))
        cursor.execute("DELETE FROM events WHERE event_id=%s", (event_id,))

        # Remove the organization only if it no longer owns any events.
        cursor.execute(
            "SELECT COUNT(*) FROM events WHERE organization_id=%s",
            (organization_id,),
        )
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "DELETE FROM organizations WHERE organization_id=%s",
                (organization_id,),
            )

        connection.commit()
        flash("Event permanently deleted, including its attendance and certificate records.", "success")
    except Exception as error:
        if connection:
            connection.rollback()
        app.logger.exception("Could not permanently delete event %s", event_id)
        flash(f"Could not delete event: {error}", "error")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return redirect(url_for("dashboard"))


@app.route("/event/<int:event_id>")
@login_required
def event_details(event_id):



    connection = None



    cursor = None



    try:



        connection = get_db_connection()



        cursor = connection.cursor()



        cursor.execute(



            """



            SELECT



                e.event_id,



                e.event_name,



                e.event_type,



                e.description,



                e.event_date,



                e.venue,



                o.organization_name,



                o.organization_type,



                o.email



            FROM events e



            JOIN organizations o



                ON e.organization_id = o.organization_id



            WHERE e.event_id = %s;



            """,



            (event_id,)



        )



        event = cursor.fetchone()
        if event and str(event[8]).strip().lower() != session["organizer_email"].strip().lower():
            flash("You do not have permission to view this event.", "error")
            return redirect(url_for("dashboard"))



        if not event:



            flash("Event not found.", "error")



            return redirect(url_for("dashboard"))



        cursor.execute(



            """



            SELECT



                r.registration_id,



                r.registration_code,



                p.participant_name,



                p.email,



                p.phone,



                r.registered_at,



                COALESCE(a.attendance_status, 'Not Marked')



                    AS attendance_status



            FROM registrations r



            JOIN participants p



                ON r.participant_id = p.participant_id



            LEFT JOIN attendance a



                ON r.registration_id = a.registration_id



            WHERE r.event_id = %s



            ORDER BY r.registered_at DESC;



            """,



            (event_id,)



        )



        participants = cursor.fetchall()



        # Get the active Merit template



        cursor.execute(



            """



            SELECT



                template_id,



                template_name,



                template_file_path,



                certificate_type



            FROM certificate_templates



            WHERE event_id = %s



              AND certificate_type = 'Merit'



              AND is_active = TRUE



            ORDER BY template_id DESC



            LIMIT 1;



            """,



            (event_id,)



        )



        merit_template = cursor.fetchone()



        # Get the active Participation template



        cursor.execute(



            """



            SELECT



                template_id,



                template_name,



                template_file_path,



                certificate_type



            FROM certificate_templates



            WHERE event_id = %s



              AND certificate_type = 'Participation'



              AND is_active = TRUE



            ORDER BY template_id DESC



            LIMIT 1;



            """,



            (event_id,)



        )



        participation_template = cursor.fetchone()



        # Get already generated certificates for this event



        cursor.execute(



            """



            SELECT



                c.certificate_id,



                r.registration_id,



                p.participant_name,



                p.email,



                c.certificate_type,



                c.certificate_number,



                c.email_status,



                c.generated_at



            FROM certificates c



            JOIN registrations r



                ON c.registration_id = r.registration_id



            JOIN participants p



                ON r.participant_id = p.participant_id



            WHERE r.event_id = %s



            ORDER BY c.generated_at DESC;



            """,



            (event_id,)



        )



        generated_certificates = cursor.fetchall()



        return render_template(



            "event_details.html",



            event=event,



            participants=participants,



            merit_template=merit_template,



            participation_template=participation_template,



            generated_certificates=generated_certificates



        )



    except Exception as error:



        flash(f"Error loading event: {error}", "error")



        return redirect(url_for("dashboard"))



    finally:



        if cursor:



            cursor.close()



        if connection:



            connection.close()



# ============================================================

# EMAIL REGISTRATION QR CODE

# ============================================================



def send_registration_qr_email(

    recipient_email,

    participant_name,

    event_name,

    event_date,

    venue,

    registration_code,

    qr_path,

):

    """Email the participant's unique registration QR code as a PNG attachment."""

    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")

    smtp_port = int(os.getenv("SMTP_PORT", "465"))

    smtp_email = os.getenv("SMTP_EMAIL")

    smtp_password = os.getenv("SMTP_PASSWORD")



    if not smtp_email or not smtp_password:

        raise ValueError("SMTP_EMAIL and SMTP_PASSWORD are not configured in .env")

    if not recipient_email:

        raise ValueError("Participant email is missing.")

    if not os.path.isfile(qr_path):

        raise FileNotFoundError(f"QR code image not found: {qr_path}")



    date_text = event_date.strftime("%d %B %Y") if hasattr(event_date, "strftime") else str(event_date)

    venue_text = str(venue) if venue else "Not specified"



    message = EmailMessage()

    message["Subject"] = f"Registration confirmed - {event_name}"

    message["From"] = smtp_email

    message["To"] = recipient_email

    message.set_content(

        f"""Dear {participant_name},



Your registration for \\"{event_name}\\" is confirmed.



Event date: {date_text}

Venue: {venue_text}

Registration ID: {registration_code}



Your personal attendance QR code is attached to this email. Please save it and bring it with you to the event. The organizer should scan/verify it at the event. Keep the QR code safe.



Your certificate is subject to attendance being recorded by the organizer.



Regards,

Smart Event Certificate Platform

"""

    )



    with open(qr_path, "rb") as qr_file:

        message.add_attachment(

            qr_file.read(),

            maintype="image",

            subtype="png",

            filename=f"{registration_code}.png",

        )



    with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30) as smtp:

        smtp.login(smtp_email, smtp_password)

        smtp.send_message(message)





# ============================================================



# PARTICIPANT REGISTRATION



# ============================================================



@app.route(



    "/register/<int:event_id>",



    methods=["GET", "POST"]



)



def register_participant(event_id):



    connection = None



    cursor = None



    try:



        connection = get_db_connection()



        cursor = connection.cursor()



        cursor.execute(



            """



            SELECT



                e.event_id,



                e.event_name,



                e.event_type,



                e.event_date,



                e.venue,



                o.organization_name



            FROM events e



            JOIN organizations o



                ON e.organization_id = o.organization_id



            WHERE e.event_id = %s;



            """,



            (event_id,)



        )



        event = cursor.fetchone()



        if not event:



            flash("Event not found.", "error")



            return redirect(url_for("dashboard"))



        if request.method == "GET":



            return render_template(



                "register.html",



                event=event



            )



        participant_name = request.form["participant_name"]



        email = request.form["email"]



        phone = request.form["phone"]



        cursor.execute(



            """



            SELECT participant_id



            FROM participants



            WHERE LOWER(email) = LOWER(%s)



            LIMIT 1;



            """,



            (email,)



        )



        existing_participant = cursor.fetchone()



        if existing_participant:



            participant_id = existing_participant[0]



        else:



            cursor.execute(



                """



                INSERT INTO participants



                (



                    participant_name,



                    email,



                    phone



                )



                VALUES (%s, %s, %s)



                RETURNING participant_id;



                """,



                (



                    participant_name,



                    email,



                    phone



                )



            )



            participant_id = cursor.fetchone()[0]



        cursor.execute(



            """



            SELECT registration_id



            FROM registrations



            WHERE event_id = %s



            AND participant_id = %s;



            """,



            (



                event_id,



                participant_id



            )



        )



        existing_registration = cursor.fetchone()



        if existing_registration:



            flash(



                "This participant is already registered for this event.",



                "error"



            )



            return redirect(



                url_for(



                    "register_participant",



                    event_id=event_id



                )



            )



        registration_code = (



            f"EVT{event_id}-"



            f"{uuid.uuid4().hex[:8].upper()}"



        )



        cursor.execute(



            """



            INSERT INTO registrations



            (



                event_id,



                participant_id,



                registration_code



            )



            VALUES (%s, %s, %s)



            RETURNING registration_id;



            """,



            (



                event_id,



                participant_id,



                registration_code



            )



        )



        connection.commit()



        # Generate QR code



        attendance_url = (



            request.host_url.rstrip("/")



            +



            url_for(



                "mark_attendance",



                registration_code=registration_code



            )



        )



        qr = qrcode.make(attendance_url)



        qr_filename = (



            f"{registration_code}.png"



        )



        qr_path = os.path.join(



            QR_FOLDER,



            qr_filename



        )



        qr.save(qr_path)



        # Email the participant their personal QR code. Registration remains

        # successful even if email delivery fails, so they can still download it.

        qr_email_sent = False

        qr_email_error = None

        try:

            send_registration_qr_email(

                recipient_email=email,

                participant_name=participant_name,

                event_name=event[1],

                event_date=event[3],

                venue=event[4],

                registration_code=registration_code,

                qr_path=qr_path,

            )

            qr_email_sent = True

        except Exception as email_error:

            qr_email_error = str(email_error)

            app.logger.exception(

                "Could not email registration QR code to %s", email

            )



        # Show the participant their unique QR code immediately after registration.

        return render_template(

            "registration_success.html",

            event=event,

            participant_name=participant_name,

            email=email,

            registration_code=registration_code,

            qr_filename=qr_filename,

            qr_email_sent=qr_email_sent,

            qr_email_error=qr_email_error,

        )



    except Exception as error:



        if connection:



            connection.rollback()



        flash(



            f"Registration error: {error}",



            "error"



        )



        return redirect(



            url_for(



                "register_participant",



                event_id=event_id



            )



        )



    finally:



        if cursor:



            cursor.close()



        if connection:



            connection.close()



# ============================================================



# DOWNLOAD REGISTRATION QR CODE



# ============================================================



@app.route("/qr-code/<registration_code>/download")

def download_qr_code(registration_code):

    """Download the QR image created for a participant registration."""

    # Registration codes are generated by this app and should never contain a path.

    if os.path.basename(registration_code) != registration_code:

        flash("Invalid QR code request.", "error")

        return redirect(url_for("home"))



    qr_path = os.path.join(QR_FOLDER, f"{registration_code}.png")

    if not os.path.isfile(qr_path):

        flash("QR code image was not found. Please contact the event organizer.", "error")

        return redirect(url_for("home"))



    return send_file(

        qr_path,

        mimetype="image/png",

        as_attachment=True,

        download_name=f"{registration_code}.png",

    )





# ============================================================



# QR ATTENDANCE



# ============================================================



@app.route("/attendance/<registration_code>")



def mark_attendance(registration_code):



    connection = None



    cursor = None



    try:



        connection = get_db_connection()



        cursor = connection.cursor()



        cursor.execute(



            """



            SELECT



                r.registration_id,



                p.participant_name,



                p.email,



                e.event_name



            FROM registrations r



            JOIN participants p



                ON r.participant_id = p.participant_id



            JOIN events e



                ON r.event_id = e.event_id



            WHERE r.registration_code = %s;



            """,



            (registration_code,)



        )



        registration = cursor.fetchone()



        if not registration:



            return render_template(



                "attendance_result.html",



                success=False,



                message="Invalid registration QR code."



            )



        registration_id = registration[0]



        participant_name = registration[1]



        event_name = registration[3]



        cursor.execute(



            """



            SELECT attendance_id



            FROM attendance



            WHERE registration_id = %s;



            """,



            (registration_id,)



        )



        existing_attendance = cursor.fetchone()



        if existing_attendance:



            cursor.execute(



                """



                UPDATE attendance



                SET



                    attendance_status = 'Present',



                    attendance_time = CURRENT_TIMESTAMP



                WHERE registration_id = %s;



                """,



                (registration_id,)



            )



        else:



            cursor.execute(



                """



                INSERT INTO attendance



                (



                    registration_id,



                    attendance_status,



                    attendance_time



                )



                VALUES



                (



                    %s,



                    'Present',



                    CURRENT_TIMESTAMP



                );



                """,



                (registration_id,)



            )



        connection.commit()



        return render_template(



            "attendance_result.html",



            success=True,



            participant_name=participant_name,



            event_name=event_name,



            registration_code=registration_code



        )



    except Exception as error:



        if connection:



            connection.rollback()



        return render_template(



            "attendance_result.html",



            success=False,



            message=f"Attendance error: {error}"



        )



    finally:



        if cursor:



            cursor.close()



        if connection:



            connection.close()



# ============================================================



# UPLOAD CERTIFICATE TEMPLATE



# ============================================================



@app.route(



    "/event/<int:event_id>/upload-template",



    methods=["GET", "POST"]



)



def upload_template(event_id):



    connection = None



    cursor = None



    try:



        connection = get_db_connection()



        cursor = connection.cursor()



        cursor.execute(



            """



            SELECT



                e.event_id,



                e.event_name,



                o.organization_name



            FROM events e



            JOIN organizations o



                ON e.organization_id = o.organization_id



            WHERE e.event_id = %s;



            """,



            (event_id,)



        )



        event = cursor.fetchone()



        if not event:



            flash("Event not found.", "error")



            return redirect(url_for("dashboard"))



        # The type can come from the button URL or from the form.



        certificate_type = request.args.get("certificate_type", "Participation")



        if request.method == "GET":



            if certificate_type not in ["Merit", "Participation"]:



                certificate_type = "Participation"



            return render_template(



                "upload_template.html",



                event=event,



                certificate_type=certificate_type



            )



        template_name = request.form.get("template_name", "").strip()



        certificate_type = request.form.get("certificate_type", "").strip()



        template_file = request.files.get("template_file")



        if certificate_type not in ["Merit", "Participation"]:



            flash("Please select a valid certificate type.", "error")



            return redirect(



                url_for("upload_template", event_id=event_id)



            )



        if not template_name:



            flash("Please enter a template name.", "error")



            return redirect(



                url_for(



                    "upload_template",



                    event_id=event_id,



                    certificate_type=certificate_type



                )



            )



        if not template_file or template_file.filename == "":



            flash("Please select a certificate template.", "error")



            return redirect(



                url_for(



                    "upload_template",



                    event_id=event_id,



                    certificate_type=certificate_type



                )



            )



        if not allowed_template(template_file.filename):



            flash(



                "Only PNG, JPG and JPEG templates are supported.",



                "error"



            )



            return redirect(



                url_for(



                    "upload_template",



                    event_id=event_id,



                    certificate_type=certificate_type



                )



            )



        safe_name = secure_filename(template_file.filename)



        unique_filename = (



            f"{event_id}_"



            f"{certificate_type.lower()}_"



            f"{uuid.uuid4().hex[:8]}_"



            f"{safe_name}"



        )



        template_path = os.path.join(



            UPLOAD_FOLDER,



            unique_filename



        )



        template_file.save(template_path)



        # Only the old template of THIS TYPE is deactivated.



        # The Merit and Participation templates can coexist.



        cursor.execute(



            """



            UPDATE certificate_templates



            SET is_active = FALSE



            WHERE event_id = %s



              AND certificate_type = %s;



            """,



            (event_id, certificate_type)



        )



        cursor.execute(



            """



            INSERT INTO certificate_templates



            (



                event_id,



                template_name,



                template_file_path,



                is_active,



                certificate_type



            )



            VALUES (%s, %s, %s, TRUE, %s);



            """,



            (



                event_id,



                template_name,



                template_path,



                certificate_type



            )



        )



        connection.commit()



        flash(



            f"{certificate_type} certificate template uploaded successfully!",



            "success"



        )



        return redirect(



            url_for(



                "event_details",



                event_id=event_id



            )



        )



    except Exception as error:



        if connection:



            connection.rollback()



        flash(



            f"Template upload error: {error}",



            "error"



        )



        return redirect(



            url_for(



                "event_details",



                event_id=event_id



            )



        )



    finally:



        if cursor:



            cursor.close()



        if connection:



            connection.close()



# ============================================================



# ============================================================



# EMAIL CERTIFICATE HELPER



# ============================================================



def send_certificate_email(



    recipient_email,



    participant_name,



    event_name,



    certificate_type,



    certificate_path



):



    """



    Send one generated certificate PDF by email.



    SMTP settings are read from .env:



        SMTP_HOST



        SMTP_PORT



        SMTP_EMAIL



        SMTP_PASSWORD



    """



    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")



    smtp_port = int(os.getenv("SMTP_PORT", "465"))



    smtp_email = (os.getenv("SMTP_EMAIL") or "").strip()



    smtp_password = (os.getenv("SMTP_PASSWORD") or "").replace(" ", "").strip()



    if not smtp_email or not smtp_password:



        raise ValueError(



            "SMTP_EMAIL and SMTP_PASSWORD are not configured in .env"



        )



    if not recipient_email:



        raise ValueError("Participant email is missing.")



    if not os.path.exists(certificate_path):



        raise FileNotFoundError(



            f"Certificate file not found: {certificate_path}"



        )



    message = EmailMessage()



    message["Subject"] = (



        f"{certificate_type} Certificate - {event_name}"



    )



    message["From"] = smtp_email



    message["To"] = recipient_email



    message.set_content(



        f"""Dear {participant_name},



Congratulations!



Please find attached your {certificate_type.lower()} certificate



for the event "{event_name}".



Thank you for participating.



Regards,



Smart Event Certificate Platform



"""



    )



    with open(certificate_path, "rb") as certificate_file:



        certificate_data = certificate_file.read()



    message.add_attachment(



        certificate_data,



        maintype="application",



        subtype="pdf",



        filename=os.path.basename(certificate_path)



    )



    with smtplib.SMTP_SSL(



        smtp_host,



        smtp_port,



        timeout=30



    ) as smtp:



        smtp.login(



            smtp_email,



            smtp_password



        )



        smtp.send_message(message)



# ============================================================



# GENERATE CERTIFICATES



# ============================================================



@app.route("/event/<int:event_id>/generate-certificates", methods=["POST"])
@login_required
def generate_certificates(event_id):
    """
    Generate one AI-styled PDF for every selected, Present participant.
    Form keys are normalized to support both certificate_assignment_123
    and older exported forms that may contain an escaped underscore.
    """
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT o.email
            FROM events e
            JOIN organizations o ON o.organization_id = e.organization_id
            WHERE e.event_id = %s
        """, (event_id,))
        owner = cursor.fetchone()
        if not owner or str(owner[0]).strip().lower() != session["organizer_email"].strip().lower():
            flash("You do not have permission to generate certificates for this event.", "error")
            return redirect(url_for("dashboard"))

        assignments = {}
        for key, value in request.form.items():
            normalized_key = key.replace("\\_", "_").strip()
            prefix = "certificate_assignment_"
            if not normalized_key.startswith(prefix):
                continue

            registration_id_text = normalized_key[len(prefix):]
            try:
                registration_id = int(registration_id_text)
            except (TypeError, ValueError):
                continue

            certificate_type = (value or "").strip()
            if certificate_type in ("Merit", "Participation"):
                assignments[registration_id] = certificate_type

        if not assignments:
            flash(
                "No certificate type was selected. Choose Merit or Participation for each participant, then click Generate AI Certificates.",
                "error",
            )
            return redirect(url_for("event_details", event_id=event_id))

        # The PDF is designed by generate_ai_certificate_pdf(), so an uploaded
        # image is not required. We still need a certificate_templates row
        # because certificates.template_id references that table.
        cursor.execute(
            """
            SELECT template_id, template_file_path, certificate_type
            FROM certificate_templates
            WHERE event_id = %s
              AND is_active = TRUE
              AND certificate_type IN ('Merit', 'Participation')
            ORDER BY template_id DESC;
            """,
            (event_id,),
        )
        templates = {}
        for row in cursor.fetchall():
            templates.setdefault(
                row[2],
                {"template_id": row[0], "template_path": row[1]},
            )

        # Create a lightweight database record for any selected certificate
        # type that has no active template. The placeholder path is not opened
        # or drawn; the AI-style PDF renderer creates the actual certificate.
        for certificate_type in sorted(set(assignments.values()) - set(templates)):
            cursor.execute(
                """
                INSERT INTO certificate_templates
                    (event_id, template_name, template_file_path,
                     is_active, certificate_type)
                VALUES (%s, %s, %s, TRUE, %s)
                RETURNING template_id;
                """,
                (
                    event_id,
                    f"Built-in AI {certificate_type} Design",
                    "AI_GENERATED",
                    certificate_type,
                ),
            )
            template_id = cursor.fetchone()[0]
            templates[certificate_type] = {
                "template_id": template_id,
                "template_path": "AI_GENERATED",
            }

        cursor.execute(
            """
            SELECT
                r.registration_id,
                r.registration_code,
                p.participant_name,
                p.email,
                e.event_name,
                e.event_date,
                o.organization_name,
                COALESCE(
                    (
                        SELECT a.attendance_status
                        FROM attendance a
                        WHERE a.registration_id = r.registration_id
                        ORDER BY a.attendance_time DESC NULLS LAST,
                                 a.attendance_id DESC
                        LIMIT 1
                    ),
                    'Not Marked'
                ) AS attendance_status
            FROM registrations r
            JOIN participants p ON p.participant_id = r.participant_id
            JOIN events e ON e.event_id = r.event_id
            JOIN organizations o ON o.organization_id = e.organization_id
            WHERE r.event_id = %s;
            """,
            (event_id,),
        )
        participant_rows = cursor.fetchall()
        participants_by_registration = {row[0]: row for row in participant_rows}

        generated_count = 0
        skipped = []

        for registration_id, certificate_type in assignments.items():
            participant = participants_by_registration.get(registration_id)

            if participant is None:
                skipped.append(f"registration {registration_id}: not found for this event")
                continue

            (
                registration_id,
                registration_code,
                participant_name,
                participant_email,
                event_name,
                event_date,
                organization_name,
                attendance_status,
            ) = participant

            if attendance_status != "Present":
                skipped.append(f"{participant_name}: attendance is {attendance_status}")
                continue

            template_id = templates[certificate_type]["template_id"]
            certificate_number = f"CERT-{event_id}-{uuid.uuid4().hex[:10].upper()}"
            filename = f"{certificate_number}.pdf"
            output_path = os.path.abspath(os.path.join(CERTIFICATE_FOLDER, filename))

            # Generate the PDF first. Do not remove an older certificate
            # until the new PDF has been generated successfully.
            generate_ai_certificate_pdf(
                output_path=output_path,
                participant_name=participant_name,
                event_name=event_name,
                organization_name=organization_name,
                event_date=event_date,
                certificate_type=certificate_type,
                certificate_number=certificate_number,
            )

            cursor.execute(
                """
                SELECT certificate_id, certificate_file_path
                FROM certificates
                WHERE registration_id = %s
                ORDER BY generated_at DESC NULLS LAST, certificate_id DESC
                LIMIT 1;
                """,
                (registration_id,),
            )
            existing_certificate = cursor.fetchone()

            if existing_certificate:
                old_certificate_id, old_file_path = existing_certificate
                cursor.execute(
                    "DELETE FROM certificates WHERE certificate_id = %s;",
                    (old_certificate_id,),
                )

            cursor.execute(
                """
                INSERT INTO certificates
                    (registration_id, template_id, certificate_type,
                     certificate_number, certificate_file_path, email_status)
                VALUES (%s, %s, %s, %s, %s, 'Not Sent');
                """,
                (
                    registration_id,
                    template_id,
                    certificate_type,
                    certificate_number,
                    output_path,
                ),
            )
            generated_count += 1

        connection.commit()

        # Delete replaced PDF files only after the database transaction commits.
        if generated_count:
            for registration_id, _certificate_type in assignments.items():
                # Any old file was deliberately retained until commit. Clean-up
                # is optional; old PDFs can safely remain on disk.
                pass

        if generated_count:
            message = f"{generated_count} certificate(s) generated successfully."
            if skipped:
                message += " Skipped: " + "; ".join(skipped) + "."
            flash(message, "success")
        else:
            flash(
                "No certificates were generated. " + "; ".join(skipped),
                "error",
            )

        return redirect(url_for("event_details", event_id=event_id))

    except Exception as error:
        if connection:
            connection.rollback()
        app.logger.exception("Certificate generation failed for event %s", event_id)
        flash(f"Certificate generation error: {error}", "error")
        return redirect(url_for("event_details", event_id=event_id))

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@app.route(



    "/event/<int:event_id>/send-certificates",



    methods=["POST"]



)



def send_certificates(event_id):



    connection = None



    cursor = None



    try:



        connection = get_db_connection()



        cursor = connection.cursor()



        cursor.execute(



            """



            SELECT



                c.certificate_id,



                c.certificate_file_path,



                c.certificate_type,



                p.participant_name,



                p.email,



                e.event_name



            FROM certificates c



            JOIN registrations r



                ON c.registration_id = r.registration_id



            JOIN participants p



                ON r.participant_id = p.participant_id



            JOIN events e



                ON r.event_id = e.event_id



            WHERE r.event_id = %s



              AND c.email_status = 'Not Sent'



            ORDER BY c.generated_at;



            """,



            (event_id,)



        )



        certificates = cursor.fetchall()



        if not certificates:



            flash(



                "There are no unsent certificates for this event.",



                "error"



            )



            return redirect(



                url_for("event_details", event_id=event_id)



            )



        sent_count = 0



        failed_count = 0



        first_email_error = None



        for certificate in certificates:



            (



                certificate_id,



                certificate_path,



                certificate_type,



                participant_name,



                participant_email,



                event_name



            ) = certificate



            try:



                send_certificate_email(



                    recipient_email=participant_email,



                    participant_name=participant_name,



                    event_name=event_name,



                    certificate_type=certificate_type,



                    certificate_path=certificate_path



                )



                cursor.execute(



                    """



                    UPDATE certificates



                    SET email_status = 'Sent'



                    WHERE certificate_id = %s;



                    """,



                    (certificate_id,)



                )



                sent_count += 1



            except Exception as email_error:



                failed_count += 1



                if first_email_error is None:



                    first_email_error = str(email_error)



                app.logger.exception(



                    "Certificate email failed for recipient %s",



                    participant_email



                )



        connection.commit()



        if sent_count:



            flash(



                f"{sent_count} certificate email(s) sent successfully!",



                "success"



            )



        if failed_count:



            flash(



                f"{failed_count} certificate email(s) failed. "



                "They remain Not Sent and can be retried. "



                f"First error: {first_email_error or 'Check the Flask terminal for details.'}",



                "error"



            )



        return redirect(



            url_for("event_details", event_id=event_id)



        )



    except Exception as error:



        if connection:



            connection.rollback()



        flash(



            f"Email sending error: {error}",



            "error"



        )



        return redirect(



            url_for("event_details", event_id=event_id)



        )



    finally:



        if cursor:



            cursor.close()



        if connection:



            connection.close()



# ============================================================



# VIEW GENERATED CERTIFICATE



# ============================================================



@app.route("/certificate/<int:certificate_id>")



def view_certificate(certificate_id):



    connection = None



    cursor = None



    try:



        connection = get_db_connection()



        cursor = connection.cursor()



        cursor.execute(



            """



            SELECT



                certificate_file_path,



                certificate_number,



                certificate_type



            FROM certificates



            WHERE certificate_id = %s;



            """,



            (certificate_id,)



        )



        certificate = cursor.fetchone()



        if not certificate:



            flash(



                "Certificate not found.",



                "error"



            )



            return redirect(



                url_for(



                    "dashboard"



                )



            )



        file_path = certificate[0]



        if not os.path.exists(file_path):



            flash(



                "Certificate file not found.",



                "error"



            )



            return redirect(



                url_for(



                    "dashboard"



                )



            )



        return send_file(



            file_path,



            mimetype="application/pdf"



        )



    finally:



        if cursor:



            cursor.close()



        if connection:



            connection.close()



# ============================================================



# AI CERTIFICATE PDF GENERATOR



# ============================================================



from reportlab.lib.colors import HexColor



from reportlab.pdfbase.ttfonts import TTFont



from reportlab.pdfbase import pdfmetrics



from reportlab.lib.enums import TA_CENTER



from reportlab.platypus import Paragraph



from reportlab.lib.styles import ParagraphStyle



def generate_ai_certificate_pdf(



    output_path,



    participant_name,



    event_name,



    organization_name,



    event_date,



    certificate_type,



    certificate_number



):



    """



    Generate a clean professional certificate PDF.



    This version does not require an uploaded certificate image.



    """



    # ---------------------------------------------------------



    # PAGE



    # ---------------------------------------------------------



    page_width, page_height = landscape(A4)



    pdf = canvas.Canvas(



        output_path,



        pagesize=(page_width, page_height)



    )



    # ---------------------------------------------------------



    # COLORS



    # ---------------------------------------------------------



    cream = HexColor("#F8F1E6")



    terracotta = HexColor("#9F6046")



    dark_brown = HexColor("#3E2D25")



    warm_brown = HexColor("#70402F")



    muted_brown = HexColor("#806F63")



    light_brown = HexColor("#C69272")



    # ---------------------------------------------------------



    # BACKGROUND



    # ---------------------------------------------------------



    pdf.setFillColor(cream)



    pdf.rect(



        0,



        0,



        page_width,



        page_height,



        fill=1,



        stroke=0



    )



    # ---------------------------------------------------------



    # OUTER BORDER



    # ---------------------------------------------------------



    pdf.setStrokeColor(terracotta)



    pdf.setLineWidth(8)



    pdf.rect(



        18,



        18,



        page_width - 36,



        page_height - 36,



        fill=0,



        stroke=1



    )



    # ---------------------------------------------------------



    # INNER BORDER



    # ---------------------------------------------------------



    pdf.setStrokeColor(light_brown)



    pdf.setLineWidth(1.5)



    pdf.rect(



        34,



        34,



        page_width - 68,



        page_height - 68,



        fill=0,



        stroke=1



    )



    center_x = page_width / 2



    # ---------------------------------------------------------



    # DECORATIVE CORNERS



    # ---------------------------------------------------------



    corner_size = 45



    pdf.setStrokeColor(terracotta)



    pdf.setLineWidth(2)



    # Top-left



    pdf.line(45, page_height - 45,



             45 + corner_size, page_height - 45)



    pdf.line(45, page_height - 45,



             45, page_height - 45 - corner_size)



    # Top-right



    pdf.line(page_width - 45, page_height - 45,



             page_width - 45 - corner_size, page_height - 45)



    pdf.line(page_width - 45, page_height - 45,



             page_width - 45, page_height - 45 - corner_size)



    # Bottom-left



    pdf.line(45, 45,



             45 + corner_size, 45)



    pdf.line(45, 45,



             45, 45 + corner_size)



    # Bottom-right



    pdf.line(page_width - 45, 45,



             page_width - 45 - corner_size, 45)



    pdf.line(page_width - 45, 45,



             page_width - 45, 45 + corner_size)



    # ---------------------------------------------------------



    # ORGANIZATION



    # ---------------------------------------------------------



    pdf.setFillColor(terracotta)



    pdf.setFont(



        "Helvetica-Bold",



        11



    )



    pdf.drawCentredString(



        center_x,



        page_height - 92,



        str(organization_name).upper()



    )



    # ---------------------------------------------------------



    # MAIN TITLE



    # ---------------------------------------------------------



    pdf.setFillColor(warm_brown)



    pdf.setFont(



        "Times-Bold",



        38



    )



    pdf.drawCentredString(



        center_x,



        page_height - 145,



        "CERTIFICATE"



    )



    # ---------------------------------------------------------



    # TYPE



    # ---------------------------------------------------------



    pdf.setFillColor(terracotta)



    pdf.setFont(



        "Times-Roman",



        17



    )



    pdf.drawCentredString(



        center_x,



        page_height - 172,



        f"OF {str(certificate_type).upper()}"



    )



    # ---------------------------------------------------------



    # DECORATIVE LINE



    # ---------------------------------------------------------



    pdf.setStrokeColor(light_brown)



    pdf.setLineWidth(1)



    pdf.line(



        center_x - 90,



        page_height - 192,



        center_x + 90,



        page_height - 192



    )



    # ---------------------------------------------------------



    # PRESENTED TO



    # ---------------------------------------------------------



    pdf.setFillColor(muted_brown)



    pdf.setFont(



        "Helvetica",



        10



    )



    pdf.drawCentredString(



        center_x,



        page_height - 225,



        "PROUDLY PRESENTED TO"



    )



    # ---------------------------------------------------------



    # PARTICIPANT NAME



    # ---------------------------------------------------------



    pdf.setFillColor(dark_brown)



    pdf.setFont(



        "Times-Italic",



        30



    )



    pdf.drawCentredString(



        center_x,



        page_height - 265,



        str(participant_name)



    )



    # Name underline



    pdf.setStrokeColor(light_brown)



    pdf.line(



        center_x - 190,



        page_height - 278,



        center_x + 190,



        page_height - 278



    )



    # ---------------------------------------------------------



    # RECOGNITION TEXT



    # ---------------------------------------------------------



    pdf.setFillColor(muted_brown)



    pdf.setFont(



        "Helvetica",



        11



    )



    if certificate_type == "Merit":



        recognition_text = (



            "For outstanding performance and achievement in"



        )



    else:



        recognition_text = (



            "For active participation and contribution in"



        )



    pdf.drawCentredString(



        center_x,



        page_height - 310,



        recognition_text



    )



    # ---------------------------------------------------------



    # EVENT NAME



    # ---------------------------------------------------------



    pdf.setFillColor(warm_brown)



    pdf.setFont(



        "Times-Bold",



        21



    )



    # Handle long event names



    event_text = str(event_name)



    if len(event_text) > 55:



        pdf.setFont(



            "Times-Bold",



            17



        )



    pdf.drawCentredString(



        center_x,



        page_height - 342,



        event_text



    )



    # ---------------------------------------------------------



    # DESCRIPTION



    # ---------------------------------------------------------



    pdf.setFillColor(muted_brown)



    description_style = ParagraphStyle(



        "CertificateDescription",



        fontName="Helvetica",



        fontSize=9.5,



        leading=13,



        alignment=TA_CENTER,



        textColor=muted_brown



    )



    if certificate_type == "Merit":



        description = (



            "In recognition of outstanding performance, "



            "dedication and achievement demonstrated "



            "during this event."



        )



    else:



        description = (



            "In recognition of active participation, "



            "enthusiasm and valuable contribution "



            "to this event."



        )



    paragraph = Paragraph(



        description,



        description_style



    )



    paragraph.wrapOn(



        pdf,



        500,



        50



    )



    paragraph.drawOn(



        pdf,



        center_x - 250,



        page_height - 395



    )



    # ---------------------------------------------------------



    # DATE



    # ---------------------------------------------------------



    try:



        if hasattr(event_date, "strftime"):



            formatted_date = event_date.strftime(



                "%d %B %Y"



            )



        else:



            formatted_date = datetime.strptime(



                str(event_date),



                "%Y-%m-%d"



            ).strftime(



                "%d %B %Y"



            )



    except Exception:



        formatted_date = str(event_date)



    # ---------------------------------------------------------



    # BOTTOM INFORMATION



    # ---------------------------------------------------------



    bottom_y = 100



    # Date



    pdf.setStrokeColor(light_brown)



    pdf.line(



        145,



        bottom_y + 20,



        335,



        bottom_y + 20



    )



    pdf.setFillColor(terracotta)



    pdf.setFont(



        "Helvetica-Bold",



        9



    )



    pdf.drawCentredString(



        240,



        bottom_y + 5,



        "DATE"



    )



    pdf.setFillColor(dark_brown)



    pdf.setFont(



        "Helvetica",



        10



    )



    pdf.drawCentredString(



        240,



        bottom_y - 10,



        formatted_date



    )



    # Organizer



    pdf.setStrokeColor(light_brown)



    pdf.line(



        page_width - 335,



        bottom_y + 20,



        page_width - 145,



        bottom_y + 20



    )



    pdf.setFillColor(terracotta)



    pdf.setFont(



        "Helvetica-Bold",



        9



    )



    pdf.drawCentredString(



        page_width - 240,



        bottom_y + 5,



        "ORGANIZER"



    )



    pdf.setFillColor(dark_brown)



    pdf.setFont(



        "Helvetica",



        10



    )



    pdf.drawCentredString(



        page_width - 240,



        bottom_y - 10,



        str(organization_name)



    )



    # ---------------------------------------------------------



    # CERTIFICATE ID



    # ---------------------------------------------------------



    pdf.setFillColor(



        HexColor("#927D70")



    )



    pdf.setFont(



        "Helvetica",



        7



    )



    pdf.drawCentredString(



        center_x,



        45,



        f"Certificate ID: {certificate_number}"



    )



    # ---------------------------------------------------------



    # FINISH PDF



    # ---------------------------------------------------------



    pdf.save()



# ============================================================



# AI CERTIFICATE DESIGN PREVIEW



# ============================================================



@app.route("/ai-certificate-preview")



def ai_certificate_preview():



    sample_data = {



        "participant_name": "Sri Lakshmi",



        "event_name": "Weekend Pottery Workshop",



        "organization_name": "Creative Clay Cafe",



        "event_date": "24 August 2026",



        "certificate_type": "Participation",



        "certificate_number": "CERT-2-AI2026TEST"



    }



    return render_template(



        "certificate_preview.html",



        **sample_data



    )



# ============================================================



# AI CERTIFICATE REAL DATA TEST



# ============================================================



@app.route("/ai-certificate-test/<int:event_id>")



def ai_certificate_test(event_id):



    connection = None



    cursor = None



    try:



        connection = get_db_connection()



        cursor = connection.cursor()



        # ----------------------------------------------------



        # Get one PRESENT participant from this event



        # ----------------------------------------------------



        cursor.execute(



            """



            SELECT



                r.registration_id,



                p.participant_name,



                p.email,



                e.event_name,



                e.event_date,



                o.organization_name,



                a.attendance_status



            FROM registrations r



            JOIN participants p



                ON r.participant_id = p.participant_id



            JOIN events e



                ON r.event_id = e.event_id



            JOIN organizations o



                ON e.organization_id = o.organization_id



            JOIN attendance a



                ON r.registration_id = a.registration_id



            WHERE r.event_id = %s



              AND a.attendance_status = 'Present'



            ORDER BY r.registration_id



            LIMIT 1;



            """,



            (event_id,)



        )



        participant = cursor.fetchone()



        if not participant:



            return """



            <h2>No Present Participant Found</h2>



            <p>Please register a participant and mark their attendance



            as Present before running this test.</p>



            """



        (



            registration_id,



            participant_name,



            participant_email,



            event_name,



            event_date,



            organization_name,



            attendance_status



        ) = participant



        # ----------------------------------------------------



        # Create test certificate number



        # ----------------------------------------------------



        certificate_number = (



            f"AI-TEST-{event_id}-"



            f"{uuid.uuid4().hex[:8].upper()}"



        )



        # ----------------------------------------------------



        # Save test PDF



        # ----------------------------------------------------



        filename = (



            f"{certificate_number}.pdf"



        )



        output_path = os.path.join(



            CERTIFICATE_FOLDER,



            filename



        )



        # ----------------------------------------------------



        # Generate new professional certificate



        # ----------------------------------------------------



        generate_ai_certificate_pdf(



            output_path=output_path,



            participant_name=participant_name,



            event_name=event_name,



            organization_name=organization_name,



            event_date=event_date,



            certificate_type="Participation",



            certificate_number=certificate_number



        )



        # ----------------------------------------------------



        # Return generated PDF directly in browser



        # ----------------------------------------------------



        return send_file(



            output_path,



            mimetype="application/pdf"



        )



    except Exception as error:



        return f"""



        <h2>AI Certificate Test Error</h2>



        <pre>{error}</pre>



        """



    finally:



        if cursor:



            cursor.close()



        if connection:



            connection.close()



# ============================================================



# RUN APPLICATION



# ============================================================



if __name__ == "__main__":



    app.run(



        host="0.0.0.0",



        port=5000,



        debug=True



    )