from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q
from rest_framework import serializers
from core.models import Profile
from rest_framework.authtoken.models import Token

User = get_user_model()


class UserRegistrationSerializer(serializers.Serializer):
    """
    **User Serilizer**
        Serialize Profile model

        **list fields:**

        * username - CharField
        * first_name - CharField
        * last_name - CharField
        * email - EmailField
    """
    first_name = serializers.CharField(max_length=30, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')

    def validate(self, attrs):
        email = attrs.get('email')
        username = attrs.get('username')
        if email and username:
            user_object = User.objects.filter(Q(email=email) | Q(username=username))
            if user_object:
                raise serializers.ValidationError('This user is already registered.')
            else:
                return self.create(attrs)

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        token, created = Token.objects.get_or_create(user=user)
        return {'token': token.key, 'user_email': user.email, 'user_username': user.username, "user_id": user.id,
                'reason': 'Successfully registered', 'success': True}


class UserLoginSerializer(serializers.Serializer):
    """
    **User Serilizer**
        Fields:
        email
        password
    """
    username_email = serializers.CharField()

    def validate(self, attrs):
        username_email = attrs.get('username_email')
        if username_email:
            user = User.objects.filter(Q(username=username_email) | Q(email=username_email))
            if user:
                token, created = Token.objects.get_or_create(user=user[0])
                return {"user_id": token.user_id, "token": token.key, 'success': True,
                        'reason': 'Logged in Successfully'}
            else:
                raise serializers.ValidationError('This is not a registered user.')
        else:
            raise serializers.ValidationError('Need Username or email')


class ProfileSerializer(serializers.ModelSerializer):
    """
    **User Serilizer**
        Serialize Profile model

        **list fields:**
        user - OneToOneField
        location - CharField
        user_title - CharField
        description - TextField
        personal_website - CharField
        twitter_username - CharField
        github_username - CharField
        is_subscribe - BooleanField
        is_developer_story - BooleanField
        profile_pic - ImageField
        developer_story - OneToOneField
    """

    class Meta:
        model = Profile

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
