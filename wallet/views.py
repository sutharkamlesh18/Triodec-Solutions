from django.shortcuts import render
from rest_framework.response import Response
from .models import Account, Transaction
from .serializers import AccountSerializer, TransactionSerializer,LoginSerializer,UserSerializer
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal
from rest_framework import status
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .permissions import IsAdminUser
from rest_framework.exceptions import NotFound
# Create your views here.

class UserRegister(APIView):
    def post(self, request):
        try:
            data = self.request.data

            serialzer = UserSerializer(data = data)
            if not serialzer.is_valid():
                return Response({"status":400, "message" : "Credintial is not matching"})
            serialzer.save()                     

            user = User.objects.get(username= serialzer.data['username'])
            refresh  = RefreshToken.for_user(user)            

            return Response({"status":200, "payload":serialzer.data,"refresh":str(refresh),"access": str(refresh.access_token)})
        except Exception as e:
            print("----->>>>>",e)
            return Response({"status":400,"message":"Invalid Credintial"})


class LoginView(APIView):
    def post(self,request):
        try:
            data = self.request.data
            serializer = LoginSerializer(data=data)

            if serializer.is_valid():
                username  = serializer.data['username']
                password = serializer.data['password'] 
                user  = authenticate(username = username, password= password)
                if user is None:
                    return Response({"status":400,'message':'Invalid Password'})
                refresh  = RefreshToken.for_user(user)
                return Response({'status':200,'refresh':str(refresh),'access':str(refresh.access_token)})

            return Response({'status':400,'message':"Invalid Credintial"})    

        except Exception as e:
            print(">>>>>",e)


class AccountCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            # Associate the user with the account being created
            account_data = {'user': request.user.id}  
            serializer = AccountSerializer(data=request.data, context={'request': request, 'account_data': account_data})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Error:", e)
            return Response({"status": 400, "message": "Failed to create account"}, status=status.HTTP_400_BAD_REQUEST)


class GetWalletBalance(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        qs = Account.objects.filter(user=request.user)

        if not qs.exists():
            raise NotFound("Account not found.")
        serializer = AccountSerializer(qs, many = True)

        return Response({"status": 200, 'payload':serializer.data})



class DepositToWallet(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TransactionSerializer(data=request.data)
        amount = Decimal(request.data.get('amount'))  
        user = request.user
        try:
            account = Account.objects.get(user=user)
        except Account.DoesNotExist:
            return Response({"message": "Account not found"}, status=400)

        if serializer.is_valid():
            account.balance += amount  
            account.save()
            serializer.save(account=account)

            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=400)


class WithdrawFromWallet(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = TransactionSerializer(data=request.data)
        amount = Decimal(request.data.get('amount')) 
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            user = request.user

            try:
                account = Account.objects.get(user=user)
                if account.balance >= amount:
                    account.balance -= amount
                    account.save()
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response({"message": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)
            except Account.DoesNotExist:
                return Response({"message": "Account not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetMiniStatement(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, account_number):
        try:
            transactions = Transaction.objects.filter(account__account_number=account_number).order_by('-timestamp')
            serializer = TransactionSerializer(transactions, many=True)
            return Response({"status": 200, 'payload':serializer.data})
        
        except Account.DoesNotExist:
            return Response({"message": "Account not found"}, status=status.HTTP_404_NOT_FOUND)


class ListAllAccounts(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated,IsAdminUser]
    def get(self, request):
        accounts = Account.objects.all()
        serializer = AccountSerializer(accounts, many=True)
        return Response(serializer.data)


class ListTransactionHistory(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        transactions = Transaction.objects.all().order_by('-timestamp')
        paginator = Paginator(transactions, 10)  

        page = request.query_params.get('page')
        try:
            transactions = paginator.page(page)
        except PageNotAnInteger:
            transactions = paginator.page(1)
        except EmptyPage:
            transactions = paginator.page(paginator.num_pages)

        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
