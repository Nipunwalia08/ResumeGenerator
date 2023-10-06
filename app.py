from flask import Flask, request, jsonify
import os
import requests
from PyPDF2 import PdfReader
import openai
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
# OpenAI API key (replace 'your-api-key' with your actual API key)
openai.api_key = os.getenv('OPENAI_API_KEY')

# Create a folder named 'user_resume' if it doesn't exist
if not os.path.exists('user_resume'):
    os.makedirs('user_resume')

def download_pdf(pdf_url):
    response = requests.get(pdf_url, stream=True)
    with open("user_resume/temp.pdf", "wb") as pdf_file:
        for chunk in response.iter_content(chunk_size=128):
            pdf_file.write(chunk)

def extract_text_from_pdf(pdf_path):
    extracted_text = ""
    with open(pdf_path, "rb") as pdf_file:
        pdf_reader = PdfReader(pdf_file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            extracted_text += page.extract_text()
    return extracted_text

@app.route('/extract-text', methods=['POST'])
def extract_text():
    data = request.get_json()
    pdf_url = data.get('pdf_url')
    if not pdf_url:
        return jsonify({'error': 'PDF URL is missing'}), 400

    try:
        download_pdf(pdf_url)
        pdf_path = os.path.join('user_resume', 'temp.pdf')
        extracted_text = extract_text_from_pdf(pdf_path)
        os.remove(pdf_path)  # Remove the temporary PDF file after extraction
        return jsonify({'extracted_text': extracted_text}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-resume', methods=['POST'])
def generate_resume():
    data = request.get_json()
    extracted_resume_text = data.get('extracted_resume_text')
    job_description = data.get('job_description')
    
    if not extracted_resume_text or not job_description:
        return jsonify({'error': 'Extracted resume text or job description is missing'}), 400
    
    try:
        # Construct prompt with extracted resume text and job description
        prompt = [
            {"role": "system", "content": "You are a AI Resume Generator."},
            {"role": "user", "content":f"""
                    consider following resume text and job description:
                    ```Resume Text:\n{extracted_resume_text}
                    Job Description:\n{job_description}```
                    Generate a new resume with the following sections for the mentioned job description:
                    Professional Summary, Education, Projects, Experience, Skills and Interests, Achievements (if any)
                    Respond in Markdown format.
                    Respond only with the generated resume text.
                    """
                    }
        ]
        # Make request to OpenAI API to generate new resume
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=prompt,
            max_tokens=1000  # Limit the response to a certain number of tokens
        )
        
        # Get the generated resume text from OpenAI response
        generated_resume_text = response["choices"][0]["message"]["content"]
        
        # Respond in Markdown format
        markdown_response = generated_resume_text
        
        return jsonify({'generated_resume': markdown_response}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)