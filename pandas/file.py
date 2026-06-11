from flask import Flask, render_template_string, jsonify, request
import pandas as pd
import numpy as np

app = Flask(__name__)

# Core reconciliation logic separated into a function
def reconcile_data(source_list, target_list):
    df_source = pd.DataFrame(source_list)
    df_target = pd.DataFrame(target_list)

    # Outer join to capture all differences
    compare = pd.merge(df_source, df_target, on='Transaction_ID', how='outer', indicator=True)

    # Filter rows based on the merge indicator
    missing_record = compare[compare['_merge'] == 'left_only']
    orphan_record = compare[compare['_merge'] == 'right_only']

    # Convert results into clean dictionaries/lists for the UI/API
    return {
        "missing_in_target": missing_record['Transaction_ID'].tolist(),
        "orphan_in_target": orphan_record['Transaction_ID'].tolist(),
        "source_preview": df_source.to_dict(orient='records'),
        "target_preview": df_target.to_dict(orient='records')
    }

# HTML Template embedded directly for simplicity
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Data Reconciliation Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f6f9; color: #333; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h1, h2 { color: #2c3e50; }
        .btn { background: #3498db; color: white; border: none; padding: 10px 20px; font-size: 16px; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #2980b9; }
        .result-box { margin-top: 20px; padding: 15px; border-left: 5px solid #e74c3c; background: #fadbd8; border-radius: 4px; }
        .success-box { margin-top: 20px; padding: 15px; border-left: 5px solid #2ecc71; background: #d4efdf; border-radius: 4px; }
        pre { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 4px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Data Reconciliation Engine</h1>
        <p>Trigger a real-time comparison between Source and Target transaction logs.</p>
        <hr>
        
        <form action="/reconcile-ui" method="POST">
            <button type="submit" class="btn">Run Reconciliation Engine</button>
        </form>

        {% if results %}
            <div class="result-box">
                <h3>⚠️ Missing in Target (Exist in Source only):</h3>
                <strong>Transaction IDs:</strong> {{ results.missing_in_target }}
            </div>

            <div class="result-box" style="border-left-color: #f39c12; background: #fdebd0;">
                <h3>⚠️ Orphan in Target (Exist in Target only):</h3>
                <strong>Transaction IDs:</strong> {{ results.orphan_in_target }}
            </div>

            <h2>Raw JSON Payload Dispatched from API:</h2>
            <pre><code>{{ raw_json }}</code></pre>
        {% endif %}
    </div>
</body>
</html>
"""

# Route 1: Web UI Interface
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, results=None)

@app.route('/reconcile-ui', methods=['POST'])
def reconcile_ui():
    # Fixed your syntax duplicate data error from your original script snippet
    source_data = {
        'Transaction_ID': [101, 102, 103, 104],
        'Amount': [500.50, 600.00, 750.25, 1000.00],
        'Status': ['Success', 'Success', 'Pending', 'Success']
    }
    target_data = {
        'Transaction_ID': [101, 102, 103, 105],
        'Amount': [500.50, 600.00, 750.30, 1200.00],
        'Status': ['Success', 'Success', 'Pending', 'Success']
    }
    
    analysis = reconcile_data(source_data, target_data)
    return render_template_string(HTML_TEMPLATE, results=analysis, raw_json=jsonify(analysis).get_data(as_text=True))

# Route 2: Pure REST API Endpoint (For automated integrations/Postman)
@app.route('/api/v1/reconcile', methods=['POST'])
def reconcile_api():
    req_data = request.get_json()
    if not req_data or 'source' not in req_data or 'target' not in req_data:
        return jsonify({"error": "Invalid request payload. Must provide source and target lists."}), 400
        
    analysis = reconcile_data(req_data['source'], req_data['target'])
    return jsonify(analysis), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
