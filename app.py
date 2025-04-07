from google import genai
from google.genai import errors
from dotenv import load_dotenv, find_dotenv
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_session import Session
import os, sys
from helpers import generate_grammar_questions, generate_reading_questions, validate_environment, login_required

# Validate environment variables
if not validate_environment():
    sys.exit("ERROR: Missing or invalid environment variables")

# Load environment variables
_ = load_dotenv(find_dotenv())

# Create Flask app, get the secret key from the environment variable
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Config Session
app.config["SESSION_PERMANENT"] = False # Session expires when the browser is closed
app.config["SESSION_TYPE"] = "filesystem" # Store session data in the filesystem on server
app.config["SESSION_FILE_DIR"] = os.path.join(app.root_path, "flask_session") # Directory to store session data
app.config["SESSION_FILE_THRESHOLD"] = 500 # The maximum number of session files before cleanup
Session(app)

# Home page
@app.route("/", methods=["GET"])
def home():
    if session.get("user_id"):
        return None
    else:
        return render_template("index.html")
    
# Dashboard page
@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    return render_template("dashboard.html")

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
        
        """Calculate score"""
        score = 0
        for i, question in enumerate(questions):
            if question["correct_answer"] == user_answers[i]:
                score += 1

        return render_template("grammar_result.html", questions=questions, total_questions=total_questions, user_answers=user_answers, score=score)
    
# Generate reading questions page
@app.route("/reading_test", methods=["GET", "POST"])
def reading_test():
    if request.method == "GET":
        try:
            questions = generate_reading_questions()
            print(questions)
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

        return render_template("reading_result.html", questions=questions, total_questions=total_questions, user_answers=user_answers, score=score)

# Clear current test session
@app.route("/retake", methods=["POST"])
def retake():
    # Clear specific test session data based on which test was completed
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
    return None

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    flash("Logged out successfully", "success")
    return redirect(url_for("home"))

@app.route("/register", methods=["GET", "POST"])
def register():
    return None

@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    return None

# Streaks, history, favorite questions function

if __name__ == "__main__":
    app.run(debug=True)