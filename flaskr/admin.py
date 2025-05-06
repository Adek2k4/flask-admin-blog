from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from flaskr.db import get_db
from flaskr.decorators import admin_required
from werkzeug.security import generate_password_hash


bp = Blueprint("admin", __name__, url_prefix="/admin")

# Widok do listy użytkowników
@bp.route("/users")
@admin_required
def list_users():
    db = get_db()
    users = db.execute(
        "SELECT id, username, is_admin FROM user WHERE id != ?", (g.user["id"],)
    ).fetchall()

    # Pobierz posty pogrupowane po author_id
    posts_by_user = {}
    for user in users:
        posts = db.execute(
            "SELECT id, title FROM post WHERE author_id = ?", (user["id"],)
        ).fetchall()
        posts_by_user[user["id"]] = posts

    return render_template("admin/users.html", users=users, posts_by_user=posts_by_user)


# Funkcja do usuwania użytkownika i jego postów
@bp.route("/delete_user/<int:user_id>", methods=("POST",))
@admin_required
def delete_user(user_id):
    db = get_db()

    # Usuń posty użytkownika
    db.execute("DELETE FROM post WHERE author_id = ?", (user_id,))

    # Usuń użytkownika
    db.execute("DELETE FROM user WHERE id = ?", (user_id,))
    db.commit()

    flash("Użytkownik i jego posty zostały usunięte.")
    return redirect(url_for("admin.list_users"))

# Funkcja do dodawania użytkownika
@bp.route("/add_user", methods=("GET", "POST"))
@admin_required
def add_user():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        is_admin = request.form.get("is_admin") == "on"

        # HASHUJEMY hasło przed zapisem
        hashed_password = generate_password_hash(password)

        db = get_db()
        db.execute(
            "INSERT INTO user (username, password, is_admin) VALUES (?, ?, ?)",
            (username, hashed_password, is_admin),
        )
        db.commit()
        flash("Nowy użytkownik został dodany.")
        return redirect(url_for("admin.list_users"))

    return render_template("admin/add_user.html")
  
# Funkcja do usuwania postu
@bp.route("/delete_post/<int:post_id>", methods=("POST",))
@admin_required
def delete_post(post_id):
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (post_id,))
    db.commit()

    flash("Post został usunięty.")
    return redirect(url_for("blog.index"))
