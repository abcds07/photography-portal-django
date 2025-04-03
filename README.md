# Photo Portal API

A Django REST API for managing photos, albums, and user profiles with tag-based search functionality.

## Features

- User registration and authentication
- Profile management with image upload
- Album creation and management
- Photo upload and management
- Tag-based photo search
- User profile viewing

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/PhotoDjango.git
cd PhotoDjango
```

2. Create and activate virtual environment:
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply migrations:
```bash
python manage.py migrate
```

5. Run the development server:
```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

## API Endpoints

### Authentication
- Register: `POST /api/users/`
- Login: `POST /api/token/`
- Refresh Token: `POST /api/token/refresh/`

### User Management
- View Profile: `GET /api/users/me/`
- Update Profile: `PUT /api/users/update_profile/`
- View Other Users: `GET /api/users/{id}/`

### Album Management
- Create Album: `POST /api/albums/`
- List Albums: `GET /api/albums/`
- Update Album: `PUT /api/albums/{id}/`
- Delete Album: `DELETE /api/albums/{id}/`

### Photo Management
- Upload Photo: `POST /api/photos/`
- List Photos: `GET /api/photos/`
- Update Photo: `PUT /api/photos/{id}/`
- Delete Photo: `DELETE /api/photos/{id}/`
- Search Photos by Tags: `GET /api/photos/search_by_tags/?tags=tag1&tags=tag2`

### Tag Management
- Create Tag: `POST /api/tags/`
- List Tags: `GET /api/tags/`
- Update Tag: `PUT /api/tags/{id}/`
- Delete Tag: `DELETE /api/tags/{id}/`

## Testing with Insomnia

1. Register a new user:
```json
POST http://127.0.0.1:8000/api/users/
Content-Type: application/json

{
    "username": "testuser",
    "password": "testpass123",
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User"
}
```

2. Save the access token from the registration response

3. For all subsequent requests, add the Authorization header:
```
Authorization: Bearer your_access_token
```

4. Create an album:
```json
POST http://127.0.0.1:8000/api/albums/
Content-Type: application/json

{
    "title": "My First Album",
    "description": "This is a test album"
}
```

5. Create a tag:
```json
POST http://127.0.0.1:8000/api/tags/
Content-Type: application/json

{
    "name": "nature"
}
```

6. Upload a photo with tags:
```json
POST http://127.0.0.1:8000/api/photos/
Content-Type: multipart/form-data

{
    "title": "Nature Photo",
    "description": "A beautiful nature photo",
    "album": 1,
    "image": [Select your image file],
    "tag_ids": [1]
}
```

7. Search photos by tag:
```
GET http://127.0.0.1:8000/api/photos/search_by_tags/?tags=nature
```

## Notes

- The access token expires after a certain period. Use the refresh token to get a new access token.
- All authenticated endpoints require the Bearer token in the Authorization header.
- File uploads should use multipart/form-data content type.
- Tag IDs are required when uploading photos with tags.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 