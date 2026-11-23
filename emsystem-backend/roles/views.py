
from django.http import JsonResponse
import json

from django.db.models import Count
from django.db import IntegrityError, transaction
from userauth.jwtutils import jwt_required
from .models import Role, Permission, RolePermission
from .permissions import has_permission
from django.views.decorators.csrf import csrf_exempt

@jwt_required
def permission_list(request):

    if request.method != "GET":
        return JsonResponse(
            {"error": "Method not allowed"},
            status=405,
        )

    permissions = list(
        Permission.objects.all()
        .order_by("permission_id")
        .values(
            "permission_id",
            "permission_name",
            "codename",
            "description",
        )
    )

    return JsonResponse(
        {
            "status": "success",
            "total_permissions": len(permissions),
            "permissions": permissions,
        },
        status=200,
    )

@jwt_required
def role_list(request):
    if request.method != "GET":
        return JsonResponse(
            {"error": "Method not allowed"},
            status=405
        )

    user = request.authenticated_user

    if not (has_permission(user, "roles.read")
        or has_permission(user, "users.create")
        or has_permission(user, "users.update")
    ):
        return JsonResponse(
            {
                "status": "error",
                "message": "You do not have permission to view roles."
            },
            status=403
        )

    roles = list(
        Role.objects
        .annotate(total_users=Count("users",distinct=True))
        .order_by("role_id")
        .values(
            "role_id",
            "role_name",
            "description",
            "created_at",
            "updated_at",
            "total_users"
        )
    )

    return JsonResponse(
        {
            "status": "success",
            "total_roles": len(roles),
            "roles": roles,
        },
        status=200
    )


@jwt_required
def role_create(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "Method not allowed"},
            status=405
        )

    user = request.authenticated_user

    # Check role creation permission.
    if not has_permission(user, "roles.create"):
        return JsonResponse(
            {
                "status": "error",
                "message": "You do not have permission to create roles."
            },
            status=403
        )

    # Parse JSON request.
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"error": "Invalid JSON request body."},
            status=400
        )

    if not isinstance(data, dict):
        return JsonResponse(
            {"error": "Request body must be a JSON object."},
            status=400
        )

    role_name = data.get("role_name")
    description = data.get("description", "")
    permissions = data.get("permissions", [])

    # Validate role name.
    if not isinstance(role_name, str) or not role_name.strip():
        return JsonResponse(
            {"error": "Role name is required."},
            status=400
        )

    role_name = role_name.strip()

    if len(role_name) > 100:
        return JsonResponse(
            {"error": "Role name cannot exceed 100 characters."},
            status=400
        )

    # Check duplicate role name (case-insensitive).
    if Role.objects.filter(role_name__iexact=role_name).exists():
        return JsonResponse(
            {"error": "A role with this name already exists."},
            status=409
        )

    # Validate description.
    if not isinstance(description, str):
        return JsonResponse(
            {"error": "Description must be a string."},
            status=400
        )

    # Validate permissions.
    if not isinstance(permissions, list):
        return JsonResponse(
            {"error": "Permissions must be a list."},
            status=400
        )

    if any(
        not isinstance(code, str) or not code.strip()
        for code in permissions
    ):
        return JsonResponse(
            {"error": "Every permission must be a non-empty string."},
            status=400
        )

    permissions = [code.strip() for code in permissions]

    if len(permissions) != len(set(permissions)):
        return JsonResponse(
            {"error": "Duplicate permissions are not allowed."},
            status=400
        )

    # Retrieve predefined permissions.
    permission_objects = list(
        Permission.objects.filter(codename__in=permissions)
    )

    if len(permission_objects) != len(permissions):
        return JsonResponse(
            {"error": "One or more permissions are invalid."},
            status=400
        )

    # Prevent privilege escalation.
    # A user can only assign permissions they personally possess.
    unauthorized_permissions = [
        permission.codename
        for permission in permission_objects
        if not has_permission(user, permission.codename)
    ]

    if unauthorized_permissions:
        return JsonResponse(
            {
                "status": "error",
                "message": "You cannot assign permissions you do not possess.",
                "unauthorized_permissions": unauthorized_permissions
            },
            status=403
        )

    # Create role and assign permissions atomically.
    try:
        with transaction.atomic():

            role = Role.objects.create(
                role_name=role_name,
                description=description
            )

            RolePermission.objects.bulk_create([
                RolePermission(
                    role=role,
                    permission=permission
                )
                for permission in permission_objects
            ])

    except IntegrityError:
        return JsonResponse(
            {"error": "A role with this name already exists."},
            status=409
        )

    return JsonResponse(
        {
            "status": "success",
            "message": "Role created successfully.",
            "role": {
                "role_id": role.role_id,
                "role_name": role.role_name,
                "description": role.description,
                "permissions": [
                    permission.codename
                    for permission in permission_objects
                ]
            }
        },
        status=201
    )

