#!/usr/bin/env python3
"""Simple web interface for JDT schema validation."""

from flask import Flask, render_template_string, request, jsonify
from parser import parse_and_validate
import json

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JDT Schema Validator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 1000px;
            width: 100%;
            overflow: hidden;
        }
        
        .header {
            background: #2d3748;
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 28px;
            margin-bottom: 5px;
        }
        
        .header p {
            font-size: 14px;
            opacity: 0.8;
        }
        
        .content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            padding: 30px;
        }
        
        @media (max-width: 768px) {
            .content {
                grid-template-columns: 1fr;
            }
        }
        
        .panel {
            display: flex;
            flex-direction: column;
            position: relative;
        }
        
        .panel h2 {
            font-size: 16px;
            color: #2d3748;
            margin-bottom: 12px;
            font-weight: 600;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .dropzone {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border: 3px dashed #667eea;
            border-radius: 4px;
            padding: 20px;
            display: none;
            align-items: center;
            justify-content: center;
            background: rgba(102, 126, 234, 0.05);
            z-index: 10;
        }
        
        .dropzone.active {
            display: flex;
        }
        
        .dropzone-content {
            text-align: center;
            pointer-events: none;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 10px;
        }
        
        .dropzone-icon {
            font-size: 40px;
        }
        
        .dropzone-text {
            color: #667eea;
            font-size: 14px;
            font-weight: 600;
            line-height: 1.4;
        }
        
        .textarea-wrapper {
            position: relative;
            flex: 1;
        }
        
        textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 12px;
            resize: vertical;
            min-height: 350px;
            color: #2d3748;
            display: block;
        }
        
        input[type="file"] {
            display: none;
        }
        
        .textarea-display {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 12px;
            overflow: auto;
            word-wrap: break-word;
            white-space: pre-wrap;
            color: #2d3748;
            background: white;
            padding: 10px;
            border-radius: 4px;
            max-height: 200px;
            border: 1px solid #e2e8f0;
            margin-top: 10px;
        }
        
        .button-group {
            grid-column: 1 / -1;
            display: flex;
            gap: 10px;
            justify-content: center;
        }
        
        button {
            padding: 12px 30px;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
        }
        
        .btn-group {
            display: flex;
            gap: 10px;
        }
        
        .btn-browse {
            background: #e2e8f0;
            color: #2d3748;
            padding: 8px 16px;
            font-size: 14px;
        }
        
        .btn-browse:hover {
            background: #cbd5e0;
        }
        
        .btn-validate {
            background: #667eea;
            color: white;
            flex: 1;
            max-width: 200px;
        }
        
        .btn-validate:hover {
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.2);
        }
        
        .btn-validate:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .btn-clear {
            background: #edf2f7;
            color: #2d3748;
        }
        
        .btn-clear:hover {
            background: #e2e8f0;
        }
        
        .result {
            grid-column: 1 / -1;
            padding: 20px;
            border-radius: 8px;
            display: none;
        }
        
        .result.show {
            display: block;
        }
        
        .result.valid {
            background: #f0fff4;
            border: 1px solid #9ae6b4;
            color: #22543d;
        }
        
        .result.invalid {
            background: #fff5f5;
            border: 1px solid #feb2b2;
            color: #742a2a;
        }
        
        .result h3 {
            margin-bottom: 10px;
            font-size: 16px;
        }
        
        .result ul {
            margin-left: 20px;
            font-size: 14px;
        }
        
        .result li {
            margin-bottom: 5px;
        }
        
        .loading {
            display: none;
            text-align: center;
            grid-column: 1 / -1;
        }
        
        .loading.show {
            display: block;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 0.8s linear infinite;
            margin: 0 auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>JDT Schema Validator</h1>
            <p>Validate JSON files against JDT schemas</p>
        </div>
        
        <div class="content">
            <div class="panel">
                <h2>
                    JDT Schema
                    <button class="btn-browse" id="browseSchemBtn">Browse</button>
                </h2>
                <div class="textarea-wrapper">
                    <div class="dropzone" id="schemaDrop">
                        <div class="dropzone-content">
                            <div class="dropzone-icon">📄</div>
                            <div class="dropzone-text">Drop file here</div>
                        </div>
                    </div>
                    <input type="file" id="schemaFile" accept=".jdt,.txt,.json">
                    <textarea id="schemaInput" placeholder="Paste your JDT schema here or drag a file..."></textarea>
                </div>
            </div>
            
            <div class="panel">
                <h2>
                    JSON File
                    <button class="btn-browse" id="browseJsonBtn">Browse</button>
                </h2>
                <div class="textarea-wrapper">
                    <div class="dropzone" id="jsonDrop">
                        <div class="dropzone-content">
                            <div class="dropzone-icon">📄</div>
                            <div class="dropzone-text">Drop file here</div>
                        </div>
                    </div>
                    <input type="file" id="jsonFile" accept=".json,.txt">
                    <textarea id="jsonInput" placeholder="Paste your JSON file here or drag a file..."></textarea>
                </div>
            </div>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Validating...</p>
            </div>
            
            <div class="result" id="result"></div>
            
            <div class="button-group">
                <button class="btn-validate" id="validateBtn" onclick="validate()">Validate</button>
                <button class="btn-clear" id="clearBtn" onclick="clearAll()">Clear</button>
            </div>
        </div>
    </div>
    
    <script>
        const schemaInput = document.getElementById('schemaInput');
        const jsonInput = document.getElementById('jsonInput');
        const schemaFile = document.getElementById('schemaFile');
        const jsonFile = document.getElementById('jsonFile');
        const schemaDrop = document.getElementById('schemaDrop');
        const jsonDrop = document.getElementById('jsonDrop');
        const browseSchemBtn = document.getElementById('browseSchemBtn');
        const browseJsonBtn = document.getElementById('browseJsonBtn');
        const validateBtn = document.getElementById('validateBtn');
        const loading = document.getElementById('loading');
        const result = document.getElementById('result');
        
        function setupDropZone(dropZone, textarea, fileInput, allowedExtensions) {
            const wrapper = textarea.parentElement;
            let dragCounter = 0;
            
            wrapper.addEventListener('dragenter', (e) => {
                e.preventDefault();
                e.stopPropagation();
                dragCounter++;
                dropZone.classList.add('active');
            });
            
            wrapper.addEventListener('dragleave', (e) => {
                e.preventDefault();
                e.stopPropagation();
                dragCounter--;
                if (dragCounter === 0) {
                    dropZone.classList.remove('active');
                }
            });
            
            wrapper.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
            
            wrapper.addEventListener('drop', (e) => {
                e.preventDefault();
                e.stopPropagation();
                dragCounter = 0;
                dropZone.classList.remove('active');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    const file = files[0];
                    const fileName = file.name.toLowerCase();
                    const fileExtension = fileName.split('.').pop();
                    
                    if (!allowedExtensions.includes(fileExtension)) {
                        showError(`Invalid file format. Only ${allowedExtensions.join(', ')} files are allowed.`);
                        return;
                    }
                    
                    const reader = new FileReader();
                    reader.onload = (event) => {
                        textarea.value = event.target.result;
                    };
                    reader.onerror = () => {
                        showError('Error reading file. Please try again.');
                    };
                    reader.readAsText(file);
                }
            });
        }
        
        function showError(message) {
            result.classList.add('show', 'invalid');
            result.innerHTML = `
                <h3>❌ Error</h3>
                <p>${escapeHtml(message)}</p>
            `;
        }
        
        function setupFileInput(fileInput, textarea) {
            fileInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = (event) => {
                        textarea.value = event.target.result;
                    };
                    reader.readAsText(file);
                }
            });
        }
        
        setupDropZone(schemaDrop, schemaInput, schemaFile, ['jdt', 'txt']);
        setupDropZone(jsonDrop, jsonInput, jsonFile, ['json', 'txt']);
        
        setupFileInput(schemaFile, schemaInput);
        setupFileInput(jsonFile, jsonInput);
        
        browseSchemBtn.addEventListener('click', () => schemaFile.click());
        browseJsonBtn.addEventListener('click', () => jsonFile.click());
        
        async function validate() {
            const schemaText = schemaInput.value.trim();
            const jsonText = jsonInput.value.trim();
            
            if (!schemaText || !jsonText) {
                alert('Please provide both a JDT schema and a JSON file');
                return;
            }
            
            loading.classList.add('show');
            result.classList.remove('show');
            
            try {
                const response = await fetch('/validate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        schema: schemaText,
                        json: jsonText
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displayResult(data.valid, data.errors);
                } else {
                    result.classList.add('show', 'invalid');
                    result.innerHTML = `
                        <h3>❌ Error</h3>
                        <p>${data.error}</p>
                    `;
                }
            } catch (error) {
                result.classList.add('show', 'invalid');
                result.innerHTML = `
                    <h3>❌ Error</h3>
                    <p>${error.message}</p>
                `;
            } finally {
                loading.classList.remove('show');
            }
        }
        
        function displayResult(valid, errors) {
            result.classList.add('show');
            
            if (valid) {
                result.classList.remove('invalid');
                result.classList.add('valid');
                result.innerHTML = '<h3>✅ Valid</h3><p>The JSON file is valid according to the schema.</p>';
            } else {
                result.classList.remove('valid');
                result.classList.add('invalid');
                let html = '<h3>❌ Invalid</h3>';
                if (errors && errors.length > 0) {
                    html += '<ul>';
                    errors.forEach(error => {
                        html += `<li>${escapeHtml(error)}</li>`;
                    });
                    html += '</ul>';
                } else {
                    html += '<p>Validation failed.</p>';
                }
                result.innerHTML = html;
            }
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function clearAll() {
            schemaInput.value = '';
            jsonInput.value = '';
            result.classList.remove('show');
        }
        
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                validate();
            }
        });
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/validate', methods=['POST'])
def validate():
    """Validate JSON against JDT schema."""
    try:
        data = request.get_json()
        schema_text = data.get('schema', '').strip()
        json_text = data.get('json', '').strip()
        print("--- SCHEMA ---")
        print(repr(schema_text))
        print("--- JSON ---")
        print(repr(json_text))
        
        if not schema_text or not json_text:
            return jsonify({
                'success': False,
                'error': 'Schema and JSON are required'
            })
        
        is_valid, errors = parse_and_validate(schema_text, json_text)
        
        return jsonify({
            'success': True,
            'valid': is_valid,
            'errors': errors or []
        })
    
    except json.JSONDecodeError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid JSON: {str(e)}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
