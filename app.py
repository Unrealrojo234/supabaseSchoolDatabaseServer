from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from supabase import create_client, Client # type: ignore
import json

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(url, key)
app = Flask(__name__)

# Configure CORS with specific options
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173", "http://localhost:4173"],  # Add your frontend URLs
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


@app.route("/")
def root():
    return "<h1 style='text-align:center;color:teal;'>Supabase postgres server</h1>"

@app.route("/api/students", methods=['GET'])
def get_students():
    try:
        # Fetch fresh data from Supabase when the endpoint is called
        response = supabase.table("students").select("*").execute()
        students_data = response.data
        
        # Return the data as JSON using jsonify
        return jsonify({
            "success": True,
            "data": students_data,
            "count": len(students_data)
        })
    
    except Exception as e:
        # Handle any errors and return appropriate response
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    


@app.route("/api/students", methods=['POST'])
def create_student():
    try:
        # Get JSON data from request body
        data = request.get_json()
        
        # Validate required fields
        if not data or 'name' not in data or 'age' not in data:
            return jsonify({
                "success": False,
                "error": "Name and age are required"
            }), 400
            
        # Extract name and age
        name = data['name']
        age = data['age']
        
        # Validate data types
        if not isinstance(name, str) or not isinstance(age, int):
            return jsonify({
                "success": False,
                "error": "Name must be a string and age must be an integer"
            }), 400
        
        # Insert data into Supabase
        response = supabase.table("students").insert({
            "name": name,
            "age": age
        }).execute()
        
        # Return the created student data
        return jsonify({
            "success": True,
            "data": response.data[0],
            "message": "Student created successfully"
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


#Delete request for a student using id

@app.route("/api/students/<int:student_id>", methods=['DELETE'])
def delete_student(student_id):
    try:
        # First check if the student exists
        check_response = supabase.table("students").select("*").eq("id", student_id).execute()
        
        if not check_response.data:
            return jsonify({
                "success": False,
                "error": f"Student with ID {student_id} not found"
            }), 404
        
        # Delete the student
        supabase.table("students").delete().eq("id", student_id).execute()
        
        return jsonify({
            "success": True,
            "message": f"Student with ID {student_id} deleted successfully",
            "deleted_record": check_response.data[0]
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True)