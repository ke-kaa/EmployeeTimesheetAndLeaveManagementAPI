# API Timesheet

This app manages employee timesheet entries, including clock-in and clock-out functionality, for the Employee Timesheet and Leave Management system.

## Features
- Clock-in and clock-out endpoints
- Automatic calculation of working hours
- View personal timesheet entries
- Manager/team timesheet overview

## Main Files
- `models.py`: Defines `TimesheetModel` (clock-in/out, working hours)
- `serializers.py`: Validation and serialization for timesheet entries
- `views.py`: API endpoints for clock-in, clock-out, and timesheet listing
- `permissions.py`: Custom permission classes (e.g., `IsManager`)
- `urls.py`: URL routing for timesheet endpoints

## API Endpoints
- `POST /api/timesheet/clock-in/` — Clock in
- `POST /api/timesheet/clock-out/` — Clock out
- `GET /api/timesheet/me/` — View your timesheet entries
- `GET /api/timesheet/team/` — Managers: view team timesheets

## Usage
1. Add `api_timesheet` to your Django `INSTALLED_APPS`.
2. Run migrations to create timesheet-related tables.
3. Use the endpoints to manage timesheet entries and team overviews.

See the main project README for setup instructions.
