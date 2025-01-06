from django.shortcuts import render

# Create your views here.
from core.firebase_utils import add_user, add_financial_data

# Example usage in a view
def test_firebase_operations(request):
    add_user("user_002", "Jane Smith", "jane@example.com", "hashed_password")
    add_financial_data(
        "financial_002",
        "user_002",
        60000,
        3,
        28,
        "Engineer",
        "Postgraduate",
        60000,
        25000
    )
    return HttpResponse("Data added to Firebase successfully!")
