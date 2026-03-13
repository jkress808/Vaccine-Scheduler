from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import sqlite3
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def is_strong_password(password):
    if len(password) < 8:
        return False
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    if not any(c in "!@#?" for c in password):
        return False
    return True


def create_patient(tokens):
    if len(tokens) != 3:
        print("Create patient failed")
        return

    username = tokens[1]
    password = tokens[2]
    if not is_strong_password(password):
        print('Create patient failed, please use a strong password (8+ char, at least one upper and one lower, at least one letter and one number, and at least one special character, from "!", "@", "#", "?")')
        return
    if username_exists_patient(username):
        print("Username taken, try again")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    patient = Patient(username, salt=salt, hash=hash)

    try:
        patient.save_to_db()
    except sqlite3.Error as e:
        print("Create patient failed")
        return
    except Exception as e:
        print("Create patient failed")
        return
    print("Created user", username)


def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = ?"
    try:
        cursor = conn.cursor()
        cursor.execute(select_username, (username,))
        for row in cursor:
            cm.close_connection()
            return row['Username'] is not None
    except sqlite3.Error as e:
        print("Error occurred when checking username")
        cm.close_connection()
        return True
    except Exception as e:
        print("Error occurred when checking username")
        cm.close_connection()
        return True
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
    if not is_strong_password(password):
        print('Create caregiver failed, please use a strong password (8+ char, at least one upper and one lower, at least one letter and one number, and at least one special character, from \"!\", \"@\", \"#\", \"?\")')
        return
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except sqlite3.Error as e:
        print("Create patient failed")
        return
    except Exception as e:
        print("Create patient failed")
        return
    print("Created user", username)


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = ?"
    try:
        cursor = conn.cursor()
        cursor.execute(select_username, (username,))
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            cm.close_connection()
            return row['Username'] is not None
    except sqlite3.Error as e:
        print("Error occurred when checking username")
        cm.close_connection()
        return True
    except Exception as e:
        print("Error occurred when checking username")
        cm.close_connection()
        return True
    cm.close_connection()
    return False


def login_patient(tokens):
 
    global current_patient
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in, try again")
        return

    if len(tokens) != 3:
        print("Login patient failed")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except sqlite3.Error as e:
        print("Login patient failed")
        return
    except Exception as e:
        print("Login failed")
        return

    if patient is None:
        print("Login patient failed")
    else:
        print("Logged in as " + username)
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
    except sqlite3.Error as e:
        print("Login failed.")
        return
    except Exception as e:
        print("Login failed.")
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver



def search_caregiver_schedule(tokens):
    cm = ConnectionManager()
    conn = cm.create_connection()

    if len(tokens) != 2:
        print("Please try again")
        return
    
    if current_caregiver is None and current_patient is None:
        print("Please login first")
        return
        
    time = tokens[1]

    try:
        datetime.datetime.strptime(time, "%Y-%m-%d")
    except ValueError:
        print("Please try again")
        return
    
    select_caregivers = "SELECT Username FROM Availabilities WHERE Time = ? ORDER BY Username"
    try:
        cursor = conn.cursor()
        cursor.execute(select_caregivers, (time,))
        print("Caregivers:")
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                print(row[0])
        else:
            print("No caregivers available")
    except sqlite3.Error as e:
        print("Please try again")
        cm.close_connection()
        return
    except Exception as e:
        print("Please try again")
        cm.close_connection()
        return
        
    select_vaccines = "SELECT Name, Doses FROM Vaccines"
    try:
        cursor.execute(select_vaccines)
        print("Vaccines:")
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                print(row[0], row[1])
        else:
            print("No vaccines available")
    except sqlite3.Error as e:
        print("Please try again")
        cm.close_connection()
        return
    except Exception as e:
        print("Please try again")
        cm.close_connection()
        return

    cm.close_connection()

