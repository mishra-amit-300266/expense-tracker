from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Database configuration (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Expense model
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Expense {self.title}>"

# Home route (GET + POST)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data
        title = request.form['title']
        amount = float(request.form['amount'])
        date_str = request.form['date']

        # Convert date string to datetime
        date = datetime.strptime(date_str, '%Y-%m-%d')

        # Create new expense object
        new_expense = Expense(title=title, amount=amount, date=date)

        # Add to database
        db.session.add(new_expense)
        db.session.commit()

        # Redirect to home (so refresh won’t resubmit form)
        return redirect('/')

    # Fetch all expenses (for display)
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    return render_template('index.html', expenses=expenses)

@app.route('/delete/<int:id>')
def delete_expense(id):
    expense = Expense.query.get_or_404(id)  # find by ID
    db.session.delete(expense)
    db.session.commit()
    return redirect('/')

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_expense(id):
    expense = Expense.query.get_or_404(id)
    
    if request.method == 'POST':
        expense.title = request.form['title']
        expense.amount = float(request.form['amount'])
        expense.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        
        db.session.commit()
        return redirect('/')
    
    return render_template('update.html', expense=expense)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run()
