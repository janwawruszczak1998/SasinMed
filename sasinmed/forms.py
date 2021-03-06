from flask_wtf import FlaskForm
from flask import session
from .models import Administrator, Visit, Patient, Diagnosis, Doctor
from wtforms import StringField, PasswordField, SelectField, BooleanField, HiddenField
from wtforms.widgets import HiddenInput
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, Optional, EqualTo
from wtforms.fields.html5 import IntegerField, DateField, TimeField



class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired()],
                           render_kw={"placeholder": "Username"})
    password = PasswordField('password', validators=[InputRequired()],
                             render_kw={"placeholder": "Password"})


class RegisterAdminForm(FlaskForm):
    username = StringField('username', validators=[InputRequired()], render_kw={"placeholder": "Username"})
    password = PasswordField('password', validators=[InputRequired(), EqualTo('confirm',
                                                                              message='Passwords must match')],
                             render_kw={"placeholder": "Password"})
    confirm = PasswordField('Repeat Password',  render_kw={"placeholder": "Repeat password"})
    special_key = PasswordField('admin code', validators=[InputRequired()],  render_kw={"placeholder": "Special key"})

class SearchForm(FlaskForm):
    phrase = StringField(render_kw={"placeholder": "Enter the search phrase or leave the field empty"})
    category = SelectField(render_kw={"placeholder": "Choose the category you want to search in"}, choices=[
        ('Patient', 'Pacjent'),
        ('Doctor', 'Lekarz')], validators=[InputRequired()])


class RegisterUserForm(FlaskForm):
    username = StringField('username', validators=[InputRequired()], render_kw={"placeholder": "Login"})
    password = PasswordField('password', validators=[InputRequired(), EqualTo('confirm',
                                                                              message='Pola haseł nie są takie same')],
                             render_kw={"placeholder": "Hasło"})
    confirm = PasswordField('Repeat Password', render_kw={"placeholder": "Powtórz hasło"})
    name = StringField('name', validators=[InputRequired()], render_kw={"placeholder": "Imię"})
    surname = StringField('surname', validators=[InputRequired()], render_kw={"placeholder": "Nazwisko"})
    pesel = StringField('pesel', validators=[InputRequired()], render_kw={"placeholder": "PESEL"})
    age = IntegerField('age', validators=[InputRequired()], render_kw={"placeholder": "Wiek"})
    birth_date = DateField('birth_date', validators=[InputRequired()], render_kw={"placeholder": "Data urodzenia"})


class AddVisitForm(FlaskForm):
    date_of_visit = DateField('Data wizyty', validators=[InputRequired()])
    time_of_visit = TimeField('Czas wizyty', validators=[InputRequired()])
    doctor = QuerySelectField('Lekarz', query_factory=lambda: Doctor.query.all(), validators=[InputRequired()])
    
class AddDiagnosisForm(FlaskForm):
    visit = QuerySelectField('Wizyta', query_factory=lambda: Visit.query.all(), validators=[InputRequired()])
    symptoms = StringField('Objawy', render_kw={"placeholder": "Objawy"})


class DeleteRecordForm(FlaskForm):
    id = IntegerField('ID', widget=HiddenInput(), validators=[InputRequired()])


class EditDiagnosisForm(FlaskForm):
    id = IntegerField('ID', widget=HiddenInput(), validators=[InputRequired()])
    symptoms = StringField('Objawy', render_kw={"placeholder": "Objawy"})

class EditVisitForm(AddVisitForm):
    id = IntegerField('ID', widget=HiddenInput(), validators=[InputRequired()])

class EditUserForm(FlaskForm):
    name = StringField('Imię', validators=[InputRequired()])
    surname = StringField('Nazwisko', validators=[InputRequired()])
    pesel = IntegerField('PESEL', validators=[InputRequired()])
    age = IntegerField('Wiek', validators=[InputRequired()])
    birth_date = DateField('Data urodzenia', validators=[InputRequired()])
