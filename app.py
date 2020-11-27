from flask import render_template, redirect, url_for, request, session, flash
from sasinmed import app, db
from sasinmed.forms import *
from sasinmed.models import *
from collections import Counter
from sasinmed.models import Administrator, Visit, Patient, Diagnosis, Doctor
from werkzeug.security import generate_password_hash, check_password_hash
from sasinmed.utils import check_logged_in_user
from flask_whooshee import *

from android_views import *

ws = WhoosheeQuery.whooshee_search

@app.route('/', methods=['GET'])
def home_page():
    form = SearchForm()
    if form.validate_on_submit():
        redirect(url_for('search'))
    return render_template('home.html', form=form)


@app.route('/search', methods=['GET'])
def search():
    resource = request.query_string

    table = Visit
    column_names = table.__table__.columns.keys()  # get columns visits

    try:
        column_names.remove('id') 
    except ValueError:
        pass

    try:
        column_names.remove('diagnosis_id')  # remove diagnosis if present
    except ValueError:
        pass

    records = table.query.order_by(table.date_of_visit).order_by(table.time_of_visit).all()
    query_records = []  # list of dictionaries (dict = record) to store in session

    for record in records:
        row = {}
        for column_name in column_names:
            data = record.__dict__[column_name]
            if data is not None and data != "":
                if column_name == "patient_id":
                    data = repr(Patient.query.filter_by(id=data).first())
                elif column_name == "doctor_id":
                    data = repr(Doctor.query.filter_by(id=data).first())
                row[column_name] = str(data)
            else:
                row[column_name] = "brak"

        row["patient"] = row.pop("patient_id")
        row["doctor"] = row.pop("doctor_id")
        query_records.append(row)

    column_names[column_names.index("patient_id")] = "patient"
    column_names[column_names.index("doctor_id")] = "doctor"

    session['column_names'] = column_names
    session['query_records'] = query_records

    print(query_records)

    return render_template('search.html', column_names=column_names, query_records=query_records, resource=resource)


