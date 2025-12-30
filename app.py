from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# --- App setup ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-me' 

# Ensure DB is placed under instance/firstapp.db
basedir = os.path.abspath(os.path.dirname(__file__))
instance_folder = os.path.join(basedir, 'instance')
db_file = os.path.join(instance_folder, 'firstapp.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database ---
class FirstApp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=False)
    phone = db.Column(db.String(30))
    created_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Person {self.id} {self.first_name}>'

# --- Routes ---
@app.route('/info')
def info():
    return render_template('info.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form values
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()

        if not first_name:
            flash('First name is required.', 'danger')
            return redirect(url_for('index'))

        new_person = FirstApp(
            first_name=first_name,
            last_name=last_name or None,
            email=email or None,
            phone=phone or None
        )
        db.session.add(new_person)
        db.session.commit()
        flash('Record added successfully.', 'success')
        return redirect(url_for('index'))

    persons = FirstApp.query.order_by(FirstApp.id).all()
    return render_template('index.html', persons=persons)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    person = FirstApp.query.get_or_404(id)
    if request.method == 'POST':
        person.first_name = request.form.get('first_name', person.first_name).strip()
        person.last_name = request.form.get('last_name', person.last_name).strip()
        person.email = request.form.get('email', person.email).strip()
        person.phone = request.form.get('phone', person.phone).strip()
        db.session.commit()
        flash('Record updated successfully.', 'success')
        return redirect(url_for('index'))
    return render_template('update.html', person=person)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    person = FirstApp.query.get_or_404(id)
    db.session.delete(person)
    db.session.commit()
    flash('Record deleted.', 'warning')
    return redirect(url_for('index'))

# Create instance folder
if __name__ == '__main__':
    if not os.path.exists(instance_folder):
        os.makedirs(instance_folder)
    with app.app_context():
        db.create_all()   
    app.run(debug=True)
