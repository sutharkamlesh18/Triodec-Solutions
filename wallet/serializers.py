from rest_framework import serializers
from .models import Account, Transaction
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['username','password']

    def create(self, validated_data):
        print(validated_data)
        user = User.objects.create(username = validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class AccountSerializer(serializers.ModelSerializer):
    # user = UserSerialzer()
    class Meta:
        model = Account
        fields = ['account_number', 'balance']

    def create(self, validated_data):
        user = self.context['request'].user
        account = Account.objects.create(user=user, **validated_data)
        return account

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['account', 'amount', 'timestamp']



