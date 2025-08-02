from flask import Flask, render_template, request, jsonify
import mysql.connector
from db_config import DBCONFIG  

app = Flask(__name__)


@app.route('/api/cpes', methods=['GET'])
def get_cpes_json():
    try:
        
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit

        
        conn = mysql.connector.connect(**DBCONFIG)
        cursor = conn.cursor(dictionary=True)

        
        cursor.execute("SELECT COUNT(*) AS total FROM cpentries")
        total = cursor.fetchone()['total']

       
        cursor.execute("""
            SELECT * FROM cpentries
            ORDER BY id
            LIMIT %s OFFSET %s
        """, (limit, offset))
        data = cursor.fetchall()

        
        cursor.close()
        conn.close()

       
        return jsonify({
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit,
            "data": data
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/')
def index():
    try:
        page = int(request.args.get('page', 1))
        limit = 10
        offset = (page - 1) * limit

        conn = mysql.connector.connect(**DBCONFIG)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) AS total FROM cpentries")
        total = cursor.fetchone()['total']
        total_pages = (total + limit - 1) // limit

        cursor.execute("""
            SELECT * FROM cpentries
            ORDER BY id
            LIMIT %s OFFSET %s
        """, (limit, offset))
        data = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template("index.html", cpes=data, page=page, total_pages=total_pages)

    except Exception as e:
        return f"<h2>Error loading page: {e}</h2>"


if __name__ == '__main__':
    app.run(debug=True)
