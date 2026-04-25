class ContentViolationError(Exception):
    status_code = 400

    def __init__(self, flagged_words):
        self.flagged_words = flagged_words
        super().__init__(f"Inappropriate content detected: {', '.join(flagged_words)}")


class ContentModerationService:
    BLOCKED_WORDS = [
        "hate", "kill", "murder", "rape", "fuck", "shit", "bitch", "bastard",
        "asshole", "damn", "cunt", "dick", "cock", "pussy", "nigger", "faggot",
        "whore", "slut", "retard", "nazi", "terrorist", "bomb", "suicide",
        "violence", "abuse", "porn", "explicit",
    ]

    def check_text(self, text: str) -> list[str]:
        lower = text.lower()
        return [word for word in self.BLOCKED_WORDS if word in lower]

    def validate(self, *texts: str) -> list[str]:
        found = []
        for text in texts:
            for word in self.check_text(text):
                if word not in found:
                    found.append(word)
        return found
