CREATE TABLE Caregivers (
    Username VARCHAR(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Availabilities (
    Time date,
    Username VARCHAR(255) REFERENCES Caregivers(Username),
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Vaccines (
    Name VARCHAR(255),
    Doses INT,
    PRIMARY KEY (Name)
);

CREATE TABLE Patients (
    Username VARCHAR(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Reservations (
    ID INTEGER PRIMARY KEY AUTOINCREMENT, 
    Patient VARCHAR(255) REFERENCES Patient(Username),
    Caregiver VARCHAR(255) REFERENCES Caregiver(Username),
    Time DATE,
    Vaccine VARCHAR(255) REFERENCES Vaccine(Name)
);

--Can I use autoincrement? OR should I get id from maxid table and do + 1