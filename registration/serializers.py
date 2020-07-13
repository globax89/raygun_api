from django.shortcuts import get_object_or_404
from firebase_admin import auth
from rest_framework import serializers
from rest_framework import exceptions as rest_exceptions
from rest_framework_simplejwt.tokens import RefreshToken

from django.utils.translation import ugettext_lazy as _
from django.utils.six import text_type

from registration.models import User, FirebaseUser
from registration.utils import FirebaseUtils


class CreateUserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        new_user = User.objects.create_user(email=validated_data.get('email'),
                                            username=validated_data.get('email'),
                                            password=validated_data.get('password'),
                                            first_name=validated_data.get('first_name'),
                                            last_name=validated_data.get('last_name'),
                                            email_confirmed=True)

        return new_user

    def update(self, instance, validated_data):
        if 'email' in validated_data:
            instance.username = validated_data.get('email')
            instance.email = validated_data.get('email')

        instance.first_name = validated_data.get(
            'first_name') if 'first_name' in validated_data else instance.first_name
        instance.last_name = validated_data.get('last_name') if 'last_name' in validated_data else instance.last_name

        instance.save()

        if 'password' in validated_data:
            instance.set_password(validated_data.get('password'))

        instance.save()

        return instance

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name')
        extra_kwargs = {
            'password': {'write_only': True},
        }


class FirebaseUserSerializer(serializers.Serializer):
    """
        This serializer takes email_id and uid as param.
        Confirms authentication.
        If user or his firebase account does not exist, then will create it
    """
    email = serializers.EmailField()
    uid = serializers.CharField(max_length=100)

    def validate(self, data):
        # print("Hello")
        try:
            user_from_firebase = FirebaseUtils.check_firebase_credentials(email=data['email'], uid=data['uid'])
            data['firebase_user'] = user_from_firebase
        except serializers.ValidationError:
            # remap all validation errors to auth failed error
            raise rest_exceptions.AuthenticationFailed()

        user = User.objects.filter(email=data['email']).first()
        if user:
            # User exists, Go to next step
            data['user'] = user
        else:
            # User does not exist
            # create new user

            user = User.objects.create_user(
                email=data['email'],
                username=data['email'].split('@')[0]
            )

            if user_from_firebase.display_name:
                user.first_name = user_from_firebase.display_name.split(' ')[0],
                user.last_name = user_from_firebase.display_name.split(' ')[1]
                user.save()

            # User has been created. Proceed to next step
            data['user'] = user

        return data

    def create_or_update_firebase_account(self, validated_data):
        user = validated_data['user']
        user_from_firebase = validated_data['firebase_user']

        if hasattr(user, "firebaseuser"):
            # Account already exists for user. Update details
            user.firebaseuser.uid = user_from_firebase.uid
            user.firebaseuser.save()
            fu = user.firebaseuser
        else:
            # create firebase Account for user

            fu = FirebaseUser.objects.create(user=user, uid=user_from_firebase.uid)

            try:
                fu.profile_pic_url = user_from_firebase.photo_url
                fu.save()
            except:
                # profile pic does not exist
                pass

        return fu

    def create(self, validated_data):
        return self.create_or_update_firebase_account(validated_data)

    def update(self, instance, validated_data):
        return self.create_or_update_firebase_account(validated_data)


class FirebaseTokenObtainSerializer(serializers.Serializer):
    email_field = User.EMAIL_FIELD

    def __init__(self, *args, **kwargs):
        super(FirebaseTokenObtainSerializer, self).__init__(*args, **kwargs)

        self.fields[self.email_field] = serializers.CharField()
        self.fields['uid'] = serializers.CharField()
        self.user = None

    def validate(self, attrs):
        email = attrs['email']
        uid = attrs['uid']

        try:
            user = User.objects.filter(email=email).first()

            if user and hasattr(user, 'firebaseuser'):
                if user.firebaseuser.uid == uid:
                    # User credentials validated
                    self.user = user

                else:
                    # uid did not match
                    # This means that either credentials are bad or data on db is not latest firebase data
                    # Contact firebase again and try to get latest details
                    user_from_firebase = FirebaseUtils.check_firebase_credentials(email=user.email, uid=uid)

                    # user validated
                    user.firebaseuser.uid = uid
                    user.firebaseuser.save()
                    self.user = user
            else:
                # User does not exist or his firebase account does not exist
                raise serializers.ValidationError("This user does not exist or firebase account does not exist")

        # catch all validation errors and simply reply with Auth Failed error
        except serializers.ValidationError:

            raise rest_exceptions.AuthenticationFailed()

        return {}

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class FirebaseTokenObtainPairSerializer(FirebaseTokenObtainSerializer):
    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    @classmethod
    def get_token_object(cls, user):
        refresh_token_object = cls.get_token(user)

        obj = {
            "refresh": text_type(refresh_token_object),
            "access": text_type(refresh_token_object.access_token)
        }

        return obj

    def validate(self, attrs):
        data = super(FirebaseTokenObtainPairSerializer, self).validate(attrs)

        token_obj = self.get_token_object(self.user)

        return token_obj
