import os
import pandas as pd



class ClientManager:
    def __init__(self, config):
        self.config = config
        self.file_path = self.config['clients']['file']
        self.fields = self.config['clients']['fields']

    def load_clients(self):
        if os.path.exists(self.file_path):
            return pd.read_excel(self.file_path)
        return pd.DataFrame(columns=self.fields)

    def save_clients(self, df):
        df.to_excel(self.file_path, index=False)

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
