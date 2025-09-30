"""
Python re Module - Complete Guide & Cheat Sheet
================================================

A comprehensive guide to mastering Python's regular expressions (re module)
with practical examples, patterns, and real-world use cases.

Author: Professional Python Developer
Created: 2025-09-30
"""

import re
from typing import List, Optional, Pattern, Match
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# PART 1: BASIC PATTERNS - THE BUILDING BLOCKS
# ============================================================================

def demo_basic_patterns() -> None:
    """
    Basic pattern matching characters.
    
    REMEMBER:
    .   = Any character (except newline)
    ^   = Start of string
    $   = End of string
    *   = 0 or more times
    +   = 1 or more times
    ?   = 0 or 1 time
    {n} = Exactly n times
    {n,m} = Between n and m times
    """
    
    text = "Hello World 2025!"
    
    # . matches any character
    pattern = r"H.llo"
    print(f"Pattern '{pattern}' matches: {re.search(pattern, text)}")
    # Output: Matches "Hello"
    
    # ^ matches start of string
    pattern = r"^Hello"
    print(f"Pattern '{pattern}' matches: {re.search(pattern, text)}")
    # Output: Matches because string starts with "Hello"
    
    # $ matches end of string
    pattern = r"2025!$"
    print(f"Pattern '{pattern}' matches: {re.search(pattern, text)}")
    # Output: Matches because string ends with "2025!"
    
    # * matches 0 or more
    pattern = r"Hel*o"  # Matches "Heo", "Helo", "Hello", "Helllo"
    print(f"Pattern '{pattern}' in 'Heo': {re.search(pattern, 'Heo')}")
    
    # + matches 1 or more
    pattern = r"l+"  # Matches one or more 'l'
    print(f"Pattern '{pattern}' matches: {re.findall(pattern, text)}")
    # Output: ['ll', 'l']
    
    # ? matches 0 or 1
    pattern = r"colou?r"  # Matches "color" or "colour"
    print(f"Pattern '{pattern}' in 'color': {re.search(pattern, 'color')}")
    print(f"Pattern '{pattern}' in 'colour': {re.search(pattern, 'colour')}")


# ============================================================================
# PART 2: CHARACTER CLASSES - MATCHING GROUPS OF CHARACTERS
# ============================================================================

def demo_character_classes() -> None:
    """
    Character classes for matching specific types of characters.
    
    REMEMBER:
    [abc]   = Match a, b, or c
    [^abc]  = Match anything EXCEPT a, b, or c
    [a-z]   = Match lowercase letters
    [A-Z]   = Match uppercase letters
    [0-9]   = Match digits
    \d      = Digit [0-9]
    \D      = Non-digit
    \w      = Word character [a-zA-Z0-9_]
    \W      = Non-word character
    \s      = Whitespace (space, tab, newline)
    \S      = Non-whitespace
    """
    
    text = "User: john_doe123, Email: test@email.com, Phone: 555-1234"
    
    # [abc] - Match any of these characters
    pattern = r"[aeiou]"  # Match vowels
    vowels = re.findall(pattern, "Hello World")
    print(f"Vowels found: {vowels}")
    # Output: ['e', 'o', 'o']
    
    # [^abc] - Match anything EXCEPT these
    pattern = r"[^aeiou]"  # Match consonants and non-letters
    consonants = re.findall(pattern, "Hello")
    print(f"Non-vowels: {consonants}")
    # Output: ['H', 'l', 'l']
    
    # \d - Match digits
    pattern = r"\d+"  # Match one or more digits
    numbers = re.findall(pattern, text)
    print(f"Numbers found: {numbers}")
    # Output: ['123', '555', '1234']
    
    # \w - Match word characters (letters, digits, underscore)
    pattern = r"\w+"  # Match words
    words = re.findall(pattern, text)
    print(f"Words found: {words}")
    
    # \s - Match whitespace
    pattern = r"\s+"  # Match spaces
    spaces = re.findall(pattern, text)
    print(f"Spaces found: {len(spaces)} spaces")
    
    # [a-z] - Range matching
    pattern = r"[a-z]+"  # Match lowercase words
    lowercase = re.findall(pattern, text)
    print(f"Lowercase words: {lowercase}")


# ============================================================================
# PART 3: MAIN FUNCTIONS - YOUR TOOLBOX
# ============================================================================

