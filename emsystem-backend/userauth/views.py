# from django.shortcuts import render
import json
import jwt

from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from datetime import timedelta, datetime , time
# from datetime import datetime, timedelta, timezone as dt_timezone
from django.utils import timezone
from django.conf import settings
from .jwtutils import create_access_token, jwt_required, JWT_ALGORITHM

from .models import User

#Get Method : home , user_list
def home(request):
    # return HttpResponse( "Hello Parth")
    return JsonResponse({
        'message':'EM System is working!',
        'status' : 'success'
    
    })


@jwt_required
def user_list(request):
    if request.method != 'GET':
        return JsonResponse (
            {'error': 'Method Not allowed!'},
            status=405
        )
        
    #read query parameters
    try:
        page_number = int(request.GET.get("page",1))
        page_size = int(request.GET.get("page_size",10))
    except(TypeError, ValueError):
        return JsonResponse(
            {"error": "page and page_size must be integers"},
            status = 400,
        )
    
    if page_number < 1:
        return JsonResponse(
            {"error":"page must be at least 1"},
            status = 400,
        )
        
    if not 1 <= page_size <= 100 :
        return JsonResponse(
            {"error":"page must be between 1 and 100"},
            status = 400,
        )
            
    queryset = User.objects.order_by("user_id").values(
        'user_id',
        'first_name',
        'last_name',
        'email',
        # 'password',
        'created_at',
        'valid_until'
    )
    
    #Divide the queryset into pages
    paginator = Paginator(queryset, page_size)
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        return JsonResponse(
            {"error": "page number must be an integer"},
            status = 400,
        )
    except EmptyPage:
        return JsonResponse(
            {"error": "Page does not exist"},
            status = 404,
        )
        
    users = list(page_obj.object_list)
    
    for user in users:
        user["created_at"] = user["created_at"].isoformat()
        user["valid_until"] = user["valid_until"].isoformat()
    
    return JsonResponse({
        "status": "success",
        "pagination": {
            "current_page":page_obj.number,
            "page_size":page_size,
            "total_users":paginator.count,
            "total_pages":paginator.num_pages,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
        },
        "users": users,
    },status=200,
    
    )
    
    

#Post method : Register
@csrf_exempt
def register_user(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "Method not allowed"},
            status=405,
        )

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=400,
        )

    if not isinstance(data, dict):
        return JsonResponse(
            {"error": "JSON object required"},
            status=400,
        )

    first_name = data.get("first_name", "").strip()
    last_name = data.get("last_name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not all([first_name, last_name, email, password]):
        return JsonResponse(
            {"error": "All fields are required"},
            status=400,
        )

    if len(first_name) > 30 or len(last_name) > 30:
        return JsonResponse(
            {"error": "Names must not exceed 30 characters"},
            status=400,
        )

    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse(
            {"error": "Enter a valid email address"},
            status=400,
        )

    if User.objects.filter(email__iexact=email).exists():
        return JsonResponse(
            {"error": "Email already registered"},
            status=409,
        )

    if not isinstance(password, str) or not 8 <= len(password) <= 128:
        return JsonResponse(
            {"error": "Password must be between 8 and 128 characters"},
            status=400,
        )

    try:
        with transaction.atomic():
            user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=make_password(password),
                valid_until=timezone.now() + timedelta(
                    days=settings.ACCOUNT_VALIDITY_DAYS
                ),
            )
    except IntegrityError:
        return JsonResponse(
            {"error": "Unable to register user with these details"},
            status=409,
        )

    return JsonResponse(
        {
            "status": "success",
            "message": "User registered successfully",
            "user": {
                "user_id": user.user_id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "created_at": user.created_at.isoformat(),
                "valid_until": user.valid_until.isoformat(),
            },
        },
        status=201,
    )

