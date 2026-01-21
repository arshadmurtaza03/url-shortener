from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import string
import random
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey123' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#Database Model
class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_url = db.Column(db.String(10), unique=True, nullable=False)

    def __repr__(self):
        return f'<Url {self.short_url}>'

#Helper Function
def generate_short_id(num_of_chars):
    """Generates a random string of fixed length"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=num_of_chars))

#Routes
@app.route('/', methods=['GET', 'POST'])
def home():
    shortened_url = None
    
    if request.method == 'POST':
        original_url = request.form['url']
        
        # Basic Validation: Check if URL starts with http
        if not original_url.startswith(('http://', 'https://')):
            original_url = 'http://' + original_url

        if original_url:
            # check if we already shortened this to save space
            existing_url = Url.query.filter_by(original_url=original_url).first()
            
            if existing_url:
                short_code = existing_url.short_url
            else:
                # Generate a new short code
                short_code = generate_short_id(5)
                # Ensure it's unique (unlikely collision but good practice)
                while Url.query.filter_by(short_url=short_code).first():
                    short_code = generate_short_id(5)
                
                new_url = Url(original_url=original_url, short_url=short_code)
                db.session.add(new_url)
                db.session.commit()
            
            # Create the full link to display
            shortened_url = request.host_url + short_code
            
    return render_template('index.html', shortened_url=shortened_url)

@app.route('/history')
def history():
    urls = Url.query.all()
    # Pass host_url so we can show clickable links in history
    return render_template('history.html', urls=urls, host_url=request.host_url)

@app.route('/<short_code>')
def redirect_to_url(short_code):
    link = Url.query.filter_by(short_url=short_code).first_or_404()
    return redirect(link.original_url)

# Create DB if it doesn't exist
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)