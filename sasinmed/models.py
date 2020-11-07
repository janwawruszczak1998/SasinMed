from sasinmed import db
from sqlalchemy.orm import relationship, Session
from sqlalchemy import ForeignKey, event
#from sqlalchemy.dialects.postgresql import TIME
from flask import abort, session
from sasinmed import admin
from flask_admin.contrib.sqla import ModelView


class Administrator(db.Model):
    __tablename__ = 'administrator'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    login = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'Administrator {self.login}'


class Doctor(db.Model):
    # connected with Visited one-to-zero-or-many

    __tablename__ = 'doctor'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(30), nullable=False)
    surname = db.Column(db.String(30), nullable=False)
    specialization = db.Column(db.String(50), nullable=False)

    # connections:
    visit = relationship("Visit", back_populates="doctor")

    def __repr__(self):
        return f'Doktor {self.name} {self.surname}, {self.specialization}'

class Visit(db.Model):
    # connected with Doctor zero-or-many-to-one
    # connected with Patient many-or-zer-to-one
    # connected with Visit one-to-one

    __tablename__ = 'visit'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    date_of_visit = db.Column(db.Date(), nullable=False)
    #time_of_visit = db.Column(db.Time, nullable=False)
    visible = db.Column(db.Boolean, nullable=False, default=False)

    # foreign keys:
    patient_id = db.Column(db.Integer, ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, ForeignKey('doctor.id'), nullable=False)
    diagnosis_id = db.Column(db.Integer, ForeignKey('diagnosis.id'), nullable=False)

    # connections:
    patient = relationship("Patient", back_populates="visit")
    doctor = relationship("Doctor", back_populates="visit")
    diagnosis = relationship("Diagnosis", back_populates="visit")


    def __repr__(self):
        return f'Wizyta dnia {self.date_of_visit} na godzinę {self.time_of_visit}'

class Diagnosis(db.Model):
    # connected with Visit one-to-one

    __tablename__ = "diagnosis"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    symptoms = db.Column(db.String(255), nullable=True)
    recommendation = db.Column(db.String(255), nullable=True)
    prescribed_medication = db.Column(db.String(255), nullable=True)

    # connections:
    visit = relationship("Visit", back_populates="diagnosis")

    def __repr__(self):
        return f'Objawy: {self.symptoms}, zalecenia: {self.recommendation}, recepta: {self.prescribed_medication}'

class Patient(db.Model):
    # connected with Visit one-to-many

    __tablename__ = "patient"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(30), nullable=False)
    surname = db.Column(db.String(30), nullable=False)
    pesel = db.Column(db.Integer, unique=True, nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    login = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)

    # connections:
    visit = relationship("Visit", back_populates="patient")

    def __repr__(self):
        return f'Pacjent {self.name} {self.surname}'

# deletion of diagnosis entails deletion of visit
@event.listens_for(Visit, 'before_delete')
def delete_reference(mapper, connection, target):
    # after_flush used for consistent results
    @event.listens_for(Session, 'after_flush', once=True)
    def receive_after_flush(session, context):
        # if diagnosis was deleted
        if not target.visit.diagnosis:
            session.delete(target.visit)

# deletion of visit entails deletion of diagnosis
@event.listens_for(Diagnosis, 'before_delete')
def delete_reference(mapper, connection, target):
    # after_flush used for consistent results
    @event.listens_for(Session, 'after_flush', once=True)
    def receive_after_flush(session, context):
        # if visit was deleted
        if not target.diagnosis.visit:
            session.delete(target.diagnosis)

class CustomModelView(ModelView):
    def is_accessible(self):
        if 'admin' in session:
            return True
        else:
            return abort(404)


admin.add_view(ModelView(Visit, db.session))
admin.add_view(ModelView(Doctor, db.session))
admin.add_view(ModelView(Diagnosis, db.session))
admin.add_view(ModelView(Patient, db.session))
admin.add_view(ModelView(Administrator, db.session))
