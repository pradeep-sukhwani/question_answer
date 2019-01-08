from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q
from rest_framework import serializers
from core.models import Profile, Question
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


class QuestionSerializer(serializers.Serializer):
    """
    **User Serilizer**
        Serialize Question model

        **fields:**
        user - OneToOneField
        title - CharField
        question - TextField
        tag - ManyToManyField
        rating - IntegerField
    """
    title = serializers.CharField(required=True)
    question = serializers.CharField(required=True)
    tag = serializers.CharField()
    id = serializers.CharField()
    rating = serializers.IntegerField()

    class Meta:
        model = Question
        fields = ('id', 'title', 'question', 'tag', 'rating',)

    def validate(self, attrs):
        question_id = attrs.get('id')
        title = attrs.get('title')
        question = attrs.get('question')

        if question_id:
            instance = Question.objects.filter(id=question_id)
            if instance:
                self.update(instance, attrs)
            else:
                serializers.ValidationError('This question doesn\'t exist.')
        else:
            if title and question:
                return self.create(attrs)
            else:
                serializers.ValidationError('Need Question and title')

    def create(self, validated_data):
        # Let's first remove the tag so that we can add it after creating the question object
        try:
            tags = validated_data.pop('tag')
        except:
            tags = None
        question = Question.objects.create(**validated_data)
        if tags:
            for item in tags:
                question.tag.add(item)
        return {'reason': 'Successfully added question', 'success': True}

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title')
        instance.question = validated_data.get('question')
        if validated_data.get('rating'):
            instance.rating += 1
        instance.save()
        tags = validated_data.get('tag')
        for item in tags:
            instance.tag.add(item)
        return {'reason': 'Successfully updated question', 'success': True}


class ProfileSerializer(serializers.ModelSerializer):
    """
    **User Serilizer**
        Serialize Profile model

        **fields:**
        user - OneToOneField
        location - CharField
        user_title - CharField
        description - TextField
        personal_website - CharField
        twitter_username - CharField
        github_username - CharField
    """
    location = serializers.CharField()
    user_title = serializers.CharField(required=True)
    id = serializers.CharField()
    description = serializers.CharField(required=True)
    personal_website = serializers.CharField()
    twitter_username = serializers.CharField()
    github_username = serializers.CharField()
    user = serializers.PrimaryKeyRelatedField(required=True)

    class Meta:
        model = Profile
        fields = ('user', 'location', 'user_title', 'description', 'personal_website', 'twitter_username',
                  'github_username',)

    def validate(self, attrs):
        profile_id = attrs.get('id')
        user_title = attrs.get('user_title')
        description = attrs.get('description')

        if user_title and description:
            instance = Profile.objects.filter(id=profile_id)
            if instance:
                self.update(instance, attrs)
            else:
                self.create(attrs)
        else:
            serializers.ValidationError('Need title and description')

    def create(self, validated_data):
        Profile.objects.create(**validated_data)
        return {'reason': 'Successfully added profile', 'success': True}

    def update(self, instance, validated_data):
        instance.location = validated_data.get('location')
        instance.user_title = validated_data.get('user_title')
        instance.description = validated_data.get('description')
        instance.personal_website = validated_data.get('personal_website')
        instance.github_username = validated_data.get('github_username')
        instance.twitter_username = validated_data.get('twitter_username')
        instance.title = validated_data.get('title')
        instance.save()
        return {'reason': 'Successfully updated profile', 'success': True}
