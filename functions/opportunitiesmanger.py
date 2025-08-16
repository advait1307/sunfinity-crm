import os
import pandas as pd


class OpportunitiesManager:
    def __init__(self, config):
        self.config = config
        self.file_path = self.config['opportunities']['file']
        self.fields = self.config['opportunities']['fields']

    def load_opps(self):
        if os.path.exists(self.file_path):
            return pd.read_excel(self.file_path)
        return pd.DataFrame(columns=self.fields)

    def save_opps(self, df):
        df.to_excel(self.file_path, index=False)

    def generate_opp_id(self, df_opps):
        if df_opps.empty or 'Opp ID' not in df_opps.columns:
            next_num = 1
        else:
            # Extract numeric part from IDs like 'OPP000001'
            nums = (
                df_opps['Opp ID']
                .astype(str)
                .str.extract(r'OPP(\d{6})')[0]
                .dropna()
                .astype(int)
            )
            next_num = nums.max() + 1 if not nums.empty else 1
        return f"OPP{next_num:06d}"

    def generate_candidate_links(self, names, df_resumes):
        links = []
        for name in names:
            row = df_resumes[df_resumes['Name'] == name]
            if not row.empty:
                resume_link = row.iloc[0]['Resume']
                if pd.notnull(resume_link) and resume_link not in ['NaN', '', 'No Resume Uploaded']:
                    links.append(f"[{name}_resume]({resume_link})")
        return '\n'.join(links)

    def update_candidate_count(self,df_opps, opp_ids, increment=True):
        for opp_id in opp_ids:
            idx = df_opps[df_opps['Opp ID'] == opp_id].index
            if not idx.empty:
                val = df_opps.at[idx[0], 'Number of candidates shared']
                current = 0 if pd.isna(val) else int(val)
                df_opps.at[idx[0], 'Number of candidates shared'] = max(current + (1 if increment else -1), 0)

