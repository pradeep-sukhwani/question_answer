from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q
from rest_framework import serializers, status
from core.models import Profile, Question, Answer
from rest_framework.authtoken.models import Token

User = get_user_model()


class UserRegistrationSerializer(serializers.Serializer):
    """
    **User Registeration Serilizer**
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
    **User Login Serilizer**
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
    **Question Serilizer**
        Serialize Question model

        Create/update the question object

        **fields:**
        user - OneToOneField
        title - CharField
        question - TextField
        tag - ManyToManyField
        rating - IntegerField
    """
    title = serializers.CharField(required=True)
    question = serializers.CharField(required=True)
    tag = serializers.CharField(required=False)
    id = serializers.CharField(required=False)
    up_vote = serializers.BooleanField(required=False)
    down_vote = serializers.BooleanField(required=False)
    profile_id = serializers.CharField(required=True)

    class Meta:
        model = Question
        fields = ('title', 'question')

    def validate(self, attrs):
        question_id = attrs.get('id')
        title = attrs.get('title')
        question = attrs.get('question')
        profile_id = attrs.get('profile_id')

        if not profile_id:
            raise serializers.ValidationError("Need Profile")
        else:
            profile = Profile.objects.filter(id=profile_id)
            if not profile:
                raise serializers.ValidationError("Profile id doesn't match")
        if question_id:
            instance = Question.objects.filter(id=question_id)
            if instance:
                return self.update(instance.first(), attrs)
            else:
                raise serializers.ValidationError('This question doesn\'t exist.')
        else:
            if title and question:
                return self.create(attrs)
            else:
                raise serializers.ValidationError('Need Question and title')

    def create(self, validated_data):
        # Let's first remove the tag so that we can add it after creating the question object
        try:
            tags = validated_data.pop('tag')
        except:
            tags = None
        profile_id = validated_data.pop('profile_id')
        question = Question.objects.create(**validated_data)
        profile_instance = Profile.objects.get(id=profile_id)
        question.asked_by = profile_instance
        profile_instance.reputation += 1
        profile_instance.save()
        question.save()
        if tags:
            for item in tags:
                question.tag.add(item)
        return {'reason': 'Successfully added question', 'success': True, 'status': status.HTTP_201_CREATED}

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title')
        instance.question = validated_data.get('question')
        if validated_data.get('up_vote'):
            instance.up_vote += 1
        if validated_data.get('down_vote'):
            instance.down_vote += 1
        instance.save()
        tags = validated_data.get('tag')
        if tags:
            for item in tags:
                try:
                    instance.tag.add(item)
                except:
                    pass
        return {'reason': 'Successfully updated question', 'success': True, 'status': status.HTTP_200_OK}


class ProfileSerializer(serializers.Serializer):
    """
    **User Serilizer**
        Serialize Profile model

        Create/update the profile

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
    title = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    profile_id = serializers.CharField(required=False)
    description = serializers.CharField(required=True)
    personal_website = serializers.CharField(required=False)
    twitter_username = serializers.CharField(required=False)
    github_username = serializers.CharField(required=False)
    user_id = serializers.CharField(required=True)

    class Meta:
        model = Profile
        fields = ('user', 'location', 'user_title', 'description', 'personal_website', 'twitter_username',
                  'github_username',)

    def validate(self, attrs):
        profile_id = attrs.get('profile_id')
        title = attrs.get('title')
        description = attrs.get('description')

        if title and description:
            instance = Profile.objects.filter(id=profile_id)
            if instance:
                return self.update(instance.first(), attrs)
            else:
                return self.create(attrs)
        else:
            raise serializers.ValidationError('Need title and description')

    def create(self, validated_data):
        user = User.objects.get(id=self.initial_data.get('user').id)
        user.first_name = validated_data.pop('first_name')
        user.last_name = validated_data.pop('last_name')
        user.save()
        validated_data.pop('profile_id')
        Profile.objects.create(**validated_data)
        return {'reason': 'Successfully added profile', 'success': True, 'status': status.HTTP_201_CREATED}

    def update(self, instance, validated_data):
        instance.location = validated_data.get('location')
        instance.user_title = validated_data.get('user_title')
        instance.description = validated_data.get('description')
        instance.personal_website = validated_data.get('personal_website')
        instance.github_username = validated_data.get('github_username')
        instance.twitter_username = validated_data.get('twitter_username')
        instance.title = validated_data.get('title')
        instance.save()
        return {'reason': 'Successfully updated profile', 'success': True, 'status': status.HTTP_200_OK}


class AnswerSerializer(serializers.Serializer):
    """
    **Answer Serilizer**
        Serialize Answer model

        It creates the answer object and assign to the relevant question object. Or if the answer is a reply
        to a particular answer then it assigns that answer to the parent answer object
        It updates the answer object - Up vote, down vote, favourite
        With every up vote - it increases the question reputation by 1 point.

        **fields:**
        answer - CharField
        parent - ForeignKey to self
        answer_by - OneToOneField to Profile
        Upvote - IntegerField
        down vote - IntegerField
        accepted_or_not - BooleanField
        favourite - IntegerField
    """
    answer = serializers.CharField(required=True)
    parent = serializers.CharField(required=False)
    accepted_or_not = serializers.BooleanField(required=False)
    favourite = serializers.BooleanField(required=False)
    question_id = serializers.CharField(required=True)
    up_vote = serializers.BooleanField(required=False)
    down_vote = serializers.BooleanField(required=False)
    answer_id = serializers.CharField(required=False)
    profile_id = serializers.CharField(required=True)

    def validate(self, attrs):
        question_id = attrs.get('question_id')
        profile_id = attrs.get('profile_id')
        answer_id = attrs.get('answer_id')
        answer = attrs.get('answer')

        if answer and question_id:
            profile_instance = Profile.objects.filter(id=profile_id)
            question_instance = Question.objects.filter(id=question_id)
            if profile_instance and question_instance:
                if answer_id:
                    answer_instance = Answer.objects.filter(id=answer_id)
                    if answer_instance:
                        return self.update(answer_instance.first(), attrs)
                return self.create(attrs)
            else:
                raise serializers.ValidationError('User Profile/Question does not exist')
        else:
            raise serializers.ValidationError('Need Answer')

    def create(self, validated_data):
        try:
            parent_answer_id = validated_data.pop('parent')
            parent_answer = Answer.objects.get(id=parent_answer_id)
        except:
            parent_answer = None
        profile_instance = Profile.objects.get(id=validated_data.pop('profile_id'))
        question_instance = Question.objects.get(id=validated_data.pop('question_id'))
        answer = Answer.objects.create(**validated_data)
        answer.answer_by = profile_instance
        question_instance.answer.add(answer)
        if parent_answer:
            answer.parent = parent_answer
        answer.save()
        return {'reason': 'Successfully added Answer', 'success': True, 'status': status.HTTP_201_CREATED}

    def update(self, instance, validated_data):
        if validated_data.get('accepted_or_not'):
            instance.accepted_or_not = True
        if validated_data.get('favourite'):
            instance.favourite += 1
        if validated_data.get('up_vote'):
            profile_instance = Profile.objects.get(id=validated_data.get('profile_id'))
            profile_instance.reputation += 1
            profile_instance.save()
            instance.up_vote += 1
        if validated_data.get('down_vote'):
            instance.down_vote += 1
        instance.save()
        return {'reason': 'Successfully updated answer', 'success': True, 'status': status.HTTP_200_OK}
