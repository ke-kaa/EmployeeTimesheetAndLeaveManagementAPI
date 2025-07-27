# API Leave

This app handles employee leave requests and approvals for the Employee Timesheet and Leave Management system.

## Features
- Submit leave requests (date range, reason)
- Approve or reject leave requests (for managers/admins)
- View personal leave history
- Team leave overview for managers
- Status tracking: Pending, Approved, Rejected

## Main Files
- `models.py`: Defines `LeaveRequestModel` (leave request, status, approval)
- `serializers.py`: Validation and serialization for leave requests
- `views.py`: API endpoints for leave creation, listing, approval, and rejection
- `permissions.py`: Custom permission classes (e.g., `IsManager`)
- `urls.py`: URL routing for leave endpoints

## API Endpoints
- `POST /api/leave-request/` — Submit a leave request
- `GET /api/leave-request/me/` — View your leave requests
- `GET /api/leave-request/team/` — Managers: view team leave requests
- `POST /api/leave-request/<id>/approve/` — Approve a leave request
- `POST /api/leave-request/<id>/reject/` — Reject a leave request

## Usage
1. Add `api_leave` to your Django `INSTALLED_APPS`.
2. Run migrations to create leave-related tables.
3. Use the endpoints to manage leave requests and approvals.

See the main project README for setup instructions.
