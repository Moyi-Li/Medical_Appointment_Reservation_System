import sys
sys.path.append("../util/*")
sys.path.append("../db/*")
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql


class Caregiver:
    def __init__(self, username, password=None, salt=None, hash=None):
        self.username = username
        self.password = password
        self.salt = salt
        self.hash = hash

    # getters
    def get(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_caregiver_details = "SELECT Salt, Hash FROM Caregivers WHERE Username = %s"
        try:
            cursor.execute(get_caregiver_details, self.username)
            for row in cursor:
                curr_salt = row['Salt']
                curr_hash = row['Hash']
                calculated_hash = Util.generate_hash(self.password, curr_salt)
                if not curr_hash == calculated_hash:
                    print("Incorrect password")
                    cm.close_connection()
                    return None
                else:
                    self.salt = curr_salt
                    self.hash = calculated_hash
                    cm.close_connection()
                    return self
        except pymssql.Error as e:
            raise e
        finally:
            cm.close_connection()
        return None

    def get_username(self):
        return self.username

    def get_salt(self):
        return self.salt

    def get_hash(self):
        return self.hash

    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_caregivers = "INSERT INTO Caregivers VALUES (%s, %s, %s)"
        try:
            cursor.execute(add_caregivers, (self.username, self.salt, self.hash))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            raise
        finally:
            cm.close_connection()

    # Insert availability with parameter date d
    def upload_availability(self, d):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_availability = "INSERT INTO Availabilities VALUES (%s , %s)"
        try:
            cursor.execute(add_availability, (d, self.username))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            print("Error occurred when updating caregiver availability")
            raise
        finally:
            cm.close_connection()

    def search_availabilities(self, d):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        name_list = []
        check_time_availability = "SELECT * FROM Availabilities WHERE Time = %s"

        try:
            cursor.execute(check_time_availability, d)
            for row in cursor:
                curr_name = row['Username']
                name_list.append(curr_name)

            return sorted(name_list)

        except pymssql.Error:
            print("Error occurred when updating caregiver availability")
            raise
        finally:
            cm.close_connection()

    def caregiver_appointment_info(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        check_availability = "SELECT * FROM Appointments WHERE Caregiver_name = %s ORDER BY AppointmentID"
        try:
            cursor.execute(check_availability, self.username)
            found_appointments = False
            print("AppointmentID Vaccine_name Date Patient_username:")

            for row in cursor:
                curr_id = row['AppointmentID']
                curr_vacc = row['Vaccine_name']
                curr_date = row['Time']
                curr_patient = row['Patient_name']
                print(f"{curr_id} {curr_vacc} {curr_date} {curr_patient}")
                found_appointments = True

            # check 3: check if the patient has any appointments
            if not found_appointments:
                print("You don't have any appointments!")
                print("Please try again!")

        except pymssql.Error:
            print("Error occurred when updating patient availability")
            raise
        finally:
            cm.close_connection()
