from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework.serializers import ValidationError

from apps.accounts.models import ShopUser, Addresses, VendorProfile

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Addresses
        fields = ['street', 'city', 'state', 'country', 'zip_code', 'is_default']

    def create(self, validated_data):
        user = self.context['request'].user
        return Addresses.objects.create(user=user, **validated_data)


class UserRegistrationSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = ShopUser
        fields = ('first_name', 'last_name', 'username', 'phone', 'email', 'password', 'profile_picture')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_phone(self, value):

        if not value.isdigit():
            raise ValidationError({'detail': 'Phone number must be entered in numbers'})

        if len(value) != 11:
            raise ValidationError({'detail': 'Phone number must be 11 digits'})

        return value

    def create(self, validated_data):
        password = self.validated_data.pop('password')
        profile_picture = validated_data.pop('profile_picture', None)
        user = ShopUser(**validated_data)
        user.set_password(password)

        if profile_picture:
            user.profile_picture = profile_picture

        user.save()
        return user


class VendorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProfile
        fields = '__all__'
        read_only_fields = ['user', 'status', 'is_active']

    def validate(self, data):
        user = self.context['request'].user

        if hasattr(user, 'vendor_profile'):
            raise ValidationError({'detail': 'You have already requested a vendor profile'})

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        return VendorProfile.objects.create(user=user, **validated_data)


class ShopUserDetailSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True)
    vendor_profile = VendorProfileSerializer()

    class Meta:
        model = ShopUser
        fields = ('id','first_name', 'last_name', 'username', 'email' ,'role','is_active','is_superuser', 'is_staff' ,'date_joined','addresses', 'vendor_profile')


class ShopUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopUser
        fields = ('id', 'first_name')


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise ValidationError({'detail': 'Old password is incorrect'})
        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise ValidationError({'detail': 'Passwords do not match'})
        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise ValidationError({'detail': 'Passwords do not match'})
        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance