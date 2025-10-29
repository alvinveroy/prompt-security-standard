"""
Flask Web Application with UPSS Integration
Demonstrates UPSS usage in a web application context.
"""

from flask import Flask, jsonify, request, render_template_string
from upss_loader import UPSSLoader
import os


app = Flask(__name__)
loader = UPSSLoader("upss_config.yaml")


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>UPSS Flask Example</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        h1 { color: #333; }
        .prompt-box { background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .metadata { background: #e3f2fd; padding: 10px; border-radius: 5px; margin: 10px 0; }
        pre { white-space: pre-wrap; word-wrap: break-word; }
        button { background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #45a049; }
        .audit-log { background: #fff3cd; padding: 10px; border-radius: 5px; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>UPSS Flask Application</h1>
    <p>This application demonstrates the Universal Prompt Security Standard (UPSS) in a web context.</p>
    
    <h2>Available Prompts</h2>
    <div id="prompts"></div>
    
    <h2>Load a Prompt</h2>
    <select id="promptSelect">
        <option value="">Select a prompt...</option>
    </select>
    <button onclick="loadPrompt()">Load Prompt</button>
    
    <div id="promptDisplay"></div>
    
    <h2>Audit Log</h2>
    <button onclick="loadAuditLog()">Refresh Audit Log</button>
    <div id="auditLog"></div>
    
    <script>
        // Load available prompts
        fetch('/api/prompts')
            .then(response => response.json())
            .then(data => {
                const promptsDiv = document.getElementById('prompts');
                const select = document.getElementById('promptSelect');
                
                data.prompts.forEach(prompt => {
                    // Add to list
                    const div = document.createElement('div');
                    div.className = 'metadata';
                    div.innerHTML = `<strong>${prompt.id}</strong> - ${prompt.description} (v${prompt.version})`;
                    promptsDiv.appendChild(div);
                    
                    // Add to select
                    const option = document.createElement('option');
                    option.value = prompt.id;
                    option.textContent = prompt.id;
                    select.appendChild(option);
                });
            });
        
        function loadPrompt() {
            const promptId = document.getElementById('promptSelect').value;
            if (!promptId) return;
            
            fetch(`/api/prompt/${promptId}`)
                .then(response => response.json())
                .then(data => {
                    const display = document.getElementById('promptDisplay');
                    display.innerHTML = `
                        <h3>Prompt: ${data.id}</h3>
                        <div class="metadata">
                            <strong>Type:</strong> ${data.metadata.type}<br>
                            <strong>Version:</strong> ${data.metadata.version}<br>
                            <strong>Hash:</strong> ${data.hash}
                        </div>
                        <div class="prompt-box">
                            <pre>${data.content}</pre>
                        </div>
                    `;
                });
        }
        
        function loadAuditLog() {
            fetch('/api/audit-log')
                .then(response => response.json())
                .then(data => {
                    const logDiv = document.getElementById('auditLog');
                    if (data.entries.length === 0) {
                        logDiv.innerHTML = '<p>No audit entries recorded.</p>';
                        return;
                    }
                    
                    let html = '<div class="audit-log">';
                    data.entries.forEach(entry => {
                        html += `<div>${entry.timestamp} - ${entry.prompt_id}: ${entry.action}</div>`;
                    });
                    html += '</div>';
                    logDiv.innerHTML = html;
                });
        }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Render the main page."""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/prompts')
def list_prompts():
    """API endpoint to list all prompts."""
    prompts = []
    for prompt_id in loader.list_prompts():
        metadata = loader.get_prompt_metadata(prompt_id)
        prompts.append({
            'id': prompt_id,
            'type': metadata.get('type'),
            'version': metadata.get('version'),
            'description': metadata.get('description', ''),
            'tags': metadata.get('tags', [])
        })
    return jsonify({'prompts': prompts})


@app.route('/api/prompt/<prompt_id>')
def get_prompt(prompt_id):
    """API endpoint to retrieve a specific prompt."""
    try:
        content = loader.get_prompt(prompt_id)
        metadata = loader.get_prompt_metadata(prompt_id)
        hash_value = loader.get_prompt_hash(prompt_id)
        
        return jsonify({
            'id': prompt_id,
            'content': content,
            'metadata': metadata,
            'hash': hash_value
        })
    except (KeyError, FileNotFoundError) as e:
        return jsonify({'error': str(e)}), 404


@app.route('/api/audit-log')
def get_audit_log():
    """API endpoint to retrieve audit log."""
    entries = loader.get_audit_log()
    return jsonify({'entries': entries})


@app.route('/api/reload', methods=['POST'])
def reload_config():
    """API endpoint to reload configuration."""
    try:
        loader.reload()
        return jsonify({'status': 'success', 'message': 'Configuration reloaded'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    print("Starting UPSS Flask Application...")
    print("Visit http://localhost:5000 to view the application")
    app.run(debug=True, host='0.0.0.0', port=5000)
