# github_file_manager.py
from github import Github
import pandas as pd
import io
import base64

class GitHubFileManager:
    def __init__(self, token, repo_name):
        self.g = Github(token)
        self.repo = self.g.get_repo(repo_name)

    def read_excel(self, path):
        file_content = self.repo.get_contents(path)
        decoded = base64.b64decode(file_content.content)
        return pd.read_excel(io.BytesIO(decoded))

    def write_excel(self, df, path, message="Update Excel file"):
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        content = excel_buffer.read()
        try:
            file_content = self.repo.get_contents(path)
            self.repo.update_file(path, message, content, file_content.sha)
        except Exception:
            self.repo.create_file(path, message, content)