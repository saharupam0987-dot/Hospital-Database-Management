
# Hospital Management System

A web-based Hospital Management System built with Django and PostgreSQL.

## Features

- User authentication and role-based access control
- Patient management
- Doctor management
- Appointment scheduling
- Patient admissions and room availability management
- Test scheduling and report uploads
- Operation management, doctor assignments, and report uploads
- Form validation for date and time fields

## Technologies Used

- Python
- Django
- PostgreSQL
- HTML
- Git

## Requirements

- Python
- PostgreSQL
- pip

## Setup Instructions

1. Clone or download the project.
2. Create and activate a Python virtual environment.
3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create the PostgreSQL database configured in `hospital_project/settings.py`.
5. Set the required environment variables:
   - `DJANGO_SECRET_KEY`
   - `DB_PASSWORD`

   Keep their values private. Do not commit credentials to Git.

6. Apply database migrations:

   ```bash
   python manage.py migrate
   ```

7. Create a Django user and assign an appropriate role through the project's profile management.
8. Start the development server:

   ```bash
   python manage.py runserver
   ```

9. Open http://127.0.0.1:8000/ in your browser.

## Running Tests

Run the automated tests with:

```bash
python manage.py test
```

## Security Note

This project is currently configured for local development. Additional security configuration is required before production deployment.
