import requests

class Gitlab:
    def __init__(self, url, project_id, token):
        self.url = url
        self.project_id = project_id
        self.token = token

    def create_variable(self, key, value):
        resp = requests.post(
            f"{self.url}/api/v4/projects/{self.project_id}/variables/?access_token={self.token}", data={"key": key, "value": value})
        print(f"variable {key} create result {resp.status_code}")
        return resp.status_code

    def delete_variable(self, key):
        resp = requests.delete(
            f"{self.url}/api/v4/projects/{self.project_id}/variables/{key}?access_token={self.token}")
        print(f"variable {key} create result {resp.status_code}")
        return resp.status_code

    def get_variable(self, key):
        resp = requests.get(
            f"{self.url}/api/v4/projects/{self.project_id}/variables/{key}?access_token={self.token}")
        print(f"variable {key} create result {resp.status_code}")
        return resp.status_code

    def update_variable(self, key, value, delete_if_present = True):
        if self.get_variable(key) == 200:
            if delete_if_present:
                self.delete_variable(key)
        self.create_variable(key, value)