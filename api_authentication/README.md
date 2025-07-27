# API Authentication

This app manages user authentication and employee profile information for the Employee Timesheet and Leave Management system.

## Features
- User registration and login (JWT-based)
- Employee profile management (with extra fields)
- Password reset (initial and regular)
- Role-based permissions: EMPLOYEE, MANAGER, ADMIN
- Manager/admin account creation for employees

## Main Files
- `models.py`: Defines the `EmployeeModel` (extra profile fields, roles, manager linkage)
- `serializers.py`: Handles validation, creation, and update of users and employees
- `views.py`: API endpoints for login, registration, password reset, and profile
- `permissions.py`: Custom permission classes (e.g., `IsManager`)
- `urls.py`: URL routing for authentication endpoints

## API Endpoints
- `POST /token/` — Obtain JWT token (login)
- `POST /token/refresh/` — Refresh JWT token
- `POST /create/account/` — Create employee account (admin/manager only)
- `POST /reset-initial-password/` — Set initial password (first login)
- `GET/PUT /employee/me/` — Retrieve or update own employee profile

## Usage
1. Add `api_authentication` to your Django `INSTALLED_APPS`.
2. Ensure `rest_framework` and `rest_framework_simplejwt` are installed and configured.
3. Use the provided endpoints for authentication and profile management.

See the main project README for setup instructions.