@csrf_exempt
def login_user(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "Method not allowed"},
            status=405,
        )

    # Read JSON from the request body
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=400,
        )

    if not isinstance(data, dict):
        return JsonResponse(
            {"error": "JSON object required"},
            status=400,
        )

    email = data.get("email")
    password = data.get("password")

    if not isinstance(email, str) or not isinstance(password, str):
        return JsonResponse(
            {"error": "Email and password are required"},
            status=400,
        )

    email = email.strip()

    if not email or not password:
        return JsonResponse(
            {"error": "Email and password are required"},
            status=400,
        )

    # Find the existing user
    user = User.objects.filter(email__iexact=email).first()

    # Verify the password hash
    if user is None or not check_password(password, user.password):
        return JsonResponse(
            {"error": "Invalid email or password"},
            status=401,
        )
        
    if timezone.now() >= user.valid_until:
        return JsonResponse(
            {
                "status": "error",
                "code": "account_expired",
                "error": "Your account has expired. Please reactivate your account.",
            },
            status=403,
    )
    
    access_token = create_access_token(user)
    # Credentials are valid
    return JsonResponse({
        "status": "success",
        "message": "Login successful",
        "token_type":"Bearer",
        "access_token":access_token,
        "expire_in":settings.JWT_ACCESS_TOKEN_MINUTES*60,
        "user": {
            "user_id": user.user_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "created_at":user.created_at.isoformat(),
            "valid_until":user.valid_until.isoformat(),
        },
    }, status=200)



# @csrf_exempt
# def renew_account(request, user_id):
#     if request.method != "POST":
#         return JsonResponse(
#             {"error": "Method not allowed"},
#             status=405,
#         )

#     auth_header = request.headers.get("Authorization", "")
#     parts = auth_header.split()

#     if len(parts) != 2 or parts[0].lower() != "bearer":
#         return JsonResponse(
#             {"error": "Authentication token required"},
#             status=401,
#         )

#     try:
#         payload = jwt.decode(
#             parts[1],
#             settings.JWT_SIGNING_KEY,
#             algorithms=[JWT_ALGORITHM],
#             options={"require": ["user_id", "iat", "exp"]},
#         )
#     except jwt.ExpiredSignatureError:
#         return JsonResponse(
#             {"error": "Access token has expired. Log in again."},
#             status=401,
#         )
#     except jwt.InvalidTokenError:
#         return JsonResponse(
#             {"error": "Invalid access token"},
#             status=401,
#         )

#     try:
#         requester = User.objects.get(
#             user_id=payload["user_id"]
#         )
#     except (User.DoesNotExist, TypeError, ValueError):
#         return JsonResponse(
#             {"error": "User not found"},
#             status=401,
#         )

#     # A user can renew only their own account.
#     if requester.user_id != user_id:
#         return JsonResponse(
#             {
#                 "error": "You can renew only your own account."
#             },
#             status=403,
#         )

#     requester.valid_until = timezone.now() + timedelta(
#         days=settings.ACCOUNT_VALIDITY_DAYS
#     )
#     requester.save(update_fields=["valid_until"])

#     return JsonResponse(
#         {
#             "status": "success",
#             "message": "Your account has been renewed successfully.",
#             "user": {
#                 "user_id": requester.user_id,
#                 "email": requester.email,
#                 "valid_until": requester.valid_until.isoformat(),
#             },
#         },
#         status=200,
#     )
 


# @csrf_exempt
# def reactivate_account(request):
#     if request.method != "POST":
#         return JsonResponse(
#             {"error": "Method not allowed"},
#             status=405,
#         )

#     # Read and validate JSON.
#     try:
#         data = json.loads(request.body)
#     except (json.JSONDecodeError, UnicodeDecodeError):
#         return JsonResponse(
#             {"error": "Invalid JSON"},
#             status=400,
#         )

#     if not isinstance(data, dict):
#         return JsonResponse(
#             {"error": "JSON object required"},
#             status=400,
#         )

#     email = data.get("email")
#     password = data.get("password")

#     if (
#         not isinstance(email, str)
#         or not isinstance(password, str)
#         or not email.strip()
#         or not password
#     ):
#         return JsonResponse(
#             {"error": "Email and password are required"},
#             status=400,
#         )

#     # Find the account using the supplied email.
#     try:
#         user = User.objects.get(email__iexact=email.strip())
#     except User.DoesNotExist:
#         return JsonResponse(
#             {"error": "Invalid email or password"},
#             status=401,
#         )

#     # Verify the password against the stored hash.
#     if not check_password(password, user.password):
#         return JsonResponse(
#             {"error": "Invalid email or password"},
#             status=401,
#         )

#     # A valid account does not need reactivation.
#     if timezone.now() < user.valid_until:
#         return JsonResponse(
#             {
#                 "status": "success",
#                 "code": "account_still_valid",
#                 "message": "Your account is still valid. Please log in normally.",
#                 "valid_until": user.valid_until.isoformat(),
#             },
#             status=200,
#         )

