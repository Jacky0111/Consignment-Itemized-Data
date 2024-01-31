import spacy
import os

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Define hospital names
hospital_names = [
    "ANSON BAY",
    "GLENEAGLES",
    "PANTAI ",
    "KPJ",
]

# Create data/hospitals directory if it doesn't exist
output_directory = "data/hospitals"
os.makedirs(output_directory, exist_ok=True)


# Function to generate possible variants and write to txt file
def generate_variants_and_write_to_file(hospital_name):
    doc = nlp(hospital_name)

    # Get possible variants using lemmatization and lowercasing
    variants = set([token.lemma_.lower() for token in doc if not token.is_punct])

    # Write variants to txt file
    with open(os.path.join(output_directory, f"{hospital_name}.txt"), "w") as file:
        file.write("\n".join(variants))


# Generate variants and write to txt files for each hospital
for hospital_name in hospital_names:
    generate_variants_and_write_to_file(hospital_name)
