import os
import pandas as pd
from functions_git.github_file_manager import GitHubFileManager


class ResumeManager:
    def __init__(self, config):
        self.config = config
        self.fields = self.config['resumes']['fields']
        self.github_manager = GitHubFileManager(
            config['github_token'],
            config['github_repo']
        )
        self.file_path = config['resumes_excel_path']

    def load_resumes(self):
        return self.github_manager.read_excel(self.file_path)

    def save_resumes(self, df):
        self.github_manager.write_excel(df, self.file_path)

    def generate_resume_id(self, df):
        prefix = "RID"
        if df.empty:
            return f"{prefix}01"
        ids = (
            df['Entry ID']
            .dropna()
            .astype(str)
            .str.replace(prefix, '', regex=False)
        )
        ids = ids[ids.str.isnumeric()]
        last_id = ids.astype(int).max() if not ids.empty else 0
        return f"{prefix}{last_id + 1:02d}"
