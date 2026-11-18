
import json
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.hashers import make_password

from userauth.jwtutils import jwt_required, create_access_token
from userauth.models import User

from .models import Role, Permission, RolePermission
from .permissions import has_permission


class HasPermissionTests(TestCase):

    def setUp(self):
        # Create a test user without a role.
        self.user = User.objects.create(
            first_name="Test",
            last_name="Employee",
            email="employee@example.com",
            password=make_password("TestPass123!"),
            valid_until=timezone.now() + timedelta(days=100),
        )

        # Create a role.
        self.role = Role.objects.create(
            role_name="Test Employee",
            description="Role for permission utility testing.",
        )

        # Create a predefined permission.
        self.permission, created = Permission.objects.get_or_create(
            codename="users.read",
            defaults={
                "permission_name": "View Users",
                "description": "Allows viewing users.",
            }
        )

    def test_returns_false_when_user_is_none(self):
        result = has_permission(None, "users.read")

        self.assertFalse(result)

    def test_returns_false_when_user_has_no_role(self):
        result = has_permission(self.user, "users.read")

        self.assertFalse(result)

    def test_returns_true_when_user_has_permission(self):
        # Assign permission to role.
        RolePermission.objects.create(
            role=self.role,
            permission=self.permission,
        )

        # Assign role to user.
        self.user.role = self.role
        self.user.save(update_fields=["role"])

        result = has_permission(self.user, "users.read")

        self.assertTrue(result)

    def test_returns_false_when_role_does_not_have_permission(self):
        # Assign role without any permissions.
        self.user.role = self.role
        self.user.save(update_fields=["role"])

        result = has_permission(self.user, "users.read")

        self.assertFalse(result)

    def test_returns_false_for_unknown_permission_codename(self):
        # Assign role to user.
        self.user.role = self.role
        self.user.save(update_fields=["role"])

        result = has_permission(self.user, "unknown.permission")

        self.assertFalse(result)



