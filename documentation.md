# Detailed Documentation: Photo Portal API Implementation

## Project Overview

The Photo Portal API is a Django REST API that allows users to manage photos, albums, and profiles with tag-based search functionality. This documentation provides a comprehensive explanation of how each component is implemented and how Django features are utilized.

## Technology Stack

- **Django 4.2.20**: Web framework
- **Django REST Framework 3.16.0**: For building RESTful APIs
- **Django REST Framework SimpleJWT 5.5.0**: For JWT authentication
- **Django CORS Headers 4.7.0**: For handling Cross-Origin Resource Sharing
- **Pillow 11.1.0**: For image processing

## Project Structure

```
PhotoDjango/
├── manage.py                  # Django command-line utility
├── photoportal/              # Project configuration directory
│   ├── __init__.py
│   ├── settings.py           # Project settings
│   ├── urls.py               # Main URL configuration
│   ├── asgi.py               # ASGI configuration
│   └── wsgi.py               # WSGI configuration
├── photos/                   # Main application directory
│   ├── __init__.py
│   ├── admin.py              # Admin interface configuration
│   ├── apps.py               # App configuration
│   ├── models.py             # Database models
│   ├── serializers.py        # DRF serializers
│   ├── urls.py               # App URL configuration
│   └── views.py              # View logic
├── media/                    # User-uploaded files
├── staticfiles/              # Static files
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```

## Models Implementation

### User Model (`photos/models.py`)

```python
class User(AbstractUser):
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.username
```

**Django Features Used:**
- **AbstractUser**: Extends Django's built-in user model to add custom fields
- **ImageField**: Handles image uploads with automatic file storage
- **TextField**: For storing longer text content
- **DateTimeField**: For timestamp tracking

### Album Model

```python
class Album(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='albums')

    def __str__(self):
        return self.title
```

**Django Features Used:**
- **CharField**: For storing short text with a maximum length
- **TextField**: For storing longer text content
- **DateTimeField with auto_now_add**: Automatically sets the creation timestamp
- **DateTimeField with auto_now**: Automatically updates the timestamp on save
- **ForeignKey**: Creates a many-to-one relationship with the User model
- **related_name**: Allows reverse lookup from User to Album

### Tag Model

```python
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
```

**Django Features Used:**
- **CharField with unique=True**: Ensures tag names are unique in the database

### Photo Model

```python
class Photo(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='photos')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photos')
    tags = models.ManyToManyField(Tag, related_name='photos', blank=True)

    def __str__(self):
        return self.title
```

**Django Features Used:**
- **ImageField**: For storing uploaded images
- **ForeignKey**: Creates relationships with Album and User models
- **ManyToManyField**: Creates a many-to-many relationship with Tag model
- **related_name**: Allows reverse lookup from related models

## Serializers Implementation

### UserSerializer (`photos/serializers.py`)

```python
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'profile_image', 'bio', 'date_joined')
        read_only_fields = ('id', 'date_joined')
```

**DRF Features Used:**
- **ModelSerializer**: Automatically creates serializers based on model fields
- **fields**: Specifies which model fields to include in the serializer
- **read_only_fields**: Prevents modification of specified fields

### TagSerializer

```python
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')
```

### PhotoSerializer

```python
class PhotoSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Photo
        fields = ('id', 'title', 'description', 'image', 'uploaded_at', 'album', 'owner', 'tags', 'tag_ids')
        read_only_fields = ('id', 'uploaded_at', 'owner')

    def create(self, validated_data):
        tag_ids = validated_data.pop('tag_ids', [])
        photo = Photo.objects.create(**validated_data)
        if tag_ids:
            tags = Tag.objects.filter(id__in=tag_ids)
            photo.tags.set(tags)
        return photo

    def update(self, instance, validated_data):
        tag_ids = validated_data.pop('tag_ids', None)
        if tag_ids is not None:
            tags = Tag.objects.filter(id__in=tag_ids)
            instance.tags.set(tags)
        return super().update(instance, validated_data)
```

**DRF Features Used:**
- **Nested Serializers**: Embeds related objects (tags, owner) in the response
- **ListField**: For handling lists of values (tag_ids)
- **write_only**: Prevents the field from being included in responses
- **Custom create/update methods**: For handling complex object creation/updates
- **set() method**: For managing many-to-many relationships

### AlbumSerializer

```python
class AlbumSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Album
        fields = ('id', 'title', 'description', 'created_at', 'updated_at', 'owner', 'photos')
        read_only_fields = ('id', 'created_at', 'updated_at', 'owner')
```

**DRF Features Used:**
- **Nested Serializers**: Embeds related photos and owner in the response

## Views Implementation

### UserViewSet (`photos/views.py`)

