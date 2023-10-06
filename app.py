from flask import Flask, request, jsonify
import os
import io
import requests
from PyPDF2 import PdfReader
import openai
import json

app = Flask(__name__)

# OpenAI API key (replace 'your-api-key' with your actual API key)
openai.api_key = os.getenv('OPENAI_API_KEY')

def extract_text_from_pdf(pdf_content):
    extracted_text = ""
    pdf_reader = PdfReader(io.BytesIO(pdf_content))
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
        response = requests.get(pdf_url)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        extracted_text = extract_text_from_pdf(response.content)
        
        # Construct prompt with extracted resume text and job description
        prompt = [
            {"role": "system", "content": "You are a AI resume extractor."},
            {"role": "user", "content":f"""
                    Consider following raw resume text extracted from user resume PDF delimited between ### ###:
                    ###{extracted_text}###
                    --------------------------------------------------------------
                    Generate a valid JSON response with above extracted resume text. 
                    Note:
                    -Generate JSON making keys section name and values text extracted from resume.
                    -Make single line JSON response. 
                    -Respond only with the generated JSON response.
                    -If PDF does not seem to be a resume, return an error message.               
                    """}
        ]
        
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=prompt,
        max_tokens=1000,  # Limit the response to a certain number of tokens
        )
        
        response = response["choices"][0]["message"]["content"]
        
        return jsonify({'extracted_text': json.loads(response)}), 200
        # return jsonify({'extracted_text': extracted_text}), 200
    
    except requests.exceptions.HTTPError as errh:
        return jsonify({'error': f'HTTP Error: {errh}'}), 500
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
                    consider following resume and job description:
                    ```Resume :\n{extracted_resume_text}
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
            max_tokens=2000  # Limit the response to a certain number of tokens
        )
        
        # Get the generated resume text from OpenAI response
        generated_resume_text = response["choices"][0]["message"]["content"]
        
        # Respond in Markdown format
        markdown_response = generated_resume_text
        
        return jsonify({'generated_resume': markdown_response}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
#     app.run(debug=True)