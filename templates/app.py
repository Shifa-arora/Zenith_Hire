from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SECRET_KEY'] = 'zenith_hire a job portal' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
migrate = Migrate(app, db)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    education = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    partner_logos = ['partner1.png', 'partner2.png', 'partner3.png']
    services = [
        {'name': 'Recruitment', 'icon': 'fa fa-users', 'description': 'Connecting you with the best candidates.'},
        {'name': 'Job Matching', 'icon': 'fa fa-briefcase', 'description': 'Find the right job opportunities.'}
    ]
    portfolio = [
        {'name': 'Web Development', 'image': 'web-dev.jpg', 'description': 'Creating amazing websites.'}
    ]
    return render_template('index.html', partner_logos=partner_logos, services=services, portfolio=portfolio)

@app.route('/who-are-you')
def who_are_you():
    return render_template('who_are_you.html')

class Recruiter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(255), nullable=False)  
    company_name = db.Column(db.String(100), nullable=False)
    business_type = db.Column(db.String(50), nullable=False)
    business_description = db.Column(db.Text, nullable=False)
    website = db.Column(db.String(100), nullable=True)
    positions_hiring = db.Column(db.Text, nullable=False)
    referral_source = db.Column(db.String(50), nullable=False)
    additional_comments = db.Column(db.Text, nullable=True)
    number_of_employees = db.Column(db.Integer, nullable=True)  

@app.route('/signup-recruiter', methods=['GET', 'POST'])
def signup_recruiter():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']  
        company_name = request.form['company_name']
        business_type = request.form['business_type']
        business_description = request.form['business_description']
        website = request.form['website']
        positions_hiring = request.form['positions_hiring']
        referral_source = request.form['referral_source']
        additional_comments = request.form['additional_comments']
        number_of_employees = request.form.get('number_of_employees')  

        existing_recruiter = Recruiter.query.filter_by(email=email).first()
        if existing_recruiter:
            flash('This email is already registered. Please use a different email or log in.', 'danger')
            return redirect(url_for('signup_recruiter'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_recruiter = Recruiter(
            name=name,
            email=email,
            phone=phone,
            password=hashed_password,
            company_name=company_name,
            business_type=business_type,
            business_description=business_description,
            website=website,
            positions_hiring=positions_hiring,
            referral_source=referral_source,
            additional_comments=additional_comments,
            number_of_employees=number_of_employees  
        )

        db.session.add(new_recruiter)
        db.session.commit()

        flash('Recruiter account created successfully!', 'success')
        return redirect(url_for('index'))  

    return render_template('signup_recruiter.html')

@app.route('/signup-job-seeker', methods=['GET', 'POST'])
def signup_jobseeker():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        age = request.form['age']
        gender = request.form['gender']
        current_job_title = request.form['current_job_title']
        desired_job_title = request.form['desired_job_title']
        years_of_experience = request.form['years_of_experience']
        skills = request.form['skills']
        education_level = request.form['education_level']
        university_name = request.form['university_name']
        address = request.form['address']
        linkedin = request.form['linkedin']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        referral_source = request.form['referral_source']
        additional_comments = request.form['additional_comments']

        # Check if the email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('This email is already registered. Please use a different email or log in.', 'danger')
            return redirect(url_for('signup_jobseeker'))

        # Hash the password before storing it
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create a new User instance
        new_user = User(
            first_name=name.split()[0],  # Assuming the first name is the first part of the name
            last_name=name.split()[1] if len(name.split()) > 1 else '',  # Last name if available
            email=email,
            phone=phone,
            age=age,
            gender=gender,
            education=education_level,
            address=address,
            bio=additional_comments,  # Assuming bio can be used for additional comments
            password=hashed_password
        )

        # Add the new user to the session and commit to the database
        db.session.add(new_user)
        db.session.commit()

        flash('Job seeker account created successfully!', 'success')
        return redirect(url_for('index'))  # Redirect to the index page

    return render_template('signup_jobseeker.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')

            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        print(f'Name: {name}, Email: {email}, Message: {message}')
        flash('Your message has been sent successfully!', 'success')
        return render_template('contact.html')
    return render_template('contact.html')

@app.route('/thank-you')
def thank_you():
    return '<h1>Thank you for reaching out! We will get back to you soon.</h1>'

@app.route('/testimonial')
def testimonial():
    return render_template('testimonial.html')

@app.route('/microsoft')
def microsoft():
    return render_template('microsoft.html')

@app.route('/amazon')
def amazon():
    return render_template('amazon.html')

@app.route('/jobs') 
def jobs():
    return render_template('jobs.html') 

@app.route('/submit_question', methods=['POST'])  
def submit_question():
    question = request.form.get('question')
    print(f'Question submitted: {question}')
    flash('Your question has been submitted!', 'success')
    return redirect(url_for('index'))  

@app.route('/profile')
@login_required
def profile():
    user_data = {
        'first_name': current_user.first_name,
        'last_name': current_user.last_name,
        'gender': current_user.gender,
        'age': current_user.age,
        'phone': current_user.phone,
        'email': current_user.email,
        'address': current_user.address,
        'education': current_user.education,
        'bio': current_user.bio
    }

    return render_template('profile.html', user_data=user_data)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)