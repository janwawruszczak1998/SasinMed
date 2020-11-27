from flask import jsonify

from sasinmed import app
from sasinmed.models import Administrator, Visit, Patient, Diagnosis, Doctor


@app.route('/mobile/hello')
def mobile_hello_world():
    return 'Hello, World!'


@app.route('/mobile/search', methods=['GET'])
def mobile_search():
    #resource = request.query_string

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
        row["dateOfVisit"] = row.pop("date_of_visit")
        row["timeOfVisit"] = row.pop("time_of_visit")
        query_records.append(row)

    return jsonify(query_records)
