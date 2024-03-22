from django.urls import path
from .views import GetWalletBalance,DepositToWallet,LoginView,AccountCreateAPIView, UserRegister, WithdrawFromWallet,GetMiniStatement,ListAllAccounts, ListTransactionHistory


urlpatterns = [
    path('create/account/', AccountCreateAPIView.as_view(), name='account_create'),
    path('wallet/balance/', GetWalletBalance.as_view(), name='get_wallet_balance'),
    path('login/', LoginView.as_view(),name='login'),
    path('user-register/', UserRegister.as_view(), name='user_register'),
    path('deposit/', DepositToWallet.as_view(), name='deposit'),
    path('withdraw/', WithdrawFromWallet.as_view(),name='withdraw'),
    path('wallet/statement/<str:account_number>/', GetMiniStatement.as_view(), name='get_mini_statement'),
    path('accounts/', ListAllAccounts.as_view(), name='list_all_accounts'),
    path('transactions/', ListTransactionHistory.as_view(), name='list_transaction_history')
]


