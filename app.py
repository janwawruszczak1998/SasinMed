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
    form = FilterForm()
    category = str(request.args["category"])
    phrase = str(request.args["phrase"])
    resource = request.query_string

    table = Visit
    column_names = table.__table__.columns.keys()  # get columns visits

    try:
        column_names.remove('id')  # remove visible field if present
    except ValueError:
        pass

    try:
        column_names.remove('visible')  # remove visible field if present
    except ValueError:
        pass

    try:
        column_names.remove('diagnosis_id')  # remove diagnosis if present
    except ValueError:
        pass


    records = table.query.all()
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

    return render_template('search.html', column_names=column_names, query_records=query_records, resource=resource,
                           form=form)


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


@app.route('/statistics')
def statistics():
    most_exclusive_priests = Priest.query.order_by(Priest.price).all()

    most_exclusive_priest = 'brak kapłanów'
    if len(most_exclusive_priests) != 0:
        most_exclusive_priest = most_exclusive_priests[-1]

    funeral_houses = Patient.query.all()
    avg_fun_house_price = 0
    if len(funeral_houses) != 0:
        sum_price = 0
        for funeral_house in funeral_houses:
            sum_price += funeral_house.price
        avg_fun_house_price = sum_price / len(funeral_houses)

    buried_number = len(Buried.query.all())

    outfits = Outfit.query.all()
    most_popular_outfit_brand = ['brak strojów', 0]

    if len(outfits) != 0:
        counter = Counter([brand.brand for brand in outfits])
        most_popular_outfit_brand = counter.most_common(1)[0]

    most_popular_container_type = ['brak pojemników', 0]
    containers = Container.query.all()

    if len(containers) != 0:
        counter = Counter([container.type_of_container for container in containers])
        most_popular_container_type = counter.most_common(1)[0]

    most_expensive_funeal = 0
    funerals = Funeral.query.order_by(Funeral.total_price).all()
    if len(funerals):
        most_expensive_funeal = funerals[-1].total_price

    burieds = Buried.query.all()
    most_popular_cause_of_death = ['brak pochowanych', 'brak danych']
    if len(burieds) != 0:
        counter = Counter([buried.cause_of_death for buried in burieds])
        most_popular_cause_of_death = counter.most_common(1)[0]

    return render_template('statistics.html', most_exclusive_priest=most_exclusive_priest,
                           avg_fun_house_price=avg_fun_house_price, buried_number=buried_number,
                           most_popular_outfit_brand=most_popular_outfit_brand,
                           most_popular_container_type=most_popular_container_type,
                           most_expensive_funeal=most_expensive_funeal,
                           most_popular_cause_of_death=most_popular_cause_of_death)


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


@app.route('/dashboard/buried', methods=['GET', 'POST'])
@check_logged_in_user
def user_buried():
    delete_record_form = DeleteRecordForm()
    diagnosis_form = AddBuriedForm()
    edit_diagnosis_form = EditBuriedForm()

    if request.method == 'POST':
        if edit_diagnosis_form.validate_on_submit():

            diagnosis_id = edit_diagnosis_form.id.data
            diagnosis_to_edit = Diagnosis.query.filter_by(id=diagnosis_id).first()

            diagnosis_to_edit.symptoms = edit_diagnosis_form.symptoms.data
            diagnosis_to_edit.recommendation = edit_diagnosis_form.recommendation.data
            diagnosis_to_edit.prescribed_medication = edit_diagnosis_form.prescribed_medication.data

            db.session.commit()

        elif delete_record_form.validate_on_submit():
            diagnosis_id = delete_record_form.id.data
            diagnosis_to_delete = Diagnosis.query.filter_by(id=diagnosis_id).first()

            db.session.delete(diagnosis_to_delete)
            db.session.commit()

        elif diagnosis_form.validate_on_submit():
            new_diagnosis = Diagnosis(visit_id=diagnosis_form.visit.data.id, symptoms=diagnosis_form.symptoms.data, 
                                recommendation=diagnosis_form.recommendation.data,
                                prescribed_medication=diagnosis_form.prescribed_medication.data)
            db.session.add(new_diagnosis)
            db.session.commit()

    diagnosis = Diagnosis.query.join(Visit).join(Patient).filter_by(name=session['username']).all()
    diagnosis_header = ['', 'visit', 'symptoms', 'recommendation', 'prescribed_medication', '']

    return render_template('user_buried.html', diagnosis_form=diagnosis_form,
                           diagnosis_header=diagnosis_header, delete_record_form=delete_record_form,
                           edit_diagnosis_form=edit_diagnosis_form)


@app.route('/dashboard/funerals', methods=['GET', 'POST'])
@check_logged_in_user
def user_funerals():
    visit_form = AddFuneralForm()
    delete_record_form = DeleteRecordForm()
    edit_visit_form = EditFuneralForm()

    if request.method == 'POST':
        if edit_visit_form.validate_on_submit():
            visit_id = edit_visit_form.id.data
            visit_to_edit = Visit.query.filter_by(id=visit_id).first()
            visit_to_edit.date_of_visit = edit_visit_form.date_of_visit.data
            visit_to_edit.time_of_visit = edit_visit_form.time_of_visit.data
            visit_to_edit.visible = edit_visit_form.visible
            db.session.commit()

        elif delete_record_form.validate_on_submit():
            visit_id = delete_record_form.id.data
            visit_to_delete = Visit.query.filter_by(id=visit_id).first()
            diagnosis_in_visit = Diagnosis.query.filter_by(visit_id=visit_id).first()

            db.session.delete(diagnosis_in_visit)
            db.session.commit()

        elif visit_form.validate_on_submit():
            new_visit = Visit(visible=False,  patient_id=session['patient_id'], doctor_id=visit_form.doctor.data.id, date_of_visit=visit_form.date_of_visit.data, time_of_visit=visit_form.time_of_visit.data)
            db.session.add(new_visit)
            db.session.commit()

    else:
        print('Błąd formularza')

    visits = Visit.query.join(Patient).filter(Patient.name == session['username']).all()
    visit_header = ['', 'id', 'date', 'time', 'doctor', '']

    return render_template('user_funerals.html', visit_form=visit_form, visits=visits,
                           visit_header=visit_header, delete_record_form=delete_record_form,
                           edit_visit_form=edit_visit_form)


if __name__ == '__main__':
    app.run(debug=True)