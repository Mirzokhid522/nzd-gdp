from flask import Flask, render_template, jsonify
import pandas as pd
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_gdp_data():
    csv_path = os.path.join(os.path.dirname(__file__), 'gdp.csv')
    
    if not os.path.exists(csv_path):
        return jsonify({"error": "gdp.csv not found"}), 404

    try:
        records = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines:
            parts = [p.strip().strip('"') for p in line.split(',')]
            if len(parts) >= 3:
                quarter = parts[0]
                if any(q in quarter for q in ['Q1', 'Q2', 'Q3', 'Q4']):
                    try:
                        year_num = int(quarter[:4])
                        # Filter from 2024 onwards for high-resolution large chart layout
                        if year_num >= 2024:
                            yoy_val = float(parts[1]) if parts[1] not in ['..', '', 'NaN'] else None
                            qoq_val = float(parts[2]) if parts[2] not in ['..', '', 'NaN'] else None
                            
                            records.append({
                                "quarter": quarter,
                                "yoy": yoy_val,
                                "qoq": qoq_val
                            })
                    except ValueError:
                        continue
                        
        return jsonify(records)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=2333)