#     # Reactivate only the account authenticated by its credentials.
#     user.valid_until = timezone.now() + timedelta(
#         days=settings.ACCOUNT_VALIDITY_DAYS
#     )
#     user.save(update_fields=["valid_until"])

#     # Issue a fresh access token after successful reactivation.
#     access_token = create_access_token(user)

#     return JsonResponse(
#         {
#             "status": "success",
#             "message": "Account reactivated successfully",
#             "token_type": "Bearer",
#             "access_token": access_token,
#             "expire_in": settings.JWT_ACCESS_TOKEN_MINUTES * 60,
#             "user": {
#                 "user_id": user.user_id,
#                 "first_name": user.first_name,
#                 "last_name": user.last_name,
#                 "email": user.email,
#                 "created_at": user.created_at.isoformat(),
#                 "valid_until": user.valid_until.isoformat(),
#             },
#         },
#         status=200,
#     )



@jwt_required
@csrf_exempt
def update_user(request, user_id):
    if request.method not in ["PUT","PATCH"]:
        return JsonResponse(
            {"error": "Method not allowed"},
            status=405,
        )

    # Find the user to update
    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return JsonResponse(
            {"error": "User not found"},
            status=404,
        )

    # Read JSON body
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=400,
        )

    if not isinstance(data, dict):
        return JsonResponse(
            {"error": "JSON object required"},
            status=400,
        )

    # Only these fields can be updated
    allowed_fields = {"first_name", "last_name", "email"}

    if not data:
        return JsonResponse(
            {"error": "Provide at least one field to update"},
            status=400,
        )

    if set(data.keys()) - allowed_fields:
        return JsonResponse(
            {"error": "Only first_name, last_name, and email can be updated"},
            status=400,
        )

    # PUT requires every editable field
    if request.method == "PUT" and not allowed_fields.issubset(data.keys()):
        return JsonResponse(
            {"error": "PUT requires first_name, last_name, and email"},
            status=400,
        )

    # Validate and apply the supplied fields
    updated_fields = []

    for field in data:
        value = data[field]

        if not isinstance(value, str):
            return JsonResponse(
                {"error": f"{field} must be a string"},
                status=400,
            )

        value = value.strip()

        if not value:
            return JsonResponse(
                {"error": f"{field} cannot be empty"},
                status=400,
            )

        if field in ["first_name", "last_name"] and len(value) > 30:
            return JsonResponse(
                {"error": "Names must not exceed 30 characters"},
                status=400,
            )

        if field == "email":
            try:
                validate_email(value)
            except ValidationError:
                return JsonResponse(
                    {"error": "Enter a valid email address"},
                    status=400,
                )

            if User.objects.filter(
                email__iexact=value
            ).exclude(user_id=user_id).exists():
                return JsonResponse(
                    {"error": "Email already registered"},
                    status=409,
                )

        setattr(user, field, value)
        updated_fields.append(field)

    try:
        user.save(update_fields=updated_fields)
    except IntegrityError:
        return JsonResponse(
            {"error": "Unable to update user with these details"},
            status=409,
        )

    return JsonResponse({
        "status": "success",
        "message": "User updated successfully",
        "user": {
            "user_id": user.user_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "created_at": user.created_at.isoformat(),
        },
    }, status=200)



@jwt_required
@csrf_exempt
def delete_user(request, user_id):
    if request.method != "DELETE":
        return JsonResponse(
            {"error": "Method not allowed"},
            status = 405,
        )
    
    try :
        user = User.objects.get(user_id = user_id)
    except User.DoesNotExist:
        return JsonResponse(
            {"error": "User does not exists"},
            status = 404,
        )
    
    user.delete()
    
    return JsonResponse({
        "status": "success",
        "message": "User deleted successfully",
        "user_id": user_id,
        
    },status= 200,
    )
   
   
