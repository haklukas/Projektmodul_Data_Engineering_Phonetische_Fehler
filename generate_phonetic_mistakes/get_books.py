import requests
import csv
import time
import re

# ---------------------------------------------------------
# 1. OCLC Library 100 Titles (FULL LIST INCLUDED)
# ---------------------------------------------------------
oclc_titles = [
    "Don Quixote",
    "Alice's Adventures in Wonderland",
    "The Adventures of Huckleberry Finn",
    "The Adventures of Tom Sawyer",
    "Treasure Island",
    "Pride and Prejudice",
    "Wuthering Heights",
    "Jane Eyre",
    "Moby Dick",
    "The Scarlet Letter",
    "Gulliver's Travels",
    "The Pilgrim's Progress",
    "A Christmas Carol",
    "David Copperfield",
    "A Tale of Two Cities",
    "Little Women",
    "Great Expectations",
    "The Hobbit",
    "Frankenstein",
    "Oliver Twist",
    "Uncle Tom's Cabin",
    "Crime and Punishment",
    "Madame Bovary",
    "The Return of the King",
    "Dracula",
    "The Three Musketeers",
    "Brave New World",
    "War and Peace",
    "To Kill a Mockingbird",
    "The Wizard of Oz",
    "Les Misérables",
    "The Secret Garden",
    "Animal Farm",
    "The Great Gatsby",
    "The Little Prince",
    "The Call of the Wild",
    "20,000 Leagues Under the Sea",
    "Anna Karenina",
    "The Wind in the Willows",
    "The Picture of Dorian Gray",
    "The Grapes of Wrath",
    "Sense and Sensibility",
    "The Last of the Mohicans",
    "Tess of the d'Urbervilles",
    "Harry Potter and the Sorcerer's Stone",
    "Heidi",
    "Ulysses",
    "The Complete Sherlock Holmes",
    "The Count of Monte Cristo",
    "The Old Man and the Sea",
    "The Lion, the Witch and the Wardrobe",
    "The Hunchback of Notre Dame",
    "Pinocchio",
    "One Hundred Years of Solitude",
    "Ivanhoe",
    "The Red Badge of Courage",
    "Anne of Green Gables",
    "Black Beauty",
    "Peter Pan",
    "A Farewell to Arms",
    "The House of the Seven Gables",
    "Lord of the Flies",
    "The Prince and the Pauper",
    "A Portrait of the Artist as a Young Man",
    "Lord Jim",
    "Harry Potter and the Chamber of Secrets",
    "Red and Black",
    "The Stranger",
    "The Trial",
    "Lady Chatterley's Lover",
    "Kidnapped",
    "The Catcher in the Rye",
    "Fahrenheit 451",
    "Journey to the Centre of the Earth",
    "Vanity Fair",
    "All Quiet on the Western Front",
    "Gone with the Wind",
    "My Ántonia",
    "Of Mice and Men",
    "The Vicar of Wakefield",
    "A Connecticut Yankee in King Arthur's Court",
    "White Fang",
    "Fathers and Sons",
    "Doctor Zhivago",
    "The Decameron",
    "Nineteen Eighty-Four",
    "The Jungle",
    "The Da Vinci Code",
    "Persuasion",
    "Mansfield Park",
    "Candide",
    "For Whom the Bell Tolls",
    "Far from the Madding Crowd",
    "The Fellowship of the Ring",
    "The Return of the Native",
    "Sons and Lovers",
    "Charlotte's Web",
    "The Swiss Family Robinson",
    "Bleak House",
    "Père Goriot"
]

# ---------------------------------------------------------
# 2. Retry wrapper
# ---------------------------------------------------------
def retry_until_found(func, *args, delay=3):
    """Retry a function until it returns a non-None result."""
    while True:
        try:
            result = func(*args)
            if result:
                return result
            print(f"Retrying in {delay}s...")
        except Exception as e:
            print(f"Error: {e} — retrying in {delay}s...")
        time.sleep(delay)

# ---------------------------------------------------------
# 3. Find work key
# ---------------------------------------------------------
def find_work_key(title):
    url = f"https://openlibrary.org/search.json?title={title}"
    r = requests.get(url, timeout=10)
    data = r.json()
    docs = data.get("docs", [])
    if not docs:
        return None
    return docs[0].get("key")

# ---------------------------------------------------------
# 4. Extract clean year
# ---------------------------------------------------------
def extract_year(date_string):
    """Extract a clean 4-digit year. Accepts 'Dec 14, 2010', rejects '199u'."""
    if not date_string:
        return None

    # Find any clean 4-digit year
    match = re.search(r"\b(19|20)\d{2}\b", date_string)
    if match:
        return match.group(0)

    return None  # reject fuzzy years

# ---------------------------------------------------------
# 5. Fetch COMPLETE edition metadata
# ---------------------------------------------------------
def fetch_complete_edition(work_key):
    url = f"https://openlibrary.org{work_key}/editions.json"
    r = requests.get(url, timeout=10)
    data = r.json()
    editions = data.get("entries", [])
    if not editions:
        return None

    for ed in editions:
        # Extract ISBN
        isbn13 = ed.get("isbn_13", [""])
        isbn10 = ed.get("isbn_10", [""])

        isbn = ""
        if isbn13 and isbn13[0]:
            isbn = isbn13[0]
        elif isbn10 and isbn10[0]:
            isbn = isbn10[0]

        publisher = ed.get("publishers", [""])[0] if ed.get("publishers") else ""
        publish_year = extract_year(ed.get("publish_date", ""))

        # Accept only complete rows
        if isbn and publisher and publish_year:
            return {
                "isbn": isbn,
                "publisher": publisher,
                "publish_year": publish_year
            }

    return None

# ---------------------------------------------------------
# 6. Write CSV
# ---------------------------------------------------------
with open("oclc_library_100.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Title", "ISBN", "Publisher", "Publish Year"])

    for title in oclc_titles:
        print(f"\n=== Fetching: {title} ===")

        work_key = retry_until_found(find_work_key, title)
        print(f"Found work key: {work_key}")

        meta = retry_until_found(fetch_complete_edition, work_key)
        print(f"Found complete edition for: {title}")

        writer.writerow([
            title,
            meta["isbn"],
            meta["publisher"],
            meta["publish_year"]
        ])

print("\nDone! CSV written: oclc_library_100.csv")
