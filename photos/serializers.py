from rest_framework import serializers
from .models import User, Album, Photo, Tag

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'profile_image', 'bio', 'date_joined')
        read_only_fields = ('id', 'date_joined')

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')

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

class AlbumSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Album
        fields = ('id', 'title', 'description', 'created_at', 'updated_at', 'owner', 'photos')
        read_only_fields = ('id', 'created_at', 'updated_at', 'owner') 