@csrf_exempt
@jwt_required
def roles_api(request):
    if request.method == "GET":
        return role_list.__wrapped__(request)

    if request.method == "POST":
        return role_create.__wrapped__(request)

    return JsonResponse(
        {"error": "Method not allowed"},
        status=405
    )
    


@jwt_required
def role_detail(request, role_id):
    if request.method != "GET":
        return JsonResponse(
            {"error": "Method not allowed"},
            status=405
        )

    user = request.authenticated_user

    # Check permission.
    if not has_permission(user, "roles.read"):
        return JsonResponse(
            {
                "status": "error",
                "message": "You do not have permission to view roles."
            },
            status=403
        )

    try:
        role = Role.objects.get(role_id=role_id)
    except Role.DoesNotExist:
        return JsonResponse(
            {"error": "Role not found."},
            status=404
        )

    # Retrieve assigned permission codenames.
    permissions = list(
        RolePermission.objects.filter(role=role)
        .select_related("permission")
        .values_list("permission__codename", flat=True)
    )

    # Retrieve users assigned to this role.
    assigned_users = list(
        role.users.order_by("user_id").values(
            "user_id",
            "first_name",
            "last_name",
            "email"
        )
    )

    return JsonResponse(
        {
            "status": "success",
            "role": {
                "role_id": role.role_id,
                "role_name": role.role_name,
                "description": role.description,
                "created_at": role.created_at,
                "updated_at": role.updated_at,
                "permissions": permissions,
                "total_users": len(assigned_users),
                "assigned_users": assigned_users
            }
        },
        status=200
    )


@csrf_exempt
@jwt_required
def role_update(request, role_id):
    """
    Update an existing role and its assigned permissions.

    PUT: Replace all role information.
    PATCH: Update only the supplied fields.
    """

    # 1. Allow only PUT and PATCH
    if request.method not in ["PUT", "PATCH"]:
        return JsonResponse(
            {"error": "Method not allowed."},
            status=405
        )

    user = request.authenticated_user

    # 2. Check role update permission
    if not has_permission(user, "roles.update"):
        return JsonResponse(
            {
                "status": "error",
                "message": "You do not have permission to update roles."
            },
            status=403
        )

    # 3. Find the role
    try:
        role = Role.objects.get(role_id=role_id)
    except Role.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "Role not found."},
            status=404
        )

    # 4. Parse JSON request body
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"error": "Invalid JSON request body."},
            status=400
        )

    if not isinstance(data, dict):
        return JsonResponse(
            {"error": "Request body must be a JSON object."},
            status=400
        )

    # 5. Validate fields
    allowed_fields = {"role_name", "description", "permissions"}

    if not data:
        return JsonResponse(
            {"error": "Request body cannot be empty."},
            status=400
        )

    if set(data.keys()) - allowed_fields:
        return JsonResponse(
            {"error": "One or more fields are not allowed."},
            status=400
        )

    # PUT requires all fields
    if request.method == "PUT":
        missing_fields = allowed_fields - set(data.keys())

        if missing_fields:
            return JsonResponse(
                {
                    "error": "PUT requires all fields.",
                    "missing_fields": sorted(missing_fields)
                },
                status=400
            )

    # 6. Prepare updated values
    role_name = data.get("role_name", role.role_name)
    description = data.get("description", role.description)

    if not isinstance(role_name, str) or not role_name.strip():
        return JsonResponse(
            {"error": "Role name is required."},
            status=400
        )

    role_name = role_name.strip()

    if len(role_name) > 100:
        return JsonResponse(
            {"error": "Role name cannot exceed 100 characters."},
            status=400
        )

    if not isinstance(description, str):
        return JsonResponse(
            {"error": "Description must be a string."},
            status=400
        )

    # 7. Check duplicate role name
    duplicate_role = Role.objects.filter(
        role_name__iexact=role_name
    ).exclude(role_id=role_id).exists()

    if duplicate_role:
        return JsonResponse(
            {"error": "A role with this name already exists."},
            status=409
        )

    # 8. Validate permissions if supplied
    permission_objects = None

    if "permissions" in data:
        permission_codes = data["permissions"]

        if not isinstance(permission_codes, list):
            return JsonResponse(
                {"error": "Permissions must be a list."},
                status=400
            )

        if any(
            not isinstance(code, str) or not code.strip()
            for code in permission_codes
        ):
            return JsonResponse(
                {"error": "Each permission must be a valid codename string."},
                status=400
            )

        permission_codes = [
            code.strip() for code in permission_codes
        ]

        if len(permission_codes) != len(set(permission_codes)):
            return JsonResponse(
                {"error": "Duplicate permissions are not allowed."},
                status=400
            )

        permission_objects = list(
            Permission.objects.filter(
                codename__in=permission_codes
            )
        )

        found_codes = {
            permission.codename
            for permission in permission_objects
        }

        unknown_codes = set(permission_codes) - found_codes

        if unknown_codes:
            return JsonResponse(
                {
                    "error": "One or more permissions are invalid.",
                    "invalid_permissions": sorted(unknown_codes)
                },
                status=400
            )

        # 9. Prevent privilege escalation
        user_permissions = set(
            RolePermission.objects.filter(
                role_id=user.role_id
            ).values_list(
                "permission__codename",
                flat=True
            )
        )

        unauthorized_permissions = (
            set(permission_codes) - user_permissions
        )

        if unauthorized_permissions:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "You cannot assign permissions you do not possess.",
                    "unauthorized_permissions": sorted(
                        unauthorized_permissions
                    )
                },
                status=403
            )

    # 10. Update role and permissions atomically
    try:
        with transaction.atomic():

            role.role_name = role_name
            role.description = description

            role.save(
                update_fields=[
                    "role_name",
                    "description",
                    "updated_at"
                ]
            )

            # Replace permissions only when supplied
            if permission_objects is not None:

                RolePermission.objects.filter(
                    role=role
                ).delete()

                RolePermission.objects.bulk_create([
                    RolePermission(
                        role=role,
                        permission=permission
                    )
                    for permission in permission_objects
                ])

    except IntegrityError:
        return JsonResponse(
            {"error": "Unable to update role due to a database conflict."},
            status=409
        )

    # 11. Get updated permissions
    updated_permissions = list(
        RolePermission.objects.filter(
            role=role
        ).values_list(
            "permission__codename",
            flat=True
        )
    )

    return JsonResponse(
        {
            "status": "success",
            "message": "Role updated successfully.",
            "role": {
                "role_id": role.role_id,
                "role_name": role.role_name,
                "description": role.description,
                "permissions": updated_permissions
            }
        },
        status=200
    )



