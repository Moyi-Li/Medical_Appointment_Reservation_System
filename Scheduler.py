from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime

'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    """
    TODO: Part 1
    """
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again!")
        return

    # (EXTRA) check 3: check if the password is not strong:
    if not strong_password(password):
        print("For your security, please change your password to a strong one!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    patient = Patient(username, salt=salt, hash=hash)

    # save to patient information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    # (EXTRA) check 3: check if the password is not strong:
    if not strong_password(password):
        print("For your security, please change your password to a strong one!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def login_patient(tokens):
    """
    TODO: Part 1
    """
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_patient is not None or current_caregiver is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed. Please enter login_patient <username> <password>!")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    """
    TODO: Part 2
    """
    global current_caregiver, current_patient

    # check 1: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    # check 2: check if no one login
    if (current_caregiver is None) & (current_patient is None):
        print('Please login first!')
        return

    date = tokens[1]
    date_tokens = date.split("-")

    # check 3: we assume input is hyphenated in the format mm-dd-yyyy
    if len(date_tokens) != 3:
        print("Please try again!")
        return

    try:
        month = int(date_tokens[0])
        day = int(date_tokens[1])
        year = int(date_tokens[2])

        d = datetime.datetime(year, month, day)
        caregiver = Caregiver(current_caregiver)
        vaccine = Vaccine(None, None)

        # check 4: check if there are available caregiver on that day:
        caregiver_list = caregiver.search_availabilities(d)
        if caregiver_list:
            vacc_dict = vaccine.search_vaccine()
            for each_caregiver in caregiver_list:
                for each_vaccine in vacc_dict:
                    print(f'{each_caregiver} {each_vaccine} {vacc_dict[each_vaccine]}')
        else:
            print("NO Caregiver is available!")
            print("Please try again!")

    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return


def reserve(tokens):
    """
    TODO: Part 2
    """
    global current_caregiver, current_patient

    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    # check 2: check if no user is logged in
    if current_patient is None:
        # check 3: check if the current user logged in is not a patient
        if current_caregiver:
            print('Please login as a patient!')
            return
        print('Please login first!')
        return

    date = tokens[1]
    date_tokens = date.split("-")
    need_vacc_name = tokens[2]

    # check 4: we assume input is hyphenated in the format mm-dd-yyyy
    if len(date_tokens) != 3:
        print("Please try again!")
        return

    try:
        month = int(date_tokens[0])
        day = int(date_tokens[1])
        year = int(date_tokens[2])
        d = datetime.datetime(year, month, day)

    except ValueError:
        print("Please enter a valid date!")
        return

    try:
        caregiver = Caregiver(current_caregiver)
        vaccine = Vaccine(need_vacc_name, None)
        vaccine_info = vaccine.get()
        patient = current_patient.get_username()

        # check 5: check and select the caregiver for the appointment
        caregiver_list = caregiver.search_availabilities(d)
        if caregiver_list:
            select_caregiver = caregiver_list[0]
        else:
            print("No Caregiver is available!")
            return

        # check 6: check if no such vaccine exist
        if vaccine_info:
            available_vacc_count = vaccine_info.get_available_doses()
        else:
            print("There is no Vaccine in that name available!")
            print("Please try again!")
            return

        # check 7: check if vaccines are available in amount
        if available_vacc_count >= 1:
            try:
                # make an appointment!
                reserve_appointment(patient, select_caregiver, need_vacc_name, d)
                update_caregiver_availabilities(d, select_caregiver)
                vaccine_info.decrease_available_doses(1)
            except pymssql.Error as e:
                print("Upload Availability Failed")
                print("Db-Error:", e)
                quit()
        else:
            print("Not enough available doses!")
            return

    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return


def reserve_appointment(patient, caregiver, vaccine, d):
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    try:
        add_appointment = "INSERT INTO Appointments (Patient_name, Caregiver_name, Vaccine_name, Time) VALUES (%s, %s, %s, %s)"
        cursor.execute(add_appointment, (patient, caregiver, vaccine, d))
        conn.commit()
        appointment_id = cursor.lastrowid
        print(f"Appointment ID: {appointment_id}, Caregiver username: {caregiver}")
    except pymssql.Error:
        print("Error occurred when reserving appointment")
        raise
    finally:
        cm.close_connection()


def update_caregiver_availabilities(d, select_name):
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    delete_availability = "DELETE FROM Availabilities WHERE Time = %s AND Username = %s"

    try:
        cursor.execute(delete_availability, (d, select_name))
        conn.commit()

    except pymssql.Error:
        print("Error occurred when deleting caregiver availability")


def upload_availability(tokens):
    global current_caregiver

    # check 1: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    #  check 2: check if the current logged-in user is a caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    """
    TODO: Extra Credit
    """
    pass


def strong_password(password):
    # check 1: check if length is less than 8 characters
    if len(password) < 8:
        print("Please include at least 8 characters!")
        return False

    # check 2: check if password is a mixture of both letters and numbers
    elif not any(char.isdigit() for char in password):
        print('Password should have at least one number!')
        return False

    elif not any(char.isalpha() for char in password):
        print('Password should have at least one letter!')
        return False

    # check 3: check if password is a mixture of both uppercase and lowercase
    elif not any(char.isupper() for char in password):
        print('Password should should have at least one uppercase letter!')
        return False

    elif not any(char.islower() for char in password):
        print('Password should should have at least one lowercase letter!')
        return False

    # check 4: check if the password include at least one special characters
    counts = 0
    special_characters = "!@#?"
    for char in password:
        if char in special_characters:
            counts += 1

    if counts == 0:
        print("Password should have at least one special character!")
        return False

    # All checks passed!
    return True


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):
    '''
    TODO: Part 2
    '''
    global current_caregiver, current_patient

    # check 1: the length for tokens need to be exactly 1 to include all information (with the operation name)
    if len(tokens) != 1:
        print("Please try again!")
        return

    # check 2: check if no one login
    if (current_caregiver is None) & (current_patient is None):
        print('Please login first.')
        return

    try:
        # patient login
        if current_patient is not None:
            username = current_patient.get_username()
            patient = Patient(username)
            patient.patient_appointment_info()

        # caregiver_login
        if current_patient is None:
            username = current_caregiver.get_username()
            caregiver = Caregiver(username)
            caregiver.caregiver_appointment_info()

    except Exception:
        print("Please try again!")
        return


def logout(tokens):
    """
    TODO: Part 2
    """
    global current_caregiver, current_patient

    try:
        # check 1: the length for tokens need to be exactly 1 to include all information (with the operation name)
        if len(tokens) != 1:
            print("Please try again!")
            return

        # check 2: check if no one login
        if (current_caregiver is None) & (current_patient is None):
            print('Please login first.')
            return
        else:
            current_caregiver = None
            current_patient = None
            print('Successfully logged out!')
            return

    # check 3: check if other error exists
    except Exception:
        print("Please try again!")
        return


def simple_transfer(response):
    response = response.lower()
    tokens = response.split(" ")
    return tokens


def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> Quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue

        operation = tokens[0]
        operation = operation.lower()

        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)

        elif operation == "search_caregiver_schedule":
            tokens = simple_transfer(response)
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            tokens = simple_transfer(response)
            reserve(tokens)
        elif operation == "upload_availability":
            tokens = simple_transfer(response)
            upload_availability(tokens)
        elif operation == cancel:
            cancel(tokens)
        elif operation == "add_doses":
            tokens = simple_transfer(response)
            add_doses(tokens)
        elif operation == "show_appointments":
            tokens = simple_transfer(response)
            show_appointments(tokens)
        elif operation == "logout":
            tokens = simple_transfer(response)
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
