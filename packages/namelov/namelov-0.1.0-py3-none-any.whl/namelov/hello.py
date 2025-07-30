# Example letter to adjective mapping. You can expand/modify this!
LETTER_ADJECTIVES = {
    'A': "Awesome",
    'B': "Brilliant",
    'C': "Creative",
    'D': "Diligent",
    'E': "Excellent",
    'F': "Fantastic",
    'G': "Generous",
    'H': "Honest",
    'I': "Inspiring",
    'J': "Joyful",
    'K': "Kind",
    'L': "Lively",
    'M': "Motivated",
    'N': "Noble",
    'O': "Outstanding",
    'P': "Passionate",
    'Q': "Quick-witted",
    'R': "Radiant",
    'S': "Smart",
    'T': "Talented",
    'U': "Unique",
    'V': "Valiant",
    'W': "Wise",
    'X': "Xenodochial",
    'Y': "Youthful",
    'Z': "Zealous",
}

def hello(name: str) -> str:
    if name:
        # Compose "Hello <name>!" part
        greeting = f"Hello {name}!\nLet me describe your Lovely name:"
        lines = []
        # For each letter, find the adjective
        for letter in name:
            adjective = LETTER_ADJECTIVES.get(letter.upper(), "Wonderful")
            lines.append(f"{letter.upper()} is for {adjective}")
        # Combine all
        description = "\n".join(lines)
        return f"{greeting}\n{description}"
    else:
        return "Can I know your Name?"