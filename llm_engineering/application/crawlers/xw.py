from datetime import datetime

import requests
from bs4 import BeautifulSoup
from loguru import logger

from llm_engineering.domain.documents import XWinfoDocument

from .base import BaseCrawler


class XWinfoCrawler(BaseCrawler):
    model = XWinfoDocument

    def __init__(self, ignore=(".git", ".toml", ".lock", ".png")) -> None:
        super().__init__()
        self._ignore = ignore

    def extract(self, link: str, **kwargs) -> None:
        old_model = self.model.find(link=link)
        if old_model is not None:
            logger.info(f"Repository already exists in the database: {link}")

            return

        logger.info(f"Starting scraping xwordinfo site: {link}")

        page = requests.get(link)
        soup = BeautifulSoup(page.content, "html.parser")
        # clue content
        content = str(soup)

        # author
        author_div = soup.find("div", string="Author:")
        author_name = author_div.find_next_sibling("div").text.strip()

        # title/subtitle
        title = f'NYT Puzzle - {link.split("date=")[1]}'  # wont work if link is invalid
        subtitle = f"A NYT puzzle by {author_name}"

        # day of week
        date_string = link.split("date=")[1]  # Format: YYYY-MM-DD
        # Convert string to datetime object
        date_object = datetime.strptime(date_string, "%m/%d/%Y")
        # Get the day of the week (e.g., Sunday, Monday)
        day_of_week = date_object.strftime("%A")

        # put it together
        content = {
            "Title": title,
            "Subtitle": subtitle,
            "Content": content,
            "language": "en",
            "dow": day_of_week,
            "Puzzle Author": author_name,
        }
        user = kwargs["user"]
        instance = self.model(
            content=content,
            link=link,
            platform="xwinfo",
            author_id=user.id,
            author_full_name=user.full_name,
        )
        instance.save()

        logger.info(f"Finished scrapping GitHub repository: {link}")