@csrf_exempt
@jwt_required
def create_user(request):
    if request.method != "POST":
        return JsonResponse(
            {"error":"Method not allowed"},
            status = 405,
        )
    
    #read and load json request body
    try : 
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"error":"Invalid JSON"},
            status = 400,
        )
    
    if not isinstance(data, dict):
        return JsonResponse({
            "error": "Json object are required"
            },status = 400,
        )

    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    password = data.get("password")
    valid_until = data.get("valid_until")
    
    if not all(  
        isinstance(value ,str )
        for value in [first_name, last_name, email, password, valid_until,]
        ):
        return JsonResponse(
            {"error": "All fields must be String"},
            status  = 400,
        )
         
    first_name = first_name.strip()
    last_name = last_name.strip()
    email = email.strip()
    
    if not all([first_name, last_name, email, password]):
        return JsonResponse(
            {"error":"All fields are required"}, 
            status = 400,
        )
        
    if len(first_name) > 40 or len(last_name) > 40 :
        return JsonResponse(
            {"error":"name must not exceed 40 characters "},
            status = 400,
        )
    
    try: 
        validate_email(email)
    except ValidationError:
        return JsonResponse(
            {"error":"Enter a valid Email address"},
            status = 400,
        )
    
    if not 8 <= len(password) <= 128:
        return JsonResponse(
            {"error":"Password must be between 8 to 128"},
            status = 400,
        )
        
    if User.objects.filter(email__iexact=email).exists():
        return JsonResponse(
            {"error":"Email already registered"},
            status = 409,
        )
        
    try:
        selected_date = datetime.strptime(
            valid_until,
            "%Y-%m-%d",
            ).date()
    except ValueError:
        return JsonResponse(
            {"error": "Enter a valid date in YYYY-MM-DD format"},
            status=400,
        )

    today = timezone.localdate()

    if selected_date < today:
        return JsonResponse(
            {"error": "Validity date cannot be in the past"},
            status=400,
        )

    valid_until_datetime = timezone.make_aware(
        datetime.combine(selected_date, time.max)
    )       

    try:
        user = User.objects.create(
            first_name = first_name,
            last_name = last_name,
            email = email,
            password = make_password(password),
            valid_until=valid_until_datetime,
        )
    except IntegrityError:
        return JsonResponse(
            {"error": "Unable to create user with these details"},
            status =400,
        )
    
    return JsonResponse(
        {
            "status":"success",
            "message":"User created successfully",
            "user":{
                "user_id":user.user_id,
                "first_name":user.first_name,
                "last_name":user.last_name,
                "email":user.email,
                "created_at":user.created_at.isoformat(),
                "valid_until": user.valid_until.isoformat(),
            },
        },status = 201,
    )
    
    

@jwt_required  
@csrf_exempt 
def my_profile(request):
    if request.method != "GET":
        return JsonResponse(
            {"error": "Method not allowed"},
            status = 405,
        )
    
    user = request.authenticated_user
    account_valid = timezone.now() < user.valid_until
    
    return JsonResponse({
        "status":"success",
        "account_valid": account_valid,
        "user":{
            "first_name":user.first_name,
            "last_name":user.last_name,
            "email":user.email,
            "created_at":user.created_at.isoformat(),
            "valid_until":user.valid_until.isoformat(),
        },
    },status = 200)
    

@csrf_exempt
def reset_password(request):
    # This simplified endpoint is for local development only.
    if not getattr(settings, "PASSWORD_RESET_DEMO_ENABLED", False):
        return JsonResponse(
            {"error": "Password reset is unavailable."},
            status=403,
        )

    if request.method != "POST":
        return JsonResponse(
            {"error": "Method not allowed."},
            status=405,
        )

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"error": "Invalid JSON."},
            status=400,
        )

    if not isinstance(data, dict):
        return JsonResponse(
            {"error": "Request body must be a JSON object."},
            status=400,
        )

    email = data.get("email")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    if not all(
        isinstance(value, str) and value.strip()
        for value in (email, new_password, confirm_password)
    ):
        return JsonResponse(
            {"error": "Email and both password fields are required."},
            status=400,
        )

    try:
        validate_email(email.strip())
    except ValidationError:
        return JsonResponse(
            {"error": "Enter a valid email address."},
            status=400,
        )

    if new_password != confirm_password:
        return JsonResponse(
            {"error": "Passwords do not match."},
            status=400,
        )

    if not 8 <= len(new_password) <= 128:
        return JsonResponse(
            {"error": "Password must be between 8 and 128 characters."},
            status=400,
        )

    user = User.objects.filter(
        email__iexact=email.strip()
    ).first()

    if user is None:
        return JsonResponse(
            {"error": "No account found with this email."},
            status=404,
        )

    user.password = make_password(new_password)
    user.save(update_fields=["password"])

    return JsonResponse(
        {"message": "Password reset successful. Please log in."},
        status=200,
    )
