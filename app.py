from google import genai
from google.genai import errors
from dotenv import load_dotenv, find_dotenv
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import os, sys, sqlite3
from helpers import generate_grammar_questions, generate_reading_questions, validate_environment, login_required, get_username, update_user_streak

# Validate environment variables
if not validate_environment():
    sys.exit("ERROR: Missing or invalid environment variables")

# Load environment variables
_ = load_dotenv(find_dotenv())

# Create Flask app, get the secret key from the environment variable
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Config Session
app.config["SESSION_PERMANENT"] = True # Session persists even after browser is closed
app.config["SESSION_TYPE"] = "filesystem" # Store session data in the filesystem on server
app.config["SESSION_FILE_DIR"] = os.path.join(app.root_path, "flask_session") # Directory to store session data
app.config["SESSION_FILE_THRESHOLD"] = 500 # The maximum number of session files before cleanup
Session(app)

# Setup database connection, create database file if it doesn't exist
db_file = "database.db"
conn = None

if not os.path.exists(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            streak INTEGER DEFAULT 0,
            last_test_date TEXT DEFAULT NULL,
            grammar_history TEXT DEFAULT '[]',
            reading_history TEXT DEFAULT '[]'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            choices TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            explanation TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, question)
        )
    """)
    conn.commit()
    conn.close()

# Home page
@app.route("/", methods=["GET"])
def home():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    else:
        return render_template("index.html")
    
# Dashboard page
@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    try:
        conn = sqlite3.connect(db_file)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT streak FROM users WHERE id = ?", (session["user_id"],))
            row = cursor.fetchone()
            if row:
                streak = row[0]
            else:
                streak = 0
            return render_template("dashboard.html", streak=streak, username=get_username(session["user_id"]))
    except sqlite3.Error as e:
        flash(f"Error retrieving user data: {e}", "danger")
        return render_template("dashboard.html", streak=0, username="Guest")
    finally:
        conn.close()

# Generate grammar questions page
@app.route("/grammar_test", methods=["GET", "POST"])
def grammar_test():
    if request.method == "GET":
        try:
            questions = generate_grammar_questions()
            flash("Successfully generated questions", "success")
            return render_template("grammar_test.html", questions=questions)
        except Exception as e:
            flash(f"Error generating questions: {e}", "danger")
            return redirect(url_for("home"))
    else:
        """Check if the session has current test data"""
        if "current_grammar_test" not in session:
            flash("Session expired, please try again", "danger")
            return redirect(url_for("home"))
        
        questions = session["current_grammar_test"]["GRAMMAR_DATA"]
        if not questions:
            flash("Error retrieving questions", "danger")
            return redirect(url_for("home"))
        
        """Handle form submission"""
        total_questions = len(questions)
        user_answers = [request.form.get(f"answers[{i}]") for i in range(total_questions)]
        
        """Check if user answered all questions"""
        if len(user_answers) != total_questions:
            flash("Please answer all questions", "danger")
            return redirect(url_for("grammar_test"))
        else:
            session["grammar_test_completed"] = True

        """Get favorited status for each question"""
        favorited_questions = []
        if session.get("user_id"):
            try:
                conn = sqlite3.connect(db_file)
                with conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT question FROM favorites WHERE user_id = ?", (session["user_id"],))
                    favorited_questions = [row[0] for row in cursor.fetchall()]
            except sqlite3.Error as e:
                flash(f"Error retrieving favorites: {e}", "danger")
            except Exception as e:
                flash(f"Unexpected error: {e}", "danger")
            finally:
                conn.close()
        
        """Calculate score"""
        score = 0
        for i, question in enumerate(questions):
            if question["correct_answer"] == user_answers[i]:
                score += 1
        
        """Update user streak and history"""
        if session.get("user_id"):
            update_user_streak(session["user_id"])

        return render_template("grammar_result.html", questions=questions, total_questions=total_questions, user_answers=user_answers, score=score, favorited_questions=favorited_questions)
    
# Generate reading questions page
@app.route("/reading_test", methods=["GET", "POST"])
def reading_test():
    if request.method == "GET":
        try:
            questions = generate_reading_questions()
            flash("Successfully generated questions", "success")
            return render_template("reading_test.html", questions=questions)
        except Exception as e:
            flash(f"Error generating questions: {e}", "danger")
            return redirect(url_for("home"))
    else:
        """Check if the session has current test data"""
        if "current_reading_test" not in session:
            flash("Session expired, please try again", "danger")
            return redirect(url_for("home"))
        
        questions = session["current_reading_test"]["READING_DATA"]
        if not questions:
            flash("Error retrieving questions", "danger")
            return redirect(url_for("home"))
        
        """Handle form submission"""
        total_questions = sum(len(passage["questions"]) for passage in questions)
        user_answers = []
        for i in range(len(questions)):
            passage_answers = [request.form.get(f"answers[{i}][{j}]") for j in range(len(questions[i]["questions"]))]
            user_answers.append(passage_answers)        
        
        """
        Check if user answered all questions
        But user_answers is a list of lists, so we need to flatten it to check the length"""
        answers_count = sum(len(passage) for passage in user_answers)
        if answers_count != total_questions:
            flash("Please answer all questions", "danger")
            return redirect(url_for("reading_test"))
        else:
            session["reading_test_completed"] = True
        
        """Calculate score"""
        score = 0
        for i, passage in enumerate(questions):
            for j, question in enumerate(passage["questions"]):
                if question["correct_answer"] == user_answers[i][j]:
                    score += 1

        """Update user streak and history"""
        if session.get("user_id"):
            update_user_streak(session["user_id"])

        return render_template("reading_result.html", questions=questions, total_questions=total_questions, user_answers=user_answers, score=score)

# Clear current test session
@app.route("/retake", methods=["POST"])
def retake():
    """Clear specific test session data based on which test was completed"""
    if session.get("grammar_test_completed"):
        session.pop("current_grammar_test", None)
        session.pop("grammar_test_completed", None)
        return redirect(url_for("grammar_test"))
    elif session.get("reading_test_completed"):
        session.pop("current_reading_test", None)
        session.pop("reading_test_completed", None)
        return redirect(url_for("reading_test"))
    else:
        flash("No test session found", "warning")
        return redirect(url_for("home"))

# Login, logout, register, change password function
@app.route("/login", methods=["GET", "POST"])
def login():
    session.pop("user_id", None)
    if request.method == "GET":
        return render_template("login.html")
    else:
        if not request.form.get("username") or not request.form.get("password"):
            flash("Please fill in all fields", "danger")
            return redirect(url_for("login"))
        
        username = request.form.get("username")
        password = request.form.get("password")

        try:
            conn = sqlite3.connect(db_file)
            with conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
                row = cursor.fetchone()
                if not check_password_hash(row[1], password):
                    flash("Invalid username or password", "danger")
                    return redirect(url_for("login"))
                else:
                    session["user_id"] = row[0]
                    flash("Logged in successfully", "success")
                    return redirect(url_for("dashboard"))
        except sqlite3.Error as e:
            flash(f"Error logging in: {e}", "danger")
            return redirect(url_for("login"))
        except Exception as e:
            flash(f"Unexpected error: {e}", "danger")
            return redirect(url_for("login"))
        finally:
            conn.close() 

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    flash("Logged out successfully", "success")
    return redirect(url_for("home"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        if not request.form.get("username") or not request.form.get("password"):
            flash("Please fill in all fields", "danger")
            return redirect(url_for("register"))
        
        if request.form.get("password") != request.form.get("confirm_password"):
            flash("Passwords do not match", "danger")
            return redirect(url_for("register"))

        username = request.form.get("username")
        hash = generate_password_hash(request.form.get("password"))

        try:
            conn = sqlite3.connect(db_file)
            with conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash))
                flash("Account created successfully!", "success")
                return redirect(url_for("login"))
        except sqlite3.Error as e:
            flash(f"Error creating account: {e}", "danger")
            return redirect(url_for("register"))
        except sqlite3.IntegrityError:
            flash("Username already exists", "danger")
            return redirect(url_for("register"))
        except Exception as e:
            flash(f"Unexpected error: {e}", "danger")
            return redirect(url_for("register"))
        finally:
            conn.close()

@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "GET":
        return render_template("change_password.html")
    else:
        if not request.form.get("old_password") or not request.form.get("new_password"):
            flash("Please fill in all fields", "danger")
            return redirect(url_for("change_password"))
        
        if request.form.get("new_password") != request.form.get("confirm_new_password"):
            flash("New passwords do not match", "danger")
            return redirect(url_for("change_password"))

        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")

        try:
            conn = sqlite3.connect(db_file)
            with conn:
                cursor = conn.cursor()
                cursor.execute("SELECT password FROM users WHERE id = ?", (session["user_id"],))
                row = cursor.fetchone()
                if not row or not check_password_hash(row[0], old_password):
                    flash("Invalid old password", "danger")
                    return redirect(url_for("change_password"))
                
                new_hash = generate_password_hash(new_password)
                cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_hash, session["user_id"]))
                flash("Password changed successfully", "success")
                return redirect(url_for("dashboard"))
        except sqlite3.Error as e:
            flash(f"Error changing password: {e}", "danger")
            return redirect(url_for("change_password"))
        except Exception as e:
            flash(f"Unexpected error: {e}", "danger")
            return redirect(url_for("change_password"))
        finally:
            conn.close()

# Favorite & unfavorite questions function
@app.route("/favorite", methods=["POST"])
@login_required
def favorite():
    """Get data from the request using json"""
    data = request.get_json()
    question = data.get("question")
    choices = data.get("choices")
    correct_answer = data.get("correct_answer")
    explanation = data.get("explanation")

    if not all([question, choices, correct_answer, explanation]):
        return jsonify({"error": "Missing data"}), 400
    try:
        conn = sqlite3.connect(db_file)
        with conn:
            cursor = conn.cursor()
            """Check if the question already exists in the favorites table for the user"""
            cursor.execute("SELECT * FROM favorites WHERE user_id = ? AND question = ?", (session["user_id"], question))
            row = cursor.fetchone()
            if row:
                """If exist, remove from favorites
                Since user_id and question are unique together, we can use them to delete the row"""
                cursor.execute("DELETE FROM favorites WHERE user_id = ? AND question = ?", (session["user_id"], question))
                return jsonify({"message": "Question removed from favorites"}), 200
            else:
                """Insert the question into the favorites table"""
                cursor.execute("""
                    INSERT INTO favorites (user_id, question, choices, correct_answer, explanation) VALUES (?, ?, ?, ?, ?)
                """, (session["user_id"], question, choices, correct_answer, explanation))
                return jsonify({"message": "Question added to favorites"}), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {e}"}), 500
    finally:
        conn.close()

# Show favorites page
@app.route("/favorites", methods=["GET"])
@login_required
def show_favorites():
    try:
        conn = sqlite3.connect(db_file)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT question, choices, correct_answer, explanation FROM favorites WHERE user_id = ?", (session["user_id"],))
            favorites = cursor.fetchall()
            if not favorites:
                flash("No favorites found", "info")
                return render_template("favorites.html", favorites=[])
            else:
                flash("Favorites retrieved successfully", "success")
                return render_template("favorites.html", favorites=favorites)
    except sqlite3.Error as e:
        flash(f"Error retrieving favorites: {e}", "danger")
        return redirect(url_for("dashboard"))
    except Exception as e:
        flash(f"Unexpected error: {e}", "danger")
        return redirect(url_for("dashboard"))
    finally:
        conn.close()

if __name__ == "__main__":
    app.run(debug=True)