def demo_main_functions() -> None:
    """
    The 5 main re functions you'll use 90% of the time.
    
    REMEMBER THE 5:
    1. re.search()  - Find FIRST match anywhere
    2. re.match()   - Match at BEGINNING only
    3. re.findall() - Find ALL matches (returns list)
    4. re.finditer()- Find ALL matches (returns iterator)
    5. re.sub()     - Find and REPLACE
    """
    
    text = "Contact: john@email.com or jane@company.com"
    
    # 1. re.search() - Find first match
    print("\n1. re.search() - Find FIRST match:")
    match = re.search(r"\w+@\w+\.\w+", text)
    if match:
        print(f"   Found: {match.group()}")
        print(f"   Position: {match.start()} to {match.end()}")
    # Output: john@email.com
    
    # 2. re.match() - Match at start only
    print("\n2. re.match() - Match at START:")
    match = re.match(r"Contact", text)
    print(f"   Match at start: {match.group() if match else 'No match'}")
    
    match = re.match(r"john", text)
    print(f"   'john' at start: {match if match else 'No match (not at start!)'}")
    
    # 3. re.findall() - Find all matches
    print("\n3. re.findall() - Find ALL matches:")
    emails = re.findall(r"\w+@\w+\.\w+", text)
    print(f"   All emails: {emails}")
    # Output: ['john@email.com', 'jane@company.com']
    
    # 4. re.finditer() - Find all with details
    print("\n4. re.finditer() - Find ALL with details:")
    for i, match in enumerate(re.finditer(r"\w+@\w+\.\w+", text), 1):
        print(f"   Email {i}: {match.group()} at position {match.start()}")
    
    # 5. re.sub() - Find and replace
    print("\n5. re.sub() - REPLACE:")
    censored = re.sub(r"\w+@\w+\.\w+", "[EMAIL HIDDEN]", text)
    print(f"   Original: {text}")
    print(f"   Censored: {censored}")


# ============================================================================
# PART 4: GROUPS - CAPTURING PARTS OF MATCHES
# ============================================================================

def demo_groups() -> None:
    """
    Groups allow you to capture parts of your match.
    
    REMEMBER:
    (...)     = Capturing group
    (?:...)   = Non-capturing group
    (?P<name>...) = Named group
    \1, \2    = Back-reference to group 1, 2
    """
    
    # Basic groups with parentheses
    text = "John Doe, age 30, email: john@email.com"
    
    # Capturing groups
    pattern = r"(\w+)@(\w+)\.(\w+)"
    match = re.search(pattern, text)
    if match:
        print("Groups captured:")
        print(f"  Full match: {match.group(0)}")  # or match.group()
        print(f"  Group 1 (username): {match.group(1)}")
        print(f"  Group 2 (domain): {match.group(2)}")
        print(f"  Group 3 (extension): {match.group(3)}")
        print(f"  All groups: {match.groups()}")
    
    # Named groups (easier to remember!)
    pattern = r"(?P<username>\w+)@(?P<domain>\w+)\.(?P<ext>\w+)"
    match = re.search(pattern, text)
    if match:
        print("\nNamed groups:")
        print(f"  Username: {match.group('username')}")
        print(f"  Domain: {match.group('domain')}")
        print(f"  Extension: {match.group('ext')}")
        print(f"  As dict: {match.groupdict()}")
    
    # Non-capturing groups (for grouping without capturing)
    pattern = r"(?:Mr|Mrs|Ms)\. (\w+)"
    text2 = "Hello Mr. Smith and Mrs. Johnson"
    matches = re.findall(pattern, text2)
    print(f"\nNon-capturing groups: {matches}")
    # Output: ['Smith', 'Johnson'] - title not captured


# ============================================================================
# PART 5: FLAGS - MODIFYING BEHAVIOR
# ============================================================================

def demo_flags() -> None:
    """
    Flags modify how patterns match.
    
    REMEMBER THE COMMON FLAGS:
    re.IGNORECASE (re.I)  = Case-insensitive
    re.MULTILINE (re.M)   = ^ and $ match line starts/ends
    re.DOTALL (re.S)      = . matches newlines too
    re.VERBOSE (re.X)     = Allow comments in pattern
    """
    
    text = "Hello WORLD\nGoodbye world"
    
    # re.IGNORECASE - Case insensitive matching
    pattern = r"world"
    print("Without flag:", re.findall(pattern, text))
    print("With IGNORECASE:", re.findall(pattern, text, re.IGNORECASE))
    # Output: ['WORLD', 'world']
    
    # re.MULTILINE - ^ and $ match line boundaries
    pattern = r"^Goodbye"
    print("\nWithout MULTILINE:", re.findall(pattern, text))
    print("With MULTILINE:", re.findall(pattern, text, re.MULTILINE))
    
    # re.VERBOSE - Add comments to your regex
    pattern = r"""
        (?P<username>\w+)  # Username part
        @                   # @ symbol
        (?P<domain>\w+)    # Domain name
        \.                  # Dot
        (?P<ext>\w+)       # Extension
    """
    email = "john@email.com"
    match = re.search(pattern, email, re.VERBOSE)
    print(f"\nVERBOSE pattern matched: {match.group() if match else 'No match'}")
    
    # Combine multiple flags with |
    pattern = r"hello.*world"
    text2 = "Hello\nWORLD"
    match = re.search(pattern, text2, re.IGNORECASE | re.DOTALL)
    print(f"Combined flags: {match.group() if match else 'No match'}")