```python
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return super().get_permissions()

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put'])
    def update_profile(self, request):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

**DRF Features Used:**
- **ModelViewSet**: Provides CRUD operations for the User model
- **permission_classes**: Sets default permissions for all actions
- **get_permissions**: Dynamically changes permissions based on the action
- **create method override**: Customizes user creation to return JWT tokens
- **@action decorator**: Adds custom actions to the viewset
- **partial=True**: Allows partial updates

### AlbumViewSet

```python
class AlbumViewSet(viewsets.ModelViewSet):
    serializer_class = AlbumSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Album.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
```

**DRF Features Used:**
- **get_queryset**: Filters albums to show only those owned by the current user
- **perform_create**: Automatically sets the owner when creating an album

### PhotoViewSet

```python
class PhotoViewSet(viewsets.ModelViewSet):
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Photo.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'])
    def search_by_tags(self, request):
        tags = request.query_params.getlist('tags', [])
        photos = Photo.objects.filter(tags__name__in=tags).distinct()
        serializer = self.get_serializer(photos, many=True)
        return Response(serializer.data)
```

**DRF Features Used:**
- **get_queryset**: Filters photos to show only those owned by the current user
- **perform_create**: Automatically sets the owner when creating a photo
- **@action decorator**: Adds a custom action for searching photos by tags
- **query_params.getlist**: Retrieves multiple values for the same parameter
- **distinct()**: Prevents duplicate results

### TagViewSet

```python
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
```

## URL Configuration

### Main URLs (`photoportal/urls.py`)

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('photos.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

**Django Features Used:**
- **include**: Includes URLs from another module
- **static**: Serves media files during development

### App URLs (`photos/urls.py`)

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserViewSet, AlbumViewSet, PhotoViewSet, TagViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'albums', AlbumViewSet, basename='album')
router.register(r'photos', PhotoViewSet, basename='photo')
router.register(r'tags', TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
```

**DRF Features Used:**
- **DefaultRouter**: Automatically generates URL patterns for viewsets
- **basename**: Specifies the base name for URL patterns
- **TokenObtainPairView**: Provides JWT token generation
- **TokenRefreshView**: Provides JWT token refresh

## Settings Configuration

### Project Settings (`photoportal/settings.py`)

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'photos',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTH_USER_MODEL = 'photos.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

CORS_ALLOW_ALL_ORIGINS = True  # Only for development
```

**Django Features Used:**
- **INSTALLED_APPS**: Lists all installed applications
- **MIDDLEWARE**: Configures request/response processing
- **AUTH_USER_MODEL**: Specifies the custom user model
- **REST_FRAMEWORK**: Configures Django REST Framework settings
- **CORS_ALLOW_ALL_ORIGINS**: Allows cross-origin requests (development only)

## Authentication Flow

1. **User Registration**:
   - User sends a POST request to `/api/users/` with their details
   - The server creates a new user and returns JWT tokens
   - The client stores these tokens for future requests

2. **Authentication**:
   - For all authenticated requests, the client includes the access token in the Authorization header:
     ```
     Authorization: Bearer <access_token>
     ```

3. **Token Refresh**:
   - When the access token expires, the client can get a new one by sending a POST request to `/api/token/refresh/` with the refresh token:
     ```
     {
         "refresh": "<refresh_token>"
     }
     ```

## File Upload Handling

1. **Profile Image Upload**:
   - The `profile_image` field in the User model uses `ImageField`
   - When a user updates their profile with an image, Django automatically handles the file upload

2. **Photo Upload**:
   - The `image` field in the Photo model uses `ImageField`
   - When creating a photo, the client sends a multipart/form-data request with the image file

## Tag-Based Search Implementation

1. **Tag Creation**:
   - Tags are created via the TagViewSet
   - Each tag has a unique name

2. **Associating Tags with Photos**:
   - When creating or updating a photo, the client includes `tag_ids` in the request
   - The PhotoSerializer's `create` and `update` methods handle setting the tags

3. **Searching Photos by Tags**:
   - The `search_by_tags` action in PhotoViewSet filters photos by tag names
   - The client sends a GET request to `/api/photos/search_by_tags/?tags=tag1&tags=tag2`
   - The view returns photos that have any of the specified tags

## Security Features

1. **JWT Authentication**:
   - Uses Django REST Framework SimpleJWT for secure token-based authentication
   - Tokens have an expiration time to limit their validity

2. **Permission Classes**:
   - Most endpoints require authentication
   - User registration is publicly accessible
   - Users can only access their own albums and photos

3. **CORS Configuration**:
   - CORS headers are configured to allow cross-origin requests (development only)
   - In production, this should be restricted to specific origins

## Conclusion

The Photo Portal API demonstrates the power of Django and Django REST Framework for building robust, secure, and feature-rich APIs. It leverages Django's model system for data management, DRF's serializers for data transformation, and JWT for secure authentication. The project follows best practices for API design, including proper separation of concerns, RESTful endpoint design, and secure handling of user data and file uploads.
