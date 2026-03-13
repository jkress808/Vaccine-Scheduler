# Vaccine Scheduler

A command-line COVID-19 vaccine appointment scheduling application built in Python, backed by a SQLite relational database. Supports two user roles — patients and caregivers — with secure account management, appointment booking, and vaccine inventory tracking.

## Features

- **Account creation & authentication** — separate registration and login flows for patients and caregivers, with salted + hashed password storage
- **Strong password enforcement** — passwords must be 8+ characters with at least one uppercase letter, lowercase letter, digit, and special character (`!`, `@`, `#`, `?`)
- **Caregiver availability** — caregivers can upload dates they're available to administer vaccines
- **Appointment scheduling** — patients can search available caregivers by date, view vaccine inventory, and reserve an appointment; the system auto-assigns the first available caregiver alphabetically
- **Vaccine inventory management** — caregivers can add new vaccines or increase doses for existing ones; doses are decremented automatically when appointments are booked
- **Appointment history** — both patients and caregivers can view their scheduled appointments

## Tech Stack

- **Python** — application logic and CLI
- **SQLite** — local relational database
- **SQL** — schema design with foreign key constraints and `AUTOINCREMENT` primary keys

## Database Schema

| Table | Description |
|---|---|
| `Caregivers` | Caregiver accounts (username, salt, hash) |
| `Patients` | Patient accounts (username, salt, hash) |
| `Availabilities` | Caregiver availability by date |
| `Vaccines` | Vaccine inventory (name, dose count) |
| `Reservations` | Booked appointments linking patient, caregiver, date, and vaccine |

## How to Run

**Prerequisites:** Python 3.x

1. Clone the repo:
   ```
   git clone https://github.com/jkress808/Vaccine-Scheduler.git
   ```

2. Navigate to the scheduler directory:
   ```
   cd Vaccine-Scheduler/src/main/scheduler
   ```

3. Run the application:
   ```
   python Scheduler.py
   ```

## Available Commands

| Command | Role | Description |
|---|---|---|
| `create_patient <username> <password>` | — | Register a new patient account |
| `create_caregiver <username> <password>` | — | Register a new caregiver account |
| `login_patient <username> <password>` | — | Log in as a patient |
| `login_caregiver <username> <password>` | — | Log in as a caregiver |
| `search_caregiver_schedule <date>` | Patient or Caregiver | Show available caregivers and vaccine inventory for a given date (`YYYY-MM-DD`) |
| `reserve <date> <vaccine>` | Patient | Book an appointment for a given date and vaccine |
| `upload_availability <date>` | Caregiver | Mark yourself as available on a given date |
| `add_doses <vaccine> <number>` | Caregiver | Add vaccine doses to inventory (creates vaccine if it doesn't exist) |
| `show_appointments` | Patient or Caregiver | View your scheduled appointments |
| `logout` | — | Log out the current user |
| `quit` | — | Exit the application |