# ============================================================================
# PART 6: REAL-WORLD EXAMPLES - PRACTICAL PATTERNS
# ============================================================================

def validate_email(email: str) -> bool:
    """
    Validate email address.
    
    Pattern explanation:
    ^              - Start of string
    [a-zA-Z0-9._]+ - Username (letters, numbers, dots, underscores)
    @              - @ symbol
    [a-zA-Z0-9.-]+ - Domain name
    \.             - Dot
    [a-zA-Z]{2,}   - Extension (at least 2 letters)
    $              - End of string
    """
    pattern = r"^[a-zA-Z0-9._]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Validate US phone number.
    
    Accepts formats:
    - 555-1234
    - (555) 123-4567
    - 555.123.4567
    - 5551234567
    """
    pattern = r"^(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$"
    return bool(re.match(pattern, phone))


def extract_urls(text: str) -> List[str]:
    """
    Extract all URLs from text.
    
    Pattern explanation:
    https?://      - http or https
    [^\s]+         - Any non-whitespace characters
    """
    pattern = r"https?://[^\s]+"
    return re.findall(pattern, text)


def extract_hashtags(text: str) -> List[str]:
    """Extract hashtags from social media text."""
    pattern = r"#\w+"
    return re.findall(pattern, text)


def mask_credit_card(card: str) -> str:
    """
    Mask credit card numbers.
    
    Input:  1234-5678-9012-3456
    Output: ****-****-****-3456
    """
    pattern = r"\d{4}-\d{4}-\d{4}-(\d{4})"
    return re.sub(pattern, r"****-****-****-\1", card)


def extract_dates(text: str) -> List[str]:
    """
    Extract dates in format: DD/MM/YYYY or DD-MM-YYYY.
    """
    pattern = r"\d{2}[-/]\d{2}[-/]\d{4}"
    return re.findall(pattern, text)


def validate_password(password: str) -> bool:
    """
    Validate password strength:
    - At least 8 characters
    - Contains uppercase
    - Contains lowercase
    - Contains digit
    - Contains special character
    """
    if len(password) < 8:
        return False
    
    checks = [
        r"[A-Z]",      # Uppercase
        r"[a-z]",      # Lowercase
        r"\d",         # Digit
        r"[!@#$%^&*]"  # Special character
    ]
    
    return all(re.search(check, password) for check in checks)


# ============================================================================
# PART 7: COMPILED PATTERNS - FOR BETTER PERFORMANCE
# ============================================================================

def demo_compiled_patterns() -> None:
    """
    Compile patterns for reuse (faster when used multiple times).
    
    REMEMBER: Use re.compile() when using same pattern multiple times
    """
    
    # Compile the pattern once
    email_pattern: Pattern = re.compile(r"\w+@\w+\.\w+", re.IGNORECASE)
    
    texts = [
        "Contact: john@email.com",
        "Email: JANE@COMPANY.COM",
        "Reach me at: bob@site.org"
    ]
    
    print("Using compiled pattern:")
    for text in texts:
        match = email_pattern.search(text)
        if match:
            print(f"  Found: {match.group()}")
    
    # Can use all methods on compiled pattern
    print("\nUsing findall on compiled pattern:")
    all_text = " ".join(texts)
    emails = email_pattern.findall(all_text)
    print(f"  All emails: {emails}")


# ============================================================================
# PART 8: COMMON MISTAKES TO AVOID
# ============================================================================

def demo_common_mistakes() -> None:
    """Common regex mistakes and how to avoid them."""
    
    text = "Price: $100.50"
    
    # MISTAKE 1: Forgetting to escape special characters
    print("MISTAKE 1: Not escaping special characters")
    wrong = re.findall(r"$\d+", text)  # $ has special meaning!
    correct = re.findall(r"\$\d+", text)  # Escape with \
    print(f"  Wrong: {wrong}")
    print(f"  Correct: {correct}")
    
    # MISTAKE 2: Using .* too greedily
    print("\nMISTAKE 2: Greedy vs Non-greedy")
    html = "<div>Content 1</div><div>Content 2</div>"
    greedy = re.findall(r"<div>.*</div>", html)  # Matches too much!
    non_greedy = re.findall(r"<div>.*?</div>", html)  # Use ? for non-greedy
    print(f"  Greedy: {greedy}")
    print(f"  Non-greedy: {non_greedy}")
    
    # MISTAKE 3: Forgetting raw strings (r"")
    print("\nMISTAKE 3: Not using raw strings")
    path = r"C:\new\test"
    wrong_pattern = "\n"  # \n is interpreted as newline!
    correct_pattern = r"\n"  # Raw string preserves backslash
    print(f"  Always use r'' for patterns!")
    
    # MISTAKE 4: Not handling None from search()
    print("\nMISTAKE 4: Not checking if match found")
    match = re.search(r"xyz", "abc")
    # Wrong: match.group()  # This would crash!
    # Correct:
    if match:
        print(f"  Found: {match.group()}")
    else:
        print(f"  No match found (handled safely)")


# ============================================================================
# PART 9: QUICK REFERENCE CHEAT SHEET
# ============================================================================

def print_cheat_sheet() -> None:
    """Print a quick reference guide."""
    
    cheat_sheet = """
    ╔════════════════════════════════════════════════════════════════╗
    ║           PYTHON RE MODULE - QUICK REFERENCE                   ║
    ╠════════════════════════════════════════════════════════════════╣
    ║ BASIC PATTERNS                                                 ║
    ╠════════════════════════════════════════════════════════════════╣
    ║ .        Any character (except newline)                        ║
    ║ ^        Start of string                                       ║
    ║ $        End of string                                         ║
    ║ *        0 or more times                                       ║
    ║ +        1 or more times                                       ║
    ║ ?        0 or 1 time                                           ║
    ║ {n}      Exactly n times                                       ║
    ║ {n,m}    Between n and m times                                 ║
    ╠════════════════════════════════════════════════════════════════╣
    ║ CHARACTER CLASSES                                              ║
    ╠════════════════════════════════════════════════════════════════╣
    ║ [abc]    Match a, b, or c                                      ║
    ║ [^abc]   Match anything EXCEPT a, b, or c                      ║
    ║ [a-z]    Match lowercase letters                               ║
    ║ [0-9]    Match digits                                          ║
    ║ \\d       Digit [0-9]                                           ║
    ║ \\D       Non-digit                                             ║
    ║ \\w       Word character [a-zA-Z0-9_]                           ║
    ║ \\W       Non-word character                                    ║
    ║ \\s       Whitespace                                            ║
    ║ \\S       Non-whitespace                                        ║
    ╠════════════════════════════════════════════════════════════════╣
    ║ MAIN FUNCTIONS                                                 ║
    ╠════════════════════════════════════════════════════════════════╣
    ║ re.search(pattern, text)     Find FIRST match                  ║
    ║ re.match(pattern, text)      Match at START only               ║
    ║ re.findall(pattern, text)    Find ALL matches (list)           ║
    ║ re.finditer(pattern, text)   Find ALL matches (iterator)       ║
    ║ re.sub(pattern, repl, text)  Find and REPLACE                  ║
    ╠════════════════════════════════════════════════════════════════╣
    ║ GROUPS                                                         ║
    ╠════════════════════════════════════════════════════════════════╣
    ║ (...)           Capturing group                                ║
    ║ (?:...)         Non-capturing group                            ║
    ║ (?P<name>...)   Named group                                    ║
    ║ \\1, \\2         Back-reference to group                        ║
    ╠════════════════════════════════════════════════════════════════╣
    ║ FLAGS                                                          ║
    ╠════════════════════════════════════════════════════════════════╣
    ║ re.IGNORECASE (re.I)    Case-insensitive                       ║
    ║ re.MULTILINE (re.M)     ^ and $ match line boundaries          ║
    ║ re.DOTALL (re.S)        . matches newlines                     ║
    ║ re.VERBOSE (re.X)       Allow comments in pattern              ║
    ╠════════════════════════════════════════════════════════════════╣
    ║ REMEMBER                                                       ║
    ╠════════════════════════════════════════════════════════════════╣
    ║ 1. Always use raw strings: r"pattern"                          ║
    ║ 2. Escape special chars: \\. \\$ \\* \\+ \\? etc.                 ║
    ║ 3. Check if match exists before using .group()                 ║
    ║ 4. Use .*? for non-greedy matching                             ║
    ║ 5. Compile patterns you'll use multiple times                  ║
    ╚════════════════════════════════════════════════════════════════╝
    """
    print(cheat_sheet)


# ============================================================================
# PART 10: PRACTICE EXERCISES
# ============================================================================

def practice_exercises() -> None:
    """
    Practice exercises to test your understanding.
    Try to solve these before running the code!
    """
    
    print("\n" + "="*70)
    print("PRACTICE EXERCISES - Try to solve these!")
    print("="*70)
    
    # Exercise 1: Extract phone numbers
    text1 = "Call me at 555-1234 or 555.5678"
    print("\nExercise 1: Extract all phone numbers")
    print(f"Text: {text1}")
    answer1 = re.findall(r"\d{3}[-.]?\d{4}", text1)
    print(f"Answer: {answer1}")
    
    # Exercise 2: Validate username (alphanumeric, 3-16 chars)
    usernames = ["john", "ab", "user_123", "verylongusername123"]
    print("\nExercise 2: Validate usernames (3-16 alphanumeric)")
    pattern = r"^[a-zA-Z0-9_]{3,16}$"
    for username in usernames:
        valid = bool(re.match(pattern, username))
        print(f"  {username}: {'✓ Valid' if valid else '✗ Invalid'}")
    
    # Exercise 3: Extract domain from email
    email = "john.doe@company.co.uk"
    print(f"\nExercise 3: Extract domain from {email}")
    match = re.search(r"@([\w.-]+)", email)
    domain = match.group(1) if match else None
    print(f"  Domain: {domain}")
    
    # Exercise 4: Replace multiple spaces with single space
    text4 = "Too    many     spaces"
    print(f"\nExercise 4: Fix spacing in '{text4}'")
    fixed = re.sub(r"\s+", " ", text4)
    print(f"  Fixed: '{fixed}'")
    
    # Exercise 5: Extract numbers from mixed text
    text5 = "I have 3 apples, 5 oranges, and 12 bananas"
    print(f"\nExercise 5: Extract numbers from '{text5}'")
    numbers = re.findall(r"\d+", text5)
    print(f"  Numbers: {numbers}")


# ============================================================================
# MAIN EXECUTION - RUN ALL DEMOS
# ============================================================================

def main() -> None:
    """Run all demonstrations."""
    
    print("="*70)
    print("PYTHON RE MODULE - COMPREHENSIVE GUIDE")
    print("="*70)
    
    # Print cheat sheet first
    print_cheat_sheet()
    
    print("\n" + "="*70)
    print("PART 1: BASIC PATTERNS")
    print("="*70)
    demo_basic_patterns()
    
    print("\n" + "="*70)
    print("PART 2: CHARACTER CLASSES")
    print("="*70)
    demo_character_classes()
    
    print("\n" + "="*70)
    print("PART 3: MAIN FUNCTIONS")
    print("="*70)
    demo_main_functions()
    
    print("\n" + "="*70)
    print("PART 4: GROUPS")
    print("="*70)
    demo_groups()
    
    print("\n" + "="*70)
    print("PART 5: FLAGS")
    print("="*70)
    demo_flags()
    
    print("\n" + "="*70)
    print("PART 6: REAL-WORLD EXAMPLES")
    print("="*70)
    # Test real-world functions
    print(f"Email valid: {validate_email('john@email.com')}")
    print(f"Email invalid: {validate_email('invalid.email')}")
    print(f"Phone valid: {validate_phone('555-1234')}")
    print(f"URLs: {extract_urls('Visit https://example.com or http://test.org')}")
    print(f"Hashtags: {extract_hashtags('I love #python and #regex!')}")
    print(f"Masked card: {mask_credit_card('1234-5678-9012-3456')}")
    print(f"Strong password: {validate_password('SecurePass123!')}")
    
    print("\n" + "="*70)
    print("PART 7: COMPILED PATTERNS")
    print("="*70)
    demo_compiled_patterns()
    
    print("\n" + "="*70)
    print("PART 8: COMMON MISTAKES")
    print("="*70)
    demo_common_mistakes()
    
    print("\n" + "="*70)
    print("PART 9: PRACTICE EXERCISES")
    print("="*70)
    practice_exercises()
    
    print("\n" + "="*70)
    print("GUIDE COMPLETE! 🎉")
    print("="*70)
    print("\nTIP: Bookmark this file and use it as reference!")
    print("TIP: Practice with https://regex101.com for interactive testing")


if __name__ == "__main__":
    main()
