
import pandas as pd
import numpy as np

# ─────────────────────────────────────────
# 1. LOAD DATA
# ─────────────────────────────────────────
df = pd.read_csv("campaign_messy.csv")


# ─────────────────────────────────────────
# 2. FIX COLUMN NAMES
# ─────────────────────────────────────────
df.columns = df.columns.str.strip().str.lower()
df = df.loc[:, ~df.columns.duplicated()]
df['campaign_tag'] = df['campaign_tag'].str.strip()
df['channel']      = df['channel'].str.strip()


# ─────────────────────────────────────────
# 3. FIX DATES
# ─────────────────────────────────────────
df['start_date'] = pd.to_datetime(
    df['start_date'].astype(str).str.strip(),
    format='mixed', dayfirst=True
).dt.date

df['end_date'] = pd.to_datetime(
    df['end_date'].astype(str).str.strip(),
    format='mixed', dayfirst=True
).dt.date

# Swap logically reversed dates
date_mask = df['start_date'] > df['end_date']
df.loc[date_mask, ['start_date', 'end_date']] = (
    df.loc[date_mask, ['end_date', 'start_date']].values
)


# ─────────────────────────────────────────
# 4. FIX CHANNEL
# ─────────────────────────────────────────
df['channel'] = df['channel'].replace(r'[-_]', '', regex=True)

df.loc[df['campaign_tag'] == 'E-', 'channel'] = 'Email'

df['channel'] = df['channel'].replace({
    'E-mail'    : 'Email',
    'Facebok'   : 'Facebook',
    'Gogle'     : 'Google Ads',
    'Insta_gram': 'Instagram',
    'Tik_Tok'   : 'TikTok'
})

df['channel'] = df['channel'].fillna('Unknown')

df.loc[
    df['campaign_tag'].str.startswith('E-', na=False) & (df['channel'] == 'Unknown'),
    'channel'
] = 'Email'


# ─────────────────────────────────────────
# 5. FIX CONVERSIONS
# ─────────────────────────────────────────
df['conversions'] = df['conversions'].fillna(0).astype(int)


# ─────────────────────────────────────────
# 6. FIX SPEND
# ─────────────────────────────────────────
df['spend'] = (
    df['spend']
    .astype(str)
    .str.replace(r'[\$,]', '', regex=True)
)
df['spend'] = pd.to_numeric(df['spend'], errors='coerce').abs()


# ─────────────────────────────────────────
# 7. FIX ACTIVE FLAG
# ─────────────────────────────────────────
df['active'] = df['active'].astype(str).str.lower().str.strip()
df.loc[df['active'].isin(['1', 'y', 'yes', 'true']),  'active'] = 'yes'
df.loc[df['active'].isin(['0', 'f', 'no', 'false']),  'active'] = 'no'


# ─────────────────────────────────────────
# 8. REBUILD CAMPAIGN TAG
# ─────────────────────────────────────────
TAG_MAP = {
    'TikTok'    : 'TI',
    'Facebook'  : 'FA',
    'Email'     : 'EM',
    'Google Ads': 'GO',
    'Instagram' : 'IN',
    'Unknown'   : 'UN'
}
df['campaign_tag'] = df['channel'].map(TAG_MAP)


# ─────────────────────────────────────────
# 9. CREATE REVENUE COLUMNS
# ─────────────────────────────────────────
REVENUE_PER_CONVERSION = {
    'Facebook'  : 45.0,
    'Google Ads': 80.0,
    'Instagram' : 50.0,
    'TikTok'    : 30.0,
    'Unknown'   : 20.0,
    'Email'     : 70.0
}

df['revenue_per_conversion'] = df['channel'].map(REVENUE_PER_CONVERSION)
df['revenue']                = df['conversions'] * df['revenue_per_conversion']


# ─────────────────────────────────────────
# 10. EXPORT
# ─────────────────────────────────────────
df.to_csv("campaign.csv", index=False)
print("Done → campaign_clean.csv")
print(df.shape)
print(df.dtypes)