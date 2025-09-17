# BSort - Clothing Sorting Facility Management System

A Django-based web application for managing clothing sorting operations in textile recycling and distribution facilities.

## Features

- **Multi-Step Bag Processing Workflow** - Guided 4-step process for bag entry and categorization
- **Socket Management** - Track physical receiving locations with color-coded identification
- **Bag Lifecycle Tracking** - Complete monitoring from reception to final destination
- **Personnel Management** - Track sorting staff and performance metrics
- **Dashboard & Analytics** - Real-time overview of facility operations
- **Flexible Categorization** - Hierarchical bag types with customizable subtypes and parameters
- **Responsive Interface** - Optimized for floor-level facility use

## Screenshots

*Dashboard showing facility overview and statistics*

*Multi-step bag entry workflow interface*

## Quick Start

### Prerequisites

- Python 3.8+
- pip
- Docker (optional, for containerized deployment)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd BSort
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

4. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

5. **Populate test data** (optional)
   ```bash
   python manage.py populate_data
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main interface: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Run migrations in container**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. **Create superuser in container**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

The application will be available at http://localhost

## System Architecture

### Core Models

- **Socket** - Physical receiving locations (conveyor positions, input stations)
- **BagType** - Categories of clothing bags with routing parameters
- **BagSubtype** - Subcategories within bag types (Grade A, B, C)
- **Bag** - Individual bags being processed through the system
- **SortedBag** - Final processed bags with destination tracking
- **SortingPerson** - Personnel performing sorting operations

### Workflow Process

1. **Reception** - Bags arrive at designated sockets
2. **Categorization** - Multi-step classification process
3. **Quality Assessment** - Grading and parameter selection
4. **Weight & Documentation** - Physical measurements and notes
5. **Routing** - Assignment to final destination

### Key Features

- **Session-based Multi-step Forms** - Maintains state across bag entry steps
- **Dynamic Parameter Selection** - Conditional form fields based on bag type
- **Color-coded Organization** - Visual identification for sockets and categories
- **Drag-and-drop Administration** - Easy reordering of system elements
- **Real-time Statistics** - Dashboard metrics and facility overview

## Configuration

### Environment Variables

For production deployment, configure the following in `sortownia/settings.py`:

- `SECRET_KEY` - Django secret key (change from default)
- `DEBUG` - Set to `False` for production
- `ALLOWED_HOSTS` - Configure allowed hostnames
- Database settings (if not using SQLite)

### Docker Configuration

The `docker-compose.yml` includes:
- Django web application container
- Nginx reverse proxy
- Static file serving
- Network isolation

## Usage

### Admin Interface

Access the Django admin at `/admin` to configure:
- Sockets and their physical locations
- Bag types and classification parameters
- Personnel and access permissions
- System settings and ordering

### Main Workflow

1. **Socket Selection** - Choose receiving location
2. **Bag Type Selection** - Select category and parameters
3. **Subtype Selection** - Choose specific grade/variant (if applicable)
4. **Weight Entry** - Record measurements and notes
5. **Summary** - Review and confirm bag entry

### Reporting & Analytics

- Dashboard provides real-time facility statistics
- Filter bags by status, type, and processing date
- Track personnel performance metrics
- Monitor socket utilization

## Development

### Project Structure

```
BSort/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Container configuration
├── Dockerfile               # Docker build instructions
├── sortownia/               # Django project settings
│   ├── settings.py          # Main configuration
│   ├── urls.py              # Root URL routing
│   └── wsgi.py              # WSGI configuration
├── sorting/                 # Main application
│   ├── models.py            # Database models
│   ├── views.py             # Business logic
│   ├── urls.py              # URL routing
│   ├── forms.py             # Form definitions
│   ├── admin.py             # Admin interface
│   ├── templates/           # HTML templates
│   ├── static/              # CSS, JS, images
│   └── migrations/          # Database migrations
└── staticfiles/             # Collected static files
```

### Running Tests

```bash
python manage.py test
```

### Database Management

```bash
# Create new migration after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Access database shell
python manage.py dbshell
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions, issues, or feature requests, please open an issue on GitHub.

## Acknowledgments

Built with Django framework and designed for textile recycling and distribution facility operations.