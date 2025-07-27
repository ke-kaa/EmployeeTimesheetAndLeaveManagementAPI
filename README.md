# Employee Timesheet and Leave Management API

This project is a Django RESTful API for managing employee timesheets and leave requests. It provides authentication, timesheet tracking, and leave management functionalities for organizations.

## Features
- User authentication and employee profile management
- Clock-in and clock-out timesheet tracking
- Calculation of working hours
- Leave request submission and approval workflow
- Team timesheet and leave overview for managers

## Project Structure
- `api_authentication/`: Handles user authentication and employee profile data
- `api_timesheet/`: Manages timesheet entries (clock-in, clock-out, working hours)
- `api_leave/`: Manages leave requests and approvals
- `EmployeeTimesheetAndLeaveManagement/`: Django project settings and configuration
- `manage.py`: Django management script

## Setup Instructions
1. **Clone the repository**
2. **Create and activate a virtual environment**
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```
5. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```
6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

## API Endpoints
- **Authentication**: `/api/auth/` (see `api_authentication/README.md`)
- **Timesheet**: `/api/timesheet/` (see `api_timesheet/README.md`)
- **Leave**: `/api/leave/` (see `api_leave/README.md`)

Refer to each app's README for detailed API documentation.