@app.route('/search/<string:resource>/filter', methods=['GET'])
def filter(resource):
    form = FilterForm()
    text = str(request.args["text"])
    filtered_records = []
    column_names = session.get('column_names', None)
    query_records = session.get('query_records', None)

    if text == "":
        filtered_records = query_records
    else:
        for record in query_records:
            for column_name in column_names:
                data = record[column_name]
                if data != "brak" and text.casefold() in str(data).casefold():
                    filtered_records.append(record)
                    break

    return render_template('filter.html', column_names=column_names, filtered_records=filtered_records,
                           resource=resource, form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if 'logged' in session:
        if 'admin' in session:
            return redirect('/admin')
        elif 'user' in session:
            return redirect(url_for('dashboard'))

    session.permanent = True
    if form.validate_on_submit():
        admin = Administrator.query.filter_by(login=form.username.data).first()
        user = Patient.query.filter_by(login=form.username.data).first()

        if admin:
            if check_password_hash(admin.password, form.password.data):
                session['logged'] = True
                session['admin'] = True
                return redirect('/admin')
            else:
                flash('Nieprawidłowy login lub hasło')
        elif user:
            if check_password_hash(user.password, form.password.data):
                session['logged'] = True
                session['user'] = True
                session['username'] = user.name
                session['patient_id'] = user.id
                return redirect(url_for('dashboard'))
            else:
                flash('Nieprawidłowy login lub hasło')
        else:
            flash('Nieprawidłowy login lub hasło')

    return render_template('login.html', form=form)



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/signup-admin', methods=['GET', 'POST'])
def signup_admin():
    form = RegisterAdminForm()
    if form.validate_on_submit():
        if form.special_key.data == 'admin':
            hashed_password = generate_password_hash(form.password.data, method='sha256')

            if Administrator.query.filter_by(login=form.username.data).first() or Patient.query.filter_by(
                    login=form.username.data).first():
                flash('Nazwa jest już zajęta')
            else:
                new_admin = Administrator(login=form.username.data, password=hashed_password)
                db.session.add(new_admin)
                db.session.commit()
                flash('Stworzono nowego administratora')

        else:
            flash('Nieprawidłowy kod administratorski')

    return render_template('signup-admin.html', form=form)


@app.route('/signup-user', methods=['GET', 'POST'])
def signup_user():
    form = RegisterUserForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')

        if Administrator.query.filter_by(login=form.username.data).first() or Patient.query.filter_by(
                login=form.username.data).first():
            flash('Nazwa jest już zajęta')
        else:
            new_user = Patient(login=form.username.data, password=hashed_password, name=form.name.data,
                                   surname=form.surname.data, pesel=form.pesel.data, birth_date=form.birth_date.data,
                                   age=form.age.data)
            db.session.add(new_user)
            db.session.commit()
            flash('Stworzono nowe konto')

    return render_template('signup-user.html', form=form)


@app.route('/dashboard', methods=['POST', 'GET'])
@check_logged_in_user
def dashboard():
    edit_user_details = EditUserForm()
    current_user = Patient.query.filter_by(name=session['username']).first()

    if request.method == 'POST':
        if edit_user_details.validate_on_submit():
            current_user.name = edit_user_details.name.data
            current_user.surname = edit_user_details.surname.data
            current_user.pesel = edit_user_details.pesel.data
            current_user.age = edit_user_details.age.data
            current_user.birth_date = edit_user_details.birth_date.data
            db.session.commit()
            session['username'] = current_user.name
        else:
            flash('Wystąpił błąd. Skontaktuj się z administratorem')

    return render_template('dashboard.html', edit_user_details=edit_user_details, current_user=current_user)


@app.route('/dashboard/diagnosis', methods=['GET', 'POST'])
@check_logged_in_user
def user_diagnosis():
    delete_record_form = DeleteRecordForm()
    diagnosis_form = AddDiagnosisForm()
    edit_diagnosis_form = EditDiagnosisForm()

    if request.method == 'POST':
        if edit_diagnosis_form.validate_on_submit():

            diagnosis_id = edit_diagnosis_form.id.data
            diagnosis_to_edit = Diagnosis.query.filter_by(id=diagnosis_id).first()

            diagnosis_to_edit.id = edit_diagnosis_form.id.data
            diagnosis_to_edit.symptoms = edit_diagnosis_form.symptoms.data
            print("edycja diagnozy")
            print(edit_diagnosis_form.errors)
            db.session.commit()

        elif delete_record_form.validate_on_submit():
            diagnosis_id = delete_record_form.id.data
            diagnosis_to_delete = Diagnosis.query.filter_by(id=diagnosis_id).first()
            
            print("usuwanie diagnozy")
            print(delete_record_form.errors)
            
            db.session.delete(diagnosis_to_delete)
            db.session.commit()

        # elif diagnosis_form.validate_on_submit():
        #     new_diagnosis = Diagnosis(visit_id=diagnosis_form.visit.data.id, symptoms=diagnosis_form.symptoms.data)
        #     db.session.add(new_diagnosis)
        #     db.session.commit()
        #     print("dodanie diagnozy")

    diagnosis = Diagnosis.query.join(Visit).join(Patient).filter_by(name=session['username']).all()
    diagnosis_header = ['', 'id', 'wizyta', 'objawy', 'zalecenia', 'recepta', '']

    return render_template('user_diagnosis.html', diagnosis=diagnosis, diagnosis_form=diagnosis_form,
                           diagnosis_header=diagnosis_header, delete_record_form=delete_record_form,
                           edit_diagnosis_form=edit_diagnosis_form)


@app.route('/dashboard/visits', methods=['GET', 'POST'])
@check_logged_in_user
def user_visits():
    visit_form = AddVisitForm()
    delete_record_form = DeleteRecordForm()
    edit_visit_form = EditVisitForm()

    if request.method == 'POST':
        if edit_visit_form.validate_on_submit():
            visit_id = edit_visit_form.id.data
            visit_to_edit = Visit.query.filter_by(id=visit_id).first()
            visit_to_edit.date_of_visit = edit_visit_form.date_of_visit.data
            visit_to_edit.time_of_visit = edit_visit_form.time_of_visit.data
            visit_to_edit.doctor_id = edit_visit_form.doctor.data.id

            print("edycja visyty")

            db.session.commit()

        elif delete_record_form.validate_on_submit():
            visit_id = delete_record_form.id.data
            visit_to_delete = Visit.query.filter_by(id=visit_id).first()

            print("usuniecie visyty")

            db.session.delete(visit_to_delete)
            db.session.commit()

        elif visit_form.validate_on_submit():
            new_visit = Visit(visible=False,  patient_id=session['patient_id'], doctor_id=visit_form.doctor.data.id, date_of_visit=visit_form.date_of_visit.data, time_of_visit=visit_form.time_of_visit.data)
            db.session.add(new_visit)
            print("dodanie vizyty")

            db.session.commit()


    visits = Visit.query.join(Patient).filter(Patient.name == session['username']).all()
    visit_header = ['', 'id', 'data', 'godzina', 'lekarz', '']

    return render_template('user_visits.html', visit_form=visit_form, visits=visits,
                           visit_header=visit_header, delete_record_form=delete_record_form,
                           edit_visit_form=edit_visit_form)


if __name__ == '__main__':
    app.run(debug=True)
