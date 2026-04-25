class ContentViolationError(Exception):
    status_code = 400

    def __init__(self, flagged_words):
        self.flagged_words = flagged_words
        super().__init__(f"Inappropriate content detected: {', '.join(flagged_words)}")
