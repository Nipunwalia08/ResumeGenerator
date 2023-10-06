# FILEPATH: README.md

This Flask application has two endpoints:
1. `/extract-text`: This endpoint extracts text from a PDF file.
2. `/generate-resume`: This endpoint generates a resume given the extracted resume text and job description.

To use the /extract-text endpoint, send a POST request with a PDF file in the request body.
To use the /generate-resume endpoint, send a POST request with the extracted resume text and job description in the request body.
 
# Example usage:
 
## To extract text from a PDF file:

```
import requests

url = 'http://localhost:5000/extract-text'
files = {'file': open('example.pdf', 'rb')}
response = requests.post(url, files=files)
print(response.json())
```

## To generate a resume:

```
import requests

url = 'http://localhost:5000/generate-resume'
data = {'resume_text': 'Extracted resume text', 'job_description': 'Job description'}
response = requests.post(url, json=data)
print(response.json())
```
