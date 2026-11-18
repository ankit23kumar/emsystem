from .models import RolePermission


def has_permission(user, codename):
    """
    Check whether a user has a specific permission through their assigned role.
    """

    # A user without a role has no role-based permissions.
    if not user or not user.role_id:
        return False

    return RolePermission.objects.filter(
        role_id=user.role_id,
        permission__codename=codename
    ).exists()