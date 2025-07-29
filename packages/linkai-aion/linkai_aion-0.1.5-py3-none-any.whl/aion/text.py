### aion/text.py
import re
def count_words(text):
    return len(text.split())


def count_lines(text):
    return len(text.splitlines())


def summarize_text(text, max_lines=3):
    lines = text.split(". ")
    return ". ".join(lines[:max_lines]) + "."


def extract_emails(text):
    import re
    return re.findall(r'\b[\w.-]+?@\w+?\.\w+?\b', text)


def extract_urls(text):
    import re
    return re.findall(r'https?://\S+', text)


def highlight_keywords(text, words):
    for word in words:
        text = text.replace(word, f"**{word}**")
    return text





def detect_language_basic(text):
    text = text.lower()

    language_keywords = {
        'English': ['the', 'and', 'but', 'at', 'on', 'in', 'is', 'you', 'this'],
        'Russian': ['и', 'в', 'не', 'что', 'на', 'я', 'с', 'по', 'как'],
        'Armenian': ['է', 'ու', 'թե', 'մեջ', 'էին', 'բայց', 'համար', 'որ'],
        'French': ['le', 'la', 'et', 'les', 'des', 'pas', 'une', 'est', 'ce'],
        'German': ['der', 'die', 'und', 'das', 'ein', 'nicht', 'mit', 'sie'],
        'Spanish': ['el', 'la', 'y', 'los', 'una', 'que', 'por', 'con'],
        'Italian': ['il', 'la', 'e', 'che', 'non', 'per', 'con', 'una'],
        'Portuguese': ['o', 'a', 'e', 'que', 'de', 'do', 'na', 'com'],
        'Turkish': ['ve', 'bir', 'bu', 'ile', 'için', 'ama', 'çok', 'değil'],
        'Chinese (Pinyin)': ['de', 'shi', 'bu', 'wo', 'zai', 'hen', 'ni'],
        'Japanese (Romaji)': ['desu', 'watashi', 'kore', 'sore', 'ano', 'demo'],
        'Korean (Romanized)': ['neun', 'eun', 'gwa', 'geot', 'haneun', 'ibnida'],
        'Hindi (Romanized)': ['hai', 'aur', 'ka', 'mein', 'nahi', 'ke', 'tum'],
        'Arabic (Romanized)': ['wa', 'fi', 'la', 'min', 'ana', 'huwa', 'laysa']
    }

    matches = {}

    for lang, words in language_keywords.items():
        matches[lang] = sum(word in text for word in words)

    detected = max(matches, key=matches.get)

    # Optional: confidence threshold
    if matches[detected] == 0:
        return 'Unknown'

    return detected




def find_palindromes(text):
     text = text.lower()

     if len(text) >= 3:
         if text == text[::-1]:  # this reverses the string
             print("palindrome")
         else:
             print("not a palindrome")
     else:
         print("too short")











# 	Check if text is a question
def is_question(text):
    return text.strip().endswith('?')


# Normalize whitespace
def normalize_whitespace(text):
    return re.sub(r'\s+', ' ', text).strip()






#  is_sensitive_text(text)
#
# Flags text that may include sensitive data like passwords, tokens, emails, phone numbers, etc.

def is_sensitive_text(text):
    patterns = [
        r'\b\d{3}-\d{2}-\d{4}\b',      # SSN
        r'\b(?:\+?\d{1,3})?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',  # Phone
        r'\b[\w.-]+?@\w+?\.\w+?\b',    # Email
        r'(password\s*[:=]\s*.+)',     # Password patterns
        r'(api[_\-]?key\s*[:=]\s*.+)'  # API key
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)




# text_contains_visual_language(text)
#
# Checks if the text describes visual elements (useful for AI image prompts or creative writing).
def text_contains_visual_language(text):
    visual_keywords = ['see', 'look', 'bright', 'dark', 'color', 'image', 'view', 'vision', 'shape']
    return any(word in text.lower() for word in visual_keywords)