@csrf_exempt
@jwt_required
def role_delete(request, role_id):
    """
    Delete a role that is not assigned to any users.
    """

    # 1. Allow only DELETE
    if request.method != "DELETE":
        return JsonResponse(
            {"error": "Method not allowed."},
            status=405
        )

    user = request.authenticated_user

    # 2. Check permission
    if not has_permission(user, "roles.delete"):
        return JsonResponse(
            {
                "status": "error",
                "message": "You do not have permission to delete roles."
            },
            status=403
        )

    # 3. Find the role
    try:
        role = Role.objects.get(role_id=role_id)
    except Role.DoesNotExist:
        return JsonResponse(
            {
                "status": "error",
                "message": "Role not found."
            },
            status=404
        )

    # 4. Prevent deletion if users are assigned to this role
    assigned_users_count = role.users.count()

    if assigned_users_count > 0:
        return JsonResponse(
            {
                "status": "error",
                "message": (
                    "This role cannot be deleted because users are assigned to it. "
                    "Reassign those users before deleting the role."
                ),
                "assigned_users": assigned_users_count
            },
            status=409
        )

    # 5. Delete the role
    try:
        with transaction.atomic():
            role.delete()

    except IntegrityError:
        return JsonResponse(
            {
                "status": "error",
                "message": "Unable to delete this role because it is referenced by other records."
            },
            status=409
        )

    return JsonResponse(
        {
            "status": "success",
            "message": "Role deleted successfully.",
            "deleted_role": {
                "role_id": role_id,
                "role_name": role.role_name
            }
        },
        status=200
    )


@csrf_exempt
@jwt_required
def role_detail_api(request, role_id):
    """
    Dispatch GET requests to role_detail()
    and DELETE requests to role_delete().
    """

    if request.method == "GET":
        return role_detail.__wrapped__(request, role_id)

    if request.method == "DELETE":
        return role_delete.__wrapped__(request, role_id)

    return JsonResponse(
        {"error": "Method not allowed."},
        status=405
    )

