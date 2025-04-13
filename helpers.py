from google import genai
from google.genai import types
from google.genai import errors
from dotenv import load_dotenv, find_dotenv
from flask import session, redirect, flash
from functools import wraps
import os, json, sqlite3
from datetime import datetime, timedelta
from prompts import grammar_prompt, reading_prompt

# Configuration Constants
REQUIRED_GRAMMAR_QUESTIONS = 10
REQUIRED_READING_QUESTIONS = 3
MAX_GENERATION_RETRIES = 3 # Max retries to generate questions
MAX_GRAMMAR_HISTORY_QUESTIONS = 50 # Max grammar questions to keep in session history
MAX_READING_HISTORY_QUESTIONS = 20 # Max reading questions to keep in session history

# Find and load environment variables
_ = load_dotenv(find_dotenv())

# Setup database connection, create database file if it doesn't exist
db_file = "database.db"
conn = None

# Set up model
MODEL = "gemini-2.0-flash"
SYSTEM_INSTRUCTION = """
You are a helpful Vietnamese teacher who teaches English to Vietnamese students. 
You are helping them to improve their TOEIC score.
"""

def get_response(prompt):
    """A helper function to generate an optimized prompt using the Gemini API from user input."""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("API key not found in environment variables")
        
        client = genai.Client(api_key = api_key)

        response = client.models.generate_content(
            model = MODEL,
            contents = prompt,
            config = types.GenerateContentConfig(
                system_instruction = SYSTEM_INSTRUCTION,
                temperature = 0.5
            )
        )
        return response.text
    except ValueError as e:
        print(f"Config or value error: {e}")
        raise
    except errors.APIError as e:
        print(f"Gemini API error: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

# Generate grammar questions function and parse the response
def generate_grammar_questions():
    # Check if the session has current test data and if the test is not completed to avoid calling API again
    if session.get("current_grammar_test") and not session.get("grammar_test_completed"):
        return session["current_grammar_test"]["GRAMMAR_DATA"]
    else:
        unique_questions = []

        for attempt in range(MAX_GENERATION_RETRIES):
            try:
                # Track previous questions to avoid duplicates
                if not session.get("previous_grammar_questions"):
                    session["previous_grammar_questions"] = []

                # Generate questions, parse the JSON response, clean json XML tag or Markdown tag if found
                response = get_response(grammar_prompt)
                response = response.strip()
                if response.startswith("<json>") and response.endswith("</json>"):
                    response = response[len("<json>"):-len("</json>")].strip()
                if response.startswith("```json") and response.endswith("```"):
                    response = response[len("```json"):-len("```")].strip()
                questions = json.loads(response)

                # Check for duplicates against previous questions
                for q in questions["GRAMMAR_DATA"]:
                    question_text = q["question"].lower()
                    if not any(question_text in prev.lower() for prev in session["previous_grammar_questions"]):
                        unique_questions.append(q)
                        session["previous_grammar_questions"].append(question_text)

                # If we have enough unique questions, break the loop
                if len(unique_questions) >= REQUIRED_GRAMMAR_QUESTIONS:
                    break
                print(f"Attempt {attempt + 1}: Got {len(unique_questions)} unique questions so far...")
            
            except json.JSONDecodeError as e:
                print(f"JSON Decode error: {e}")
                raise
            except Exception as e:
                print(f"Unexpected error: {e}")
                raise

        # If we don't have enough unique questions after max retries, show whatever we have
        if unique_questions:
            if len(unique_questions) < REQUIRED_GRAMMAR_QUESTIONS:
                print(f"Warning: Only got {len(unique_questions)} unique questions after {MAX_GENERATION_RETRIES} attempts.")
                flash(f"Generated {len(unique_questions)} unique questions", "warning")
            
            # Keep only the last N questions in history
            session["previous_grammar_questions"] = session["previous_grammar_questions"][-MAX_GRAMMAR_HISTORY_QUESTIONS:]
            
            # Store questions in session
            questions = {"GRAMMAR_DATA": unique_questions[:REQUIRED_GRAMMAR_QUESTIONS]}
            session["current_grammar_test"] = questions
            session["grammar_test_completed"] = False
            return questions["GRAMMAR_DATA"]
        else:
            # If we couldn't generate any valid questions at all
            raise ValueError("Failed to generate any valid questions after multiple attempts")

# Generate reading questions function and parse the response
def generate_reading_questions():
    # Check if the session has current test data and if the test is not completed to avoid calling API again
    if session.get("current_reading_test") and not session.get("reading_test_completed"):
        return session["current_reading_test"]["READING_DATA"]
    else:
        unique_questions = []

        for attempt in range(MAX_GENERATION_RETRIES):
            try:
                # Track previous questions to avoid duplicates
                if not session.get("previous_reading_questions"):
                    session["previous_reading_questions"] = []

                # Generate questions, parse the JSON response, clean \n, json XML tag or Markdown tag if found
                response = get_response(reading_prompt)
                response = response.strip()
                if response.startswith("<json>") and response.endswith("</json>"):
                    response = response[len("<json>"):-len("</json>")].strip()
                if response.startswith("```json") and response.endswith("```"):
                    response = response[len("```json"):-len("```")].strip()
                questions = json.loads(response, strict=False) # force strict=False to handle any unexpected formatting

                # Check for duplicates against previous questions
                for q in questions["READING_DATA"]:
                    passage_text = q["passage"].lower()
                    if not any(passage_text in prev.lower() for prev in session["previous_reading_questions"]):
                        unique_questions.append(q)
                        session["previous_reading_questions"].append(passage_text)

                # If we have enough unique questions, break the loop
                if len(unique_questions) >= REQUIRED_READING_QUESTIONS:
                    break
                print(f"Attempt {attempt + 1}: Got {len(unique_questions)} unique questions so far...")
            
            except json.JSONDecodeError as e:
                print(f"JSON Decode error: {e}")
                raise
            except Exception as e:
                print(f"Unexpected error: {e}")
                raise

        # If we don't have enough unique questions after max retries, show whatever we have
        if unique_questions:
            if len(unique_questions) < REQUIRED_READING_QUESTIONS:
                print(f"Warning: Only got {len(unique_questions)} unique questions after {MAX_GENERATION_RETRIES} attempts.")
                flash(f"Generated {len(unique_questions)} unique questions", "warning")
            
            # Keep only the last N questions in history
            session["previous_reading_questions"] = session["previous_reading_questions"][-MAX_READING_HISTORY_QUESTIONS:]
            
            # Store questions in session
            questions = {"READING_DATA": unique_questions[:REQUIRED_READING_QUESTIONS]}
            session["current_reading_test"] = questions
            session["reading_test_completed"] = False
            return questions["READING_DATA"]
        else:
            # If we couldn't generate any valid questions at all
            raise ValueError("Failed to generate any valid questions after multiple attempts")

def validate_environment():
    """Validate required environment variables exist."""
    required_vars = ["GEMINI_API_KEY", "FLASK_SECRET_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file or environment")
        return False
    return True

def login_required(func):
    """Decorate routes to require login that accept any arguments that might be passed to the original function"""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return func(*args, **kwargs)
    return decorated_function

def get_username(user_id):
    try:
        conn = sqlite3.connect(db_file)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return "Guest"
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return "Guest"
    finally:
        conn.close()

def update_user_streak(user_id):
    try:
        conn = sqlite3.connect(db_file)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT streak, last_test_date FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if not row:
                return
            
            current_streak, last_test_date = row
            today = datetime.now().date()

            if last_test_date:
                last_date = datetime.strptime(last_test_date, "%Y-%m-%d").date()
                yesterday = today - timedelta(days=1)
                if last_date == yesterday:
                    """User took a test today and yesterday, increment streak"""
                    new_streak = current_streak + 1
                elif last_date == today:
                    """User already took a test today, no change"""
                    new_streak = current_streak
                else:
                    """User didn't take a test yesterday, reset streak"""
                    new_streak = 1
            else:
                """User has never taken a test, set streak to 1"""
                new_streak = 1
            
            cursor.execute("UPDATE users SET streak = ?, last_test_date = ? WHERE id = ?", (new_streak, today.strftime("%Y-%m-%d"), user_id))
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        conn.close()