from flask import Flask, render_template, request, redirect, url_for, session
import pickle
import numpy as np

app = Flask(__name__)

# Load the trained model
with open('Bankmodel.pkl', 'rb') as f:
    model = pickle.load(f)
app.secret_key = 'your_secret_key'

USERNAME = "admin"
PASSWORD = "1234"

# Define mappings for categorical features
mappings = {
    'application_type': {'INDIVIDUAL': 0},
    'emp_length': {
        '10+ years': 0, '2 years': 1, '< 1 year': 2, '3 years': 3, '4 years': 4, '5 years': 5,
        '1 year': 6, '6 years': 7, '7 years': 8, '8 years': 9, '9 years': 10
    },
    'grade': {'B': 0, 'A': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6},
    'home_ownership': {'RENT': 0, 'MORTGAGE': 1, 'OWN': 2, 'OTHER': 3, 'NONE': 4},
    'purpose': {
        'Debt consolidation': 0, 'credit card': 1, 'other': 2, 'home improvement': 3,
        'major purchase': 4, 'small business': 5, 'car': 6, 'wedding': 7, 'medical': 8,
        'moving': 9, 'house': 10, 'vacation': 11, 'educational': 12, 'renewable_energy': 13
    },
    'verification_status': {'Not Verified': 0, 'Verified': 1, 'Source Verified': 2}
}

# Login Page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Invalid username or password.")
    return render_template('login.html')

# Home page (after login)
@app.route('/home')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        # Extract and encode categorical values
        input_data = [
            mappings['application_type'][request.form['application_type']],
            mappings['emp_length'][request.form['emp_length']],
            mappings['grade'][request.form['grade']],
            mappings['home_ownership'][request.form['home_ownership']],
            mappings['purpose'][request.form['purpose']],
            mappings['verification_status'][request.form['verification_status']],
            float(request.form['annual_income']),
            float(request.form['dti']),
            float(request.form['int_rate']),
            float(request.form['loan_amount'])
        ]

        prediction = model.predict(np.array([input_data], dtype=object))
        result = "Bad Loan" if prediction[0] == "Charged Off" else "Good Loan"
        return render_template('index.html', prediction_text=f'The loan is predicted to be: {result}')

    except Exception as e:
        return render_template('index.html', prediction_text=f'Error: {str(e)}')

# Logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
