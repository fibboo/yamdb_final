from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from posts.models import Post, Group, Tag, TagPost


class TagSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = ('name',)


class PostSerializer(ModelSerializer):
    group = serializers.SlugRelatedField(
        queryset=Group.objects.all(),
        required=False,
        slug_field='slug'
    )
    tags = TagSerializer(many=True, required=False)
    character_quantity = serializers.SerializerMethodField()
    publication_date = serializers.DateTimeField(
        source='pub_date', read_only=True
    )

    class Meta:
        model = Post
        fields = (
            'id', 'text', 'author', 'image', 'publication_date', 'group',
            'tags', 'character_quantity'
        )

    def get_character_quantity(self, obj):
        return len(obj.text)

    def create(self, validated_data):
        if 'tags' not in self.initial_data:
            return Post.objects.create(**validated_data)
        else:
            tags = validated_data.pop('tags')
            post = Post.objects.create(**validated_data)

            for tag in tags:
                current_tag, status = Tag.objects.get_or_create(**tag)
                TagPost.objects.create(tag=current_tag, post=post)
            return post
