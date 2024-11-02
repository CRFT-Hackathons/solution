# solution

Running:
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py

brew install openapi-generator
openapi-generator generate -i http://localhost:8080/api-docs -g python --skip-validate-spec --additional-properties=generateSourceCodeOnly=true,packageName=api
```
