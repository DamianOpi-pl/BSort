# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is "BSort" (formerly "Sortownia"), a Django-based web application for managing a clothing sorting facility. The application tracks bags of clothing through a multi-step sorting process, from initial reception to final destination routing.

## Common Development Commands

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser

# Populate test data
python manage.py populate_data

# Run development server
python manage.py runserver

# Collect static files
python manage.py collectstatic
```

### Docker Development
```bash
# Build and run with Docker Compose
docker-compose up --build

# Run migrations in container
docker-compose exec web python manage.py migrate

# Access container shell
docker-compose exec web bash
```

## Architecture Overview

### Core Django Structure
- **Main Project**: `sortownia/` - Contains Django settings and root URL configuration
- **Main App**: `sorting/` - Contains all business logic for the sorting facility

### Key Models (sorting/models.py)
- **Socket**: Physical locations where bags are received (e.g., conveyor positions)
- **BagType**: Categories of clothing bags with parameters and routing rules
- **BagSubtype**: Subcategories within bag types (e.g., Grade A, Grade B)
- **SortingPerson**: Personnel who perform sorting operations
- **Bag**: Individual bags being processed through the system
- **SortedBag**: Final processed bags with destination and tracking info

### Multi-Step Bag Processing Workflow
The application implements a 4-step bag entry process using Django sessions:

1. **Step 1**: Socket selection (with optional bag source for SEP socket)
2. **Step 2**: Bag type selection (with parameter choices if applicable)
3. **Step 2b**: Subtype selection (if bag type has subtypes)
4. **Step 3**: Weight and notes entry
5. **Step 4**: Summary and confirmation

Views handle session data persistence between steps and validation.

### Key Features
- **Dashboard**: Overview statistics and system status
- **Socket Management**: Track physical receiving locations with color coding
- **Bag Tracking**: Complete lifecycle from reception to final destination
- **Personnel Management**: Track sorting staff and their performance
- **Settings**: Drag-and-drop ordering for sockets, bag types, and subtypes

### Database
- Uses SQLite for development (`db.sqlite3`)
- Models include proper relationships and validation
- Migrations are in `sorting/migrations/`

### Frontend
- Server-side rendered Django templates
- Custom CSS styling in `sorting/static/sorting/css/styles.css`
- JavaScript for dynamic forms (bag type parameters, drag-and-drop ordering)
- Responsive design for facility floor use

### Deployment
- Dockerized with nginx reverse proxy
- Docker Compose configuration for production deployment
- Static files served by nginx
- Environment-based configuration for different hosts