class SecuritySandbox:
    def __init__(self):
        self.permissions = {
            "file_system_read": False,
            "file_system_write": False,
            "network_access": False,
            "native_calls": False,
        }

    def grant_permission(self, permission_type):
        if permission_type in self.permissions:
            self.permissions[permission_type] = True
        else:
            raise Exception(f"Unknown permission type: {permission_type}")

    def revoke_permission(self, permission_type):
        if permission_type in self.permissions:
            self.permissions[permission_type] = False
        else:
            raise Exception(f"Unknown permission type: {permission_type}")

    def check_permission(self, permission_type):
        if permission_type not in self.permissions:
            raise Exception(f"Unknown permission type: {permission_type}")
        if not self.permissions[permission_type]:
            raise Exception(f"Permission denied: {permission_type}")
        return True
