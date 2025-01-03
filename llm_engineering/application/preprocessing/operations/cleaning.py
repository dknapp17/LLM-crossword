import re

from bs4 import BeautifulSoup


def clean_text(text: str) -> str:
    text = re.sub(r"[^\w\s.,!?]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def clean_crossword(text: str) -> str:
    clean_str = ""
    soup = BeautifulSoup(text, "html.parser")
    clue_blocks = soup.select(".numclue > div")
    for block in clue_blocks:
        if len(block.contents) == 2:
            clue = block.contents[0].text
            answer = block.contents[1].text
            clean_str += f"clue: {clue[:-3]} | answer: {answer} <EOT>"
    return clean_str
