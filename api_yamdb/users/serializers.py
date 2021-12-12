import uuid

from django.core.mail import send_mail
from rest_framework import serializers, validators

from users.models import User
from api_yamdb.settings import ADMIN_EMAIL


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[
            validators.UniqueValidator(queryset=User.objects.all())
        ]
    )

    class Meta:
        fields = ('username', 'email')
        model = User

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" в качестве username запрещено.'
            )
        return value

    def create(self, validated_data):
        email = validated_data['email']
        confirmation_code = str(uuid.uuid4())
        send_mail('Код', confirmation_code, ADMIN_EMAIL, [email])
        validated_data['confirmation_code'] = confirmation_code
        return User.objects.create(**validated_data)


class TokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    confirmation_code = serializers.CharField(write_only=True)

    class Meta:
        fields = ('username', 'confirmation_code')
        model = User

    def validate_confirmation_code(self, value):
        confirmation_code = getattr(self.instance, 'confirmation_code', None)
        if value != confirmation_code:
            raise serializers.ValidationError('Неверный код подтверждения!')
        return value


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[validators.UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        model = User

    def get_fields(self):
        fields = super().get_fields()
        if self.context['view'].action == 'me':
            fields['role'].read_only = True
        return fields
