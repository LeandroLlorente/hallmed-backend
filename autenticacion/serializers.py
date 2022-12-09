from rest_framework import serializers
from autenticacion.roles import ROLES
from rest_framework import serializers
from rest_framework import exceptions
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils.timezone import get_current_timezone
import json
#from json_field.fields import JSONEncoder, JSONDecoder


class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""
    def to_internal_value(self, data):
        return data
    def to_representation(self, value):
        return value

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    first = serializers.SerializerMethodField()
    last = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    def get_first(self, obj):
        return obj.first_name

    def get_last(self, obj):
        return obj.last_name

    def get_user(self, obj):
        return obj.username

    def get_role(self, obj):
        groups = obj.groups.all()
        if groups:
            role = groups[0].name
        else:
            role = "UNAUTHORIZED_USER"
        return role
    
    class Meta:
        model = User
        fields = ('user',
                  'first',
                  'last',
                  'role',
                  )


class UserAllSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    business = serializers.SerializerMethodField()
    project_role = serializers.SerializerMethodField()
    first = serializers.SerializerMethodField()
    last = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    def get_first(self, obj):
        return obj.first_name

    def get_last(self, obj):
        return obj.last_name

    def get_user(self, obj):
        return obj.username

    def get_role(self,obj):
        groups = obj.groups.all()
        if groups:
            role = groups[0].name
        else:
            role = "UNAUTHORIZED_USER"
        return role

    def get_business(self, obj):
        try:
            # autenticacion = UserBusiness.objects.filter(user_id=obj.id)[0].autenticacion
            business = obj.userbusiness.business.name
            return '{}'.format(business)
        except Exception as e:
            return ''

    def get_project_role(self, obj):
        types_serializer = UserProjectSerializer(obj.userproject_set, many=True)
        return types_serializer.data

    class Meta:
        model = User
        fields = ('user',
                  # 'password',
                  'first',
                  'last',
                  'email',
                  'is_active',
                  'role',
                  'autenticacion',
                  'project_role'
                  # 'userproject_set'

                  )


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    attrs["user"] = user
                else:
                    msg = "User is deactivated"
                    raise exceptions.ValidationError(msg)
            else:
                msg = "Unable to login with given credentials"
                raise exceptions.ValidationError(msg)
        else:
            msg = "You most provide a username and password"
            raise exceptions.ValidationError(msg)

        return attrs



class RegisterSerializer(serializers.Serializer):
    first = serializers.CharField()
    last = serializers.CharField()
    username = serializers.CharField()
    password = serializers.CharField()
    email = serializers.CharField()
    admin = serializers.BooleanField(default=False)
    role = serializers.CharField(allow_blank=True)

    def validate(self, attrs):
        email = attrs.get("email")
        username = attrs.get("username")
        first = attrs.get("first")
        last = attrs.get("last")
        password = attrs.get("password")
        is_admin = attrs.get("admin")
        role = attrs.get("role")

        if username and \
                password and \
                first and \
                last and \
                email and \
                role:
            username_query_set = User.objects.filter(username=username)
            email_query_set = User.objects.filter(email=email)
            if not username_query_set and not email_query_set:
                if is_admin is True:
                    s_user = User.objects.create_superuser(username=username, email=email, password=password,
                                                           first_name=first, last_name=last)
                    attrs['user'] = s_user
                    ROLES.set_role(s_user, "APP_ADMINISTRATOR")
                else:
                    if role == "APP_ADMINISTRATOR":
                        msg = "APP_ADMINISTRATOR is not valid for non admin users"
                        raise exceptions.ValidationError(msg)
                    s_user = User.objects.create_user(username=username, email=email, password=password,
                                                      first_name=first, last_name=last)
                    attrs['user'] = s_user
                    ROLES.set_role(s_user, role)
                obj = UserBusiness()
                business = Business.objects.get(pk=int(attrs.get("autenticacion")))
                obj.user = s_user
                obj.business = business
                obj.save()
                attrs['autenticacion'] = business.name
            else:
                msg = "The email and username fields have to be uniques"
                raise exceptions.ValidationError(msg)

        else:
            msg = "You most provide a valid user information"
            raise exceptions.ValidationError(msg)
        return attrs


class DeleteSerializer(serializers.Serializer):
    username = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get("username")
        user = User.objects.get(username=username)
        if not user:
            msg = 'The given username do not belongs to any user'
            raise exceptions.ValidationError(msg)
        else:
            attrs['user'] = user
        return attrs





