import os
import pandas as pd

class ResumeManager:
    def __init__(self, config):
        self.config = config
        self.file_path = self.config['resumes']['file']
        self.fields = self.config['resumes']['fields']

    def load_resumes(self):
        if os.path.exists(self.file_path):
            return pd.read_excel(self.file_path)
        return pd.DataFrame(columns=self.fields)

    def save_resume_file(self, df):
        df.to_excel(self.file_path, index=False)

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
