SHIP30_INSTRUCTIONS = """Write a Ship 30 for 30 style article grounded only in the supplied transcript context.
Target 1,100-1,300 words, approximately 1,250. Include a strong hook, clear headings, short paragraphs,
bullets where useful, selective emphasis, and an actionable takeaway. Do not add facts,
guest names, episodes, or claims that are not supported by the context."""


class Ship30Writer:
    target_words = 1250

    def instructions(self) -> str:
        return SHIP30_INSTRUCTIONS

    def prompt_suffix(self) -> str:
        return SHIP30_INSTRUCTIONS
