# gitlab_wrapper/apis/users.py


class UsersAPI:
    def __init__(self, client):
        self.client = client

    def list(self):
        return self.client.get("users")

    def get_by_username(self, username):
        users = self.client.get("users", params={"username": username})
        if not users:
            raise ValueError(f"User '{username}' not found.")
        return users[0]  # GitLab returns a list even for exact username match

    def get_by_userid(self, user_id):
        user = self.client.get(f"users/{user_id}")
        if not user:
            raise ValueError(f"User '{user_id}' not found.")
        return user

    def get_user_project_count(self, user_id):
        try:
            count = self.client.get(f"/users/{user_id}/associations_count")
            project_count = count["projects_count"]
            return project_count
        except Exception as e:
            return f"Error: {e}"

    def get_user_group_count(self, user_id):
        try:
            count = self.client.get(f"/users/{user_id}/associations_count")
            group_count = count["groups_count"]
            return group_count
        except Exception as e:
            return f"Error: {e}"

    def get_user_issue_count(self, user_id):
        try:
            count = self.client.get(f"/users/{user_id}/associations_count")
            issue_count = count["issues_count"]
            return issue_count
        except Exception as e:
            return f"Error: {e}"

    def get_user_mr_count(self, user_id):
        try:
            count = self.client.get(f"/users/{user_id}/associations_count")
            mr_count = count["merge_requests_count"]
            return mr_count
        except Exception as e:
            return f"Error: {e}"
