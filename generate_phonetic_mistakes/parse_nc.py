import pandas as pd


df = pd.read_csv(
    "generate_phonetic_mistakes/ncvoter_3000000.txt",
    sep="\t",
    quotechar='"',
    encoding="latin1",
    dtype=str,
    low_memory=False
)

print("DataFrame loaded successfully.")

df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# Assuming df is already loaded
df = df.astype(str)  # ensure all fields are strings

# --- NAME ---
df["Name"] = (
    df["first_name"].str.strip() + " " +
    df["middle_name"].str.strip().replace("nan", "") + " " +
    df["last_name"].str.strip()
).str.replace(r"\s+", " ", regex=True).str.strip()

print("Name column processed successfully.")

# --- COUNTY ---
df["County"] = df["county_desc"].str.strip()

# --- City ---
df["City"] = df["res_city_desc"].str.strip()

# --- ZipCode ---
df["ZipCode"] = df["zip_code"].str.strip()

print("ZipCode column processed successfully.")

# --- BIRTH YEAR ---
df["BirthYear"] = df["birth_year"].astype(str).str.strip()

print("BirthYear column processed successfully.")

# --- AGE ---
df["Age"] = df["age_at_year_end"].astype(str).str.strip()

print("Age column processed successfully.")

df = df.replace({"": pd.NA, " ": pd.NA, "nan": pd.NA})


# --- FINAL SUBSET ---
subset = df[["Name", "County", "City", "ZipCode", "BirthYear", "Age"]].dropna()

subset = subset.drop_duplicates(subset=["City"])

subset = subset.head(100)

print("Final subset created successfully.")

subset.to_csv("website_audio_input/parsed_ncvoter_subset.csv", index=False)
print("Parsed data saved to CSV file.")