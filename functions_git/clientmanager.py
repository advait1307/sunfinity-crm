import os
import pandas as pd
from functions_git.github_file_manager import GitHubFileManager
class ClientManager:
    def __init__(self, config):
        self.config = config
        self.fields = self.config['clients']['fields']
        self.github_manager = GitHubFileManager(
            config['github_token'],
            config['github_repo']
        )
        self.file_path = config['clients_excel_path']

    def load_clients(self):
        return self.github_manager.read_excel(self.file_path)

    def save_clients(self, df):
        self.github_manager.write_excel(df, self.file_path)

    def generate_client_id(self, df):
        prefix = "CID"
        if df.empty:
            return f"{prefix}01"
        last_id = (
            df['Client ID']
            .str.replace(prefix, '', regex=False)
            .astype(int)
            .max()
        )
        return f"{prefix}{last_id + 1:02d}"

    def format_contact(self, name, number, email):
        return f"{name}  |  {number}  |  {email}" if any([name, number, email]) else 'NaN'