def reserve(tokens):
    cm = ConnectionManager()
    conn = cm.create_connection()
    if len(tokens) != 3:
        print("Please try again")
        return
    if current_caregiver is None and current_patient is None:
        print("Please login first")
        return
    
    if current_patient is None:
        print("Please login as a patient")
        return
    
    time = tokens[1]
    try:
        datetime.datetime.strptime(time, "%Y-%m-%d")
    except ValueError:
        print("Please try again")
        return
    vaccine = tokens[2]
    create_reservation = "INSERT INTO Reservations (Patient, Caregiver, Time, Vaccine) Values (?,?,?,?)"
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Username FROM Availabilities WHERE time = ? ORDER BY Username ASC",  (tokens[1],))
        caregiver = cursor.fetchone()
        cursor.execute("SELECT Doses FROM Vaccines WHERE Name = ?", (tokens[2],))
        doses = cursor.fetchone()
        if doses is None or doses[0] == 0:
            print("Not enough available doses")
        elif caregiver is None:
            print("No caregiver is available")
        else:
            cursor.execute(create_reservation, (current_patient.get_username(), caregiver[0], tokens[1], tokens[2]))
            conn.commit()
            cursor.execute("SELECT ID, Caregiver FROM Reservations WHERE time = ? AND Caregiver =?", (time, caregiver[0]))
            rows = cursor.fetchone()
            cursor.execute("DELETE FROM Availabilities WHERE Username = ? AND Time = ?", (caregiver[0], time))
            cursor.execute("UPDATE Vaccines SET Doses = Doses - 1 WHERE Name = ?", (vaccine,))
            conn.commit()
            print(f"Appointment ID {rows[0]}, Caregiver username {rows[1]}")


    except sqlite3.Error as e:
        print("Please try again")
        cm.close_connection()
        return
    except Exception as e:
        print("Please try again")
        cm.close_connection()
        return
    cm.close_connection()




def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format yyyy-mm-dd
    date_tokens = date.split("-")
    year = int(date_tokens[0])
    month = int(date_tokens[1])
    day = int(date_tokens[2])
    try:
        d = datetime.date(year, month, day)
        current_caregiver.upload_availability(d)
    except sqlite3.Error as e:
        print("Upload Availability Failed")
        return
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        return
    print("Availability uploaded!")


def cancel(tokens):
    """
    TODO: Extra Credit
    """
    pass


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
    except sqlite3.Error as e:
        print("Error occurred when adding doses")
        return
    except Exception as e:
        print("Error occurred when adding doses")
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except sqlite3.Error as e:
            print("Error occurred when adding doses")
            return
        except Exception as e:
            print("Error occurred when adding doses")
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except sqlite3.Error as e:
            print("Error occurred when adding doses")
            return
        except Exception as e:
            print("Error occurred when adding doses")
            return
    print("Doses updated!")


def show_appointments(tokens):
    cm = ConnectionManager()
    conn = cm.create_connection()

    if len(tokens) != 1:
        print("Please try again")
        return

    if current_caregiver is None and current_patient is None:
        print("Please login first")
        return
    user = current_caregiver
    if current_patient:
        user = current_patient
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT ID, Vaccine, Time, Caregiver FROM Reservations WHERE Patient = ? ORDER BY ID", (user.get_username(), ))
            appointments = cursor.fetchall()
            if appointments:
             for row in appointments:
                print(f"{row[0]} {row[1]} {row[2]} {row[3]}")
             return
            else:
                print("No appointments scheduled")
        except sqlite3.Error as e:
            print("Please try again now")
            cm.close_connection()
            return
        
        except Exception as e:
            print("Please try again now")
            cm.close_connection()
            return
        cm.close_connection()
    elif user:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT ID, Vaccine, Time, Patient FROM Reservations WHERE Caregiver = ? ORDER BY ID", (user.get_username(), ))
            appointments = cursor.fetchall()
            if appointments:
             for row in appointments:
                print(f"{row[0]} {row[1]} {row[2]} {row[3]}")
             return
            else:
                print("No appointments scheduled")
    
        except sqlite3.Error as e:
            print("Please try again")
            cm.close_connection()
            return
        
        except Exception as e:
            print("Please try again")
            cm.close_connection()
            return
        cm.close_connection()



def logout(tokens):

    if len(tokens) != 1:
        print("Please try again")
        return

    global current_caregiver
    global current_patient
    if current_caregiver is None and current_patient is None:
        print("Please login first")
        return
    elif current_caregiver is not None or current_patient is not None:
        current_caregiver = None
        current_patient = None
        print("Successfully logged out")
        return
    else:
        print("Please try again")
        return


def start():
    stop = False
    print("*** Please enter one of the following commands ***")
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
    print("> quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        ## response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == cancel:
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