class PermissionListAPITests(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            first_name="Test",
            last_name="Employee",
            email="permissiontest@example.com",
            password=make_password("TestPass123!"),
            valid_until=timezone.now() + timedelta(days=100),
        )

        self.token = create_access_token(self.user)

        self.url = "/api/permissions"

    def test_permission_list_requires_authentication(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_authenticated_user_can_list_permissions(self):
        response = self.client.get(
            self.url,
            HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertIn("permissions", data)
        self.assertIn("total_permissions", data)

        self.assertIsInstance(data["permissions"], list)

    def test_user_without_role_can_list_permissions(self):
        # This user intentionally has no assigned role.
        self.assertIsNone(self.user.role_id)

        response = self.client.get(
            self.url,
            HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )

        self.assertEqual(response.status_code, 200)



class RoleListAPITests(TestCase):

    def setUp(self):
        # Create a user who will have roles.read permission.
        self.admin_user = User.objects.create(
            first_name="Test",
            last_name="Admin",
            email="roleadmin@example.com",
            password=make_password("TestPass123!"),
            valid_until=timezone.now() + timedelta(days=100),
        )

        # Create a user without any role.
        self.employee_user = User.objects.create(
            first_name="Test",
            last_name="Employee",
            email="roleemployee@example.com",
            password=make_password("TestPass123!"),
            valid_until=timezone.now() + timedelta(days=100),
        )

        # Create a role for the admin.
        self.admin_role = Role.objects.create(
            role_name="Role List Test Admin",
            description="Role for testing role list authorization.",
        )

        # Retrieve the predefined roles.read permission.
        self.read_permission, created = Permission.objects.get_or_create(
            codename="roles.read",
            defaults={
                "permission_name": "View Roles",
                "description": "Allows viewing roles.",
            }
        )

        # Assign roles.read to the admin role.
        RolePermission.objects.create(
            role=self.admin_role,
            permission=self.read_permission,
        )

        # Assign the role to the admin user.
        self.admin_user.role = self.admin_role
        self.admin_user.save(update_fields=["role"])

        # Generate JWT tokens.
        self.admin_token = create_access_token(self.admin_user)
        self.employee_token = create_access_token(self.employee_user)

        self.url = "/api/roles"

    def test_role_list_requires_authentication(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_user_with_roles_read_can_list_roles(self):
        response = self.client.get(
            self.url,
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}"
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertIn("roles", data)
        self.assertIn("total_roles", data)
        self.assertIsInstance(data["roles"], list)

    def test_user_without_roles_read_cannot_list_roles(self):
        response = self.client.get(
            self.url,
            HTTP_AUTHORIZATION=f"Bearer {self.employee_token}"
        )

        self.assertEqual(response.status_code, 403)



class RoleCreateAPITests(TestCase):

    def setUp(self):
        self.admin = User.objects.create(
            first_name="Test",
            last_name="Admin",
            email="rolecreateadmin@example.com",
            password=make_password("TestPass123!"),
            valid_until=timezone.now() + timedelta(days=100),
        )

        self.employee = User.objects.create(
            first_name="Test",
            last_name="Employee",
            email="rolecreateemployee@example.com",
            password=make_password("TestPass123!"),
            valid_until=timezone.now() + timedelta(days=100),
        )

        # Create an admin role.
        self.admin_role = Role.objects.create(
            role_name="Role Create Test Admin",
            description="Role for testing role creation.",
        )

        # Retrieve or create the predefined permissions.
        self.create_permission, _ = Permission.objects.get_or_create(
            codename="roles.create",
            defaults={
                "permission_name": "Create Roles",
                "description": "Allows creating roles.",
            }
        )

        self.read_permission, _ = Permission.objects.get_or_create(
            codename="users.read",
            defaults={
                "permission_name": "View Users",
                "description": "Allows viewing users.",
            }
        )

        self.delete_permission, _ = Permission.objects.get_or_create(
            codename="users.delete",
            defaults={
                "permission_name": "Delete Users",
                "description": "Allows deleting users.",
            }
        )

        # Give the admin roles.create and users.read.
        RolePermission.objects.create(
            role=self.admin_role,
            permission=self.create_permission,
        )

        RolePermission.objects.create(
            role=self.admin_role,
            permission=self.read_permission,
        )

        self.admin.role = self.admin_role
        self.admin.save(update_fields=["role"])

        self.admin_token = create_access_token(self.admin)
        self.employee_token = create_access_token(self.employee)

        self.url = "/api/roles"

    def test_role_create_requires_authentication(self):
        response = self.client.post(
            self.url,
            data=json.dumps({
                "role_name": "New Role",
                "description": "Test role",
                "permissions": [],
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)

    def test_user_without_roles_create_cannot_create_role(self):
        response = self.client.post(
            self.url,
            data=json.dumps({
                "role_name": "New Role",
                "description": "Test role",
                "permissions": [],
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.employee_token}",
        )

        self.assertEqual(response.status_code, 403)

    def test_user_with_roles_create_can_create_role(self):
        response = self.client.post(
            self.url,
            data=json.dumps({
                "role_name": "New Employee",
                "description": "Standard employee role.",
                "permissions": ["users.read"],
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}",
        )

        self.assertEqual(response.status_code, 201)

        self.assertTrue(
            Role.objects.filter(role_name="New Employee").exists()
        )

        created_role = Role.objects.get(role_name="New Employee")

        self.assertTrue(
            RolePermission.objects.filter(
                role=created_role,
                permission=self.read_permission,
            ).exists()
        )

    def test_role_create_rejects_missing_role_name(self):
        response = self.client.post(
            self.url,
            data=json.dumps({
                "description": "Test role",
                "permissions": [],
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}",
        )

        self.assertEqual(response.status_code, 400)

    def test_role_create_rejects_duplicate_role_name(self):
        Role.objects.create(
            role_name="Existing Role",
            description="Already exists.",
        )

        response = self.client.post(
            self.url,
            data=json.dumps({
                "role_name": "existing role",
                "description": "Duplicate role.",
                "permissions": [],
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}",
        )

        self.assertEqual(response.status_code, 409)

    def test_role_create_rejects_unknown_permission(self):
        response = self.client.post(
            self.url,
            data=json.dumps({
                "role_name": "Unknown Permission Role",
                "description": "Test role.",
                "permissions": ["unknown.permission"],
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}",
        )

        self.assertEqual(response.status_code, 400)

    def test_role_create_prevents_privilege_escalation(self):
        # The admin has roles.create and users.read,
        # but does not have users.delete.
        response = self.client.post(
            self.url,
            data=json.dumps({
                "role_name": "Unauthorized Role",
                "description": "Test privilege escalation.",
                "permissions": ["users.delete"],
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}",
        )

        self.assertEqual(response.status_code, 403)

        self.assertFalse(
            Role.objects.filter(role_name="Unauthorized Role").exists()
        )

    def test_role_create_rejects_duplicate_permissions(self):
        response = self.client.post(
            self.url,
            data=json.dumps({
                "role_name": "Duplicate Permission Role",
                "description": "Test duplicate permissions.",
                "permissions": ["users.read", "users.read"],
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}",
        )

        self.assertEqual(response.status_code, 400)


class RoleDetailAPITests(TestCase):

    def setUp(self):
        # Create an administrator.
        self.admin = User.objects.create(
            first_name="Test",
            last_name="Admin",
            email="roledetailadmin@example.com",
            password=make_password("TestPass123!"),
            valid_until=timezone.now() + timedelta(days=100),
        )

        # Create an employee.
        self.employee = User.objects.create(
            first_name="Test",
            last_name="Employee",
            email="roledetailemployee@example.com",
            password=make_password("TestPass123!"),
            valid_until=timezone.now() + timedelta(days=100),
        )

        # Create administrator role.
        self.admin_role = Role.objects.create(
            role_name="Role Detail Test Admin",
            description="Administrator role for testing.",
        )

        # Create target role.
        self.target_role = Role.objects.create(
            role_name="Role Detail Test Employee",
            description="Employee role for testing.",
        )

        # Retrieve predefined permissions.
        self.read_roles, _ = Permission.objects.get_or_create(
            codename="roles.read",
            defaults={
                "permission_name": "View Roles",
                "description": "Allows viewing roles.",
            }
        )

        self.read_users, _ = Permission.objects.get_or_create(
            codename="users.read",
            defaults={
                "permission_name": "View Users",
                "description": "Allows viewing users.",
            }
        )

        # Give administrator roles.read.
        RolePermission.objects.create(
            role=self.admin_role,
            permission=self.read_roles,
        )

        # Give target role users.read.
        RolePermission.objects.create(
            role=self.target_role,
            permission=self.read_users,
        )

        # Assign roles to users.
        self.admin.role = self.admin_role
        self.admin.save(update_fields=["role"])

        self.employee.role = self.target_role
        self.employee.save(update_fields=["role"])

        # Generate JWT tokens.
        self.admin_token = create_access_token(self.admin)

        self.employee_token = create_access_token(self.employee)

        self.url = f"/api/roles/{self.target_role.role_id}"

    def test_role_detail_requires_authentication(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_user_with_roles_read_can_view_role_detail(self):
        response = self.client.get(
            self.url,
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}",
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Role Detail Test Employee")
        self.assertContains(response, "users.read")
        self.assertContains(response, "roledetailemployee@example.com")

    def test_user_without_roles_read_cannot_view_role_detail(self):
        response = self.client.get(
            self.url,
            HTTP_AUTHORIZATION=f"Bearer {self.employee_token}",
        )

        self.assertEqual(response.status_code, 403)

    def test_role_detail_returns_404_for_missing_role(self):
        missing_role_id = self.target_role.role_id + 999

        response = self.client.get(
            f"/api/roles/{missing_role_id}",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}",
        )

        self.assertEqual(response.status_code, 404)



class RoleUpdateAPITests(TestCase):

    def setUp(self):
        # Create administrator.
        self.admin = User.objects.create(
            first_name="Test",
            last_name="Admin",
            email="roleupdateadmin@example.com",
            password=make_password("TestPass123!"),
            valid_until=timezone.now() + timedelta(days=100),
        )

        # Create employee without a role.
        self.employee = User.objects.create(
            first_name="Test",
            last_name="Employee",
            email="roleupdateemployee@example.com",
            password=make_password("TestPass123!"),
            valid_until=timezone.now() + timedelta(days=100),
        )

        # Administrator role.
        self.admin_role = Role.objects.create(
            role_name="Role Update Test Admin",
            description="Admin role for update tests.",
        )

        # Target role.
        self.target_role = Role.objects.create(
            role_name="Role Update Test Employee",
            description="Employee role for update tests.",
        )

        # Retrieve predefined permissions.
        self.update_permission, _ = Permission.objects.get_or_create(
            codename="roles.update",
            defaults={
                "permission_name": "Update Roles",
                "description": "Allows updating roles.",
            }
        )

        self.read_permission, _ = Permission.objects.get_or_create(
            codename="users.read",
            defaults={
                "permission_name": "View Users",
                "description": "Allows viewing users.",
            }
        )

        self.delete_permission, _ = Permission.objects.get_or_create(
            codename="users.delete",
            defaults={
                "permission_name": "Delete Users",
                "description": "Allows deleting users.",
            }
        )

        # Admin gets roles.update and users.read.
        RolePermission.objects.create(
            role=self.admin_role,
            permission=self.update_permission,
        )

        RolePermission.objects.create(
            role=self.admin_role,
            permission=self.read_permission,
        )

        # Target role initially has users.read.
        RolePermission.objects.create(
            role=self.target_role,
            permission=self.read_permission,
        )

        self.admin.role = self.admin_role
        self.admin.save(update_fields=["role"])

        self.admin_token = create_access_token(self.admin)
        self.employee_token = create_access_token(self.employee)

        self.url = f"/api/roles/{self.target_role.role_id}/update"

    def test_role_update_requires_authentication(self):
        response = self.client.patch(
            self.url,
            data=json.dumps({"role_name": "Updated Role"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)

    def test_user_without_roles_update_cannot_update_role(self):
        response = self.client.patch(
            self.url,
            data=json.dumps({"role_name": "Updated Role"}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.employee_token}",
        )

        self.assertEqual(response.status_code, 403)

    def test_role_update_with_put(self):
        response = self.client.put(
            self.url,
            data=json.dumps({
                "role_name": "Updated Employee",
                "description": "Updated description.",
                "permissions": ["users.read"],
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}",
        )

        self.assertEqual(response.status_code, 200)

        self.target_role.refresh_from_db()

        self.assertEqual(
            self.target_role.role_name,
            "Updated Employee",
        )

        self.assertEqual(
            self.target_role.description,
            "Updated description.",
        )

    def test_role_update_with_patch(self):
        response = self.client.patch(
            self.url,
            data=json.dumps({
                "role_name": "PATCH Updated Employee",
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}",
        )

        self.assertEqual(response.status_code, 200)

        self.target_role.refresh_from_db()

        self.assertEqual(
            self.target_role.role_name,
            "PATCH Updated Employee",
        )

    def test_put_requires_all_fields(self):
        response = self.client.put(
            self.url,
            data=json.dumps({
                "role_name": "Incomplete Role",
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}",
        )

        self.assertEqual(response.status_code, 400)

        self.assertIn("missing_fields", response.json())

    def test_patch_rejects_empty_body(self):
        response = self.client.patch(
            self.url,
            data=json.dumps({}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}",
        )

        self.assertEqual(response.status_code, 400)

    def test_role_update_rejects_unknown_field(self):
        response = self.client.patch(
            self.url,
            data=json.dumps({
                "role_name": "Updated Role",
                "is_admin": True,
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}",
        )

        self.assertEqual(response.status_code, 400)

    def test_role_update_rejects_duplicate_role_name(self):
        Role.objects.create(
            role_name="Existing Role",
            description="Already exists.",
        )

        response = self.client.patch(
            self.url,
            data=json.dumps({
                "role_name": "existing role",
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}",
        )

        self.assertEqual(response.status_code, 409)

    def test_role_update_rejects_unknown_permission(self):
        response = self.client.patch(
            self.url,
            data=json.dumps({
                "permissions": ["unknown.permission"],
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}",
        )

        self.assertEqual(response.status_code, 400)

    def test_role_update_prevents_privilege_escalation(self):
        response = self.client.patch(
            self.url,
            data=json.dumps({
                "permissions": ["users.delete"],
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}",
        )

        self.assertEqual(response.status_code, 403)

        # Existing permission should remain unchanged.
        self.assertTrue(
            RolePermission.objects.filter(
                role=self.target_role,
                permission=self.read_permission,
            ).exists()
        )

    def test_patch_without_permissions_preserves_existing_permissions(self):
        response = self.client.patch(
            self.url,
            data=json.dumps({
                "description": "Only description updated.",
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}",
        )

        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            RolePermission.objects.filter(
                role=self.target_role,
                permission=self.read_permission,
            ).exists()
        )

    def test_patch_with_empty_permissions_clears_permissions(self):
        response = self.client.patch(
            self.url,
            data=json.dumps({
                "permissions": [],
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}",
        )

        self.assertEqual(response.status_code, 200)

        self.assertFalse(
            RolePermission.objects.filter(
                role=self.target_role,
            ).exists()
        )



class RoleDeleteAPITests(TestCase):

    def setUp(self):
        # Create an authorized admin user.
        self.admin = User.objects.create(
            first_name="Test",
            last_name="Admin",
            email="roledeleteadmin@example.com",
            password=make_password("TestPass123!"),
            valid_until=timezone.now() + timedelta(days=100),
        )

        # Create an employee without role permissions.
        self.employee = User.objects.create(
            first_name="Test",
            last_name="Employee",
            email="roledeleteemployee@example.com",
            password=make_password("TestPass123!"),
            valid_until=timezone.now() + timedelta(days=100),
        )

        # Create the admin role.
        self.admin_role = Role.objects.create(
            role_name="Role Delete Test Admin",
            description="Admin role for delete tests.",
        )

        # Create a target role.
        self.target_role = Role.objects.create(
            role_name="Role Delete Test Target",
            description="Target role for delete tests.",
        )

        # Get or create the delete permission.
        self.delete_permission, _ = Permission.objects.get_or_create(
            codename="roles.delete",
            defaults={
                "permission_name": "Delete Roles",
                "description": "Allows deleting roles.",
            }
        )

        # Assign roles.delete to the admin role.
        RolePermission.objects.create(
            role=self.admin_role,
            permission=self.delete_permission,
        )

        self.admin.role = self.admin_role
        self.admin.save(update_fields=["role"])

        # Generate JWT tokens.
        self.admin_token = create_access_token(self.admin)
        self.employee_token = create_access_token(self.employee)

        self.url = f"/api/roles/{self.target_role.role_id}"

    def test_role_delete_requires_authentication(self):
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 401)

    def test_user_without_roles_delete_cannot_delete_role(self):
        response = self.client.delete(
            self.url,
            HTTP_AUTHORIZATION=f"Bearer {self.employee_token}",
        )

        self.assertEqual(response.status_code, 403)

        self.assertTrue(
            Role.objects.filter(
                role_id=self.target_role.role_id
            ).exists()
        )

    def test_authorized_user_can_delete_role(self):
        response = self.client.delete(
            self.url,
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}",
        )

        self.assertEqual(response.status_code, 200)

        self.assertFalse(
            Role.objects.filter(
                role_id=self.target_role.role_id
            ).exists()
        )

    def test_role_assigned_to_users_cannot_be_deleted(self):
        # Assign the target role to an employee.
        self.employee.role = self.target_role
        self.employee.save(update_fields=["role"])

        response = self.client.delete(
            self.url,
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}",
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["assigned_users"], 1)

        # Verify that the role still exists.
        self.assertTrue(
            Role.objects.filter(
                role_id=self.target_role.role_id
            ).exists()
        )

    def test_delete_nonexistent_role_returns_404(self):
        nonexistent_url = "/api/roles/999999"

        response = self.client.delete(
            nonexistent_url,
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}",
        )

        self.assertEqual(response.status_code, 404)

    def test_role_endpoint_rejects_unsupported_method(self):
        response = self.client.post(
            self.url,
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}",
        )

        self.assertEqual(response.status_code, 405)
