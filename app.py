from flask import Flask, render_template, request, redirect, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "smartcampus"


# ================= USER LOGIN =================
@app.route("/", methods=["GET","POST"])
def login():

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("campus.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email,password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            session["user"] = email
            return redirect("/dashboard")
        else:
            flash("Invalid Login")
            return redirect("/")

    return render_template("login.html")


# ================= REGISTER =================
@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("campus.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users(email,password) VALUES(?,?)",
                (email,password)
            )
            conn.commit()
            conn.close()

            flash("Registration Successful")
            return redirect("/")

        except:
            conn.close()
            flash("Email already exists")
            return redirect("/register")

    return render_template("register.html")


# ================= USER DASHBOARD =================
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("campus.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM bookings WHERE user=?", (session["user"],))
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bookings WHERE status='Booked' AND user=?", (session["user"],))
    active = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bookings WHERE status='Cancelled' AND user=?", (session["user"],))
    cancelled = cursor.fetchone()[0]

    conn.close()

    return render_template("dashboard.html",
                           total=total,
                           active=active,
                           cancelled=cancelled)


# ================= BOOK RESOURCE =================
@app.route("/book", methods=["GET","POST"])
def book():

    if "user" not in session:
        return redirect("/")

    if request.method == "POST":

        resource = request.form["resource"]
        date = request.form["date"]
        time = request.form["time"]
        members = request.form["members"]

        conn = sqlite3.connect("campus.db")
        cursor = conn.cursor()

        # DOUBLE BOOKING CHECK
        cursor.execute(
            "SELECT * FROM bookings WHERE resource=? AND date=? AND time=? AND status='Booked'",
            (resource,date,time)
        )

        conflict = cursor.fetchone()

        if conflict:
            conn.close()
            flash("Slot already booked")
            return redirect("/book")

        cursor.execute(
            "INSERT INTO bookings(user,resource,date,time,members,status) VALUES(?,?,?,?,?,?)",
            (session["user"],resource,date,time,members,"Booked")
        )

        conn.commit()
        conn.close()

        flash("Booking Successful")
        return redirect("/book")

    return render_template("book.html")


# ================= VIEW BOOKINGS =================
@app.route("/view_bookings")
def view_bookings():

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("campus.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM bookings
        WHERE user=?
        ORDER BY date,time
    """,(session["user"],))

    bookings = cursor.fetchall()
    conn.close()

    return render_template("view_bookings.html", bookings=bookings)


# ================= CANCEL BOOKING =================
@app.route("/cancel_booking/<int:id>")
def cancel_booking(id):

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("campus.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE bookings SET status='Cancelled' WHERE id=? AND user=?",
        (id,session["user"])
    )

    conn.commit()
    conn.close()

    flash("Booking Cancelled Successfully")
    return redirect("/view_bookings")


# ================= USER LOGOUT =================
@app.route("/logout")
def logout():
    session.pop("user",None)
    return redirect("/")


# ================= ADMIN LOGIN =================
@app.route("/admin_login", methods=["GET","POST"])
def admin_login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("campus.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM admin WHERE username=? AND password=?",
            (username,password)
        )

        admin = cursor.fetchone()
        conn.close()

        if admin:
            session["admin"] = username
            return redirect("/admin_dashboard")
        else:
            flash("Invalid Admin Login")
            return redirect("/admin_login")

    return render_template("admin_login.html")


# ================= ADMIN DASHBOARD =================
@app.route("/admin_dashboard")
def admin_dashboard():

    if "admin" not in session:
        return redirect("/admin_login")

    conn = sqlite3.connect("campus.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM bookings")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bookings WHERE status='Booked'")
    active = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bookings WHERE status='Cancelled'")
    cancelled = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM bookings ORDER BY date,time")
    bookings = cursor.fetchall()

    conn.close()

    return render_template(
        "admin_dashboard.html",
        total=total,
        active=active,
        cancelled=cancelled,
        bookings=bookings
    )
# Paste These Routes in `app.py`

@app.route("/admin_resources")
def admin_resources():

    if "admin" not in session:
        return redirect("/admin_login")

    conn = sqlite3.connect("campus.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM resources")
    resources = cursor.fetchall()

    conn.close()

    return render_template("admin_resources.html", resources=resources)


@app.route("/add_resource", methods=["GET", "POST"])
def add_resource():

    if "admin" not in session:
        return redirect("/admin_login")

    if request.method == "POST":
        name = request.form["name"]
        type = request.form["type"]
        capacity = request.form["capacity"]
        location = request.form["location"]

        conn = sqlite3.connect("campus.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO resources(name,type,capacity,location) VALUES(?,?,?,?)",
            (name, type, capacity, location)
        )

        conn.commit()
        conn.close()

        flash("Resource added successfully")
        return redirect("/admin_resources")

    return render_template("add_resource.html")


@app.route("/delete_resource/<int:id>")
def delete_resource(id):

    if "admin" not in session:
        return redirect("/admin_login")

    conn = sqlite3.connect("campus.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM resources WHERE id=?", (id,))

    conn.commit()
    conn.close()

    flash("Resource deleted successfully")
    return redirect("/admin_resources")

# ================= ADMIN LOGOUT =================
@app.route("/admin_logout")
def admin_logout():
    session.pop("admin",None)
    return redirect("/admin_login")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)