import os
import re

import pydle
import requests
from bs4 import BeautifulSoup

MEDIAWIKI_URL = os.environ.get("MEDIAWIKI_URL")
LGNAME = os.environ.get("LGNAME")
LGPASSWORD = os.environ.get("LGPASSWORD")
WIKI_URL = os.environ.get("WIKI_URL")

ETHERPAD_DOMAIN = "https://etherpad.indieweb.org"
HEADERS = {"User-Agent": "indieweb etherpad archiver"}

WIKI_PAGE_HEADER = """
'''<dfn>[{event_link} {event_name}]</dfn>''' was an IndieWeb meetup on Zoom held on {date}.

* Archived from: {etherpad_url}
"""

CATEGORIES_REGISTER = {
    "front-end-study-hall": "[[Category:Front_end]]\n{{Front End Study Hall|date={date}}}\n",
    "-photos-": "[[Category:Photos]]",
    "-writing-": "[[Category:Writing]]",
    "-hwc-": "{{Homebrew Website Club}}",
}

session = requests.Session()


def login_to_mediawiki():
    response = session.get(
        MEDIAWIKI_URL + "?action=query&meta=tokens&type=login&format=json"
    )

    login_data = {
        "action": "login",
        "lgname": LGNAME,
        "lgpassword": LGPASSWORD,
        "lgtoken": response.json()["query"]["tokens"]["logintoken"],
        "format": "json",
    }

    response = session.post(MEDIAWIKI_URL, data=login_data).text


def get_csrf_token():
    csrf_data = {"action": "query", "meta": "tokens", "format": "json"}

    return session.post(MEDIAWIKI_URL, data=csrf_data).json()["query"]["tokens"][
        "csrftoken"
    ]


def get_etherpad_contents(source_url):
    etherpad_url = None
    if source_url.startswith("https://events.indieweb.org"):
        events_page = requests.get(source_url, headers=HEADERS)
        page = BeautifulSoup(events_page.text, "lxml")
        links = page.find_all("a")
        for link in links:
            if link.get("href", "").startswith(ETHERPAD_DOMAIN):
                etherpad_url = link.get("href")
        event_name = page.select(".p-name")[0]
    elif source_url.startswith(ETHERPAD_DOMAIN):
        etherpad_url = source_url
    else:
        return None

    if not etherpad_url:
        return None

    etherpad_contents_url = etherpad_url + "/export/txt"

    etherpad_contents = requests.get(etherpad_contents_url).text

    etherpad_slug = etherpad_url.split(ETHERPAD_DOMAIN + "/")[-1]

    date = etherpad_slug[:10]

    etherpad_contents = WIKI_PAGE_HEADER.format(
        event_link=source_url,
        event_name=event_name,
        date=date,
        etherpad_url=etherpad_url,
    ) + "\n" + etherpad_contents

    etherpad_contents += """
[[Category:Events]]"""

    for pattern, category in CATEGORIES_REGISTER.items():
        if pattern in etherpad_url:
            etherpad_contents += category.format(date=date).replace("{", "{{").replace("}", "}}") + "\n"

    return etherpad_contents, etherpad_slug


def create_wiki_page(csrf_token, body, title):
    page_data = {
        "action": "edit",
        "format": "json",
        "title": "events/" + title.strip("/"),
        "text": body,
        "token": csrf_token,
        "summary": "Created event page using IndieWeb events / Etherpad archiver",
    }

    result = session.post(MEDIAWIKI_URL, data=page_data).text


class Bot(pydle.Client):
    async def on_connect(self):
        await self.join("#indieweb-meta")
        await self.join("#indieweb-events")

    async def on_message(self, target, source, message):
        if re.match("<(.*)>", message):
            message = message.replace(re.match("<(.*)>", message).group(0), "").strip()
        if source != self.nickname and message.startswith("!archive"):
            if message.strip() == "!archive help":
                await self.message(
                    target, "Usage: !archive <event page URL>"
                )
                return

            login_to_mediawiki()

            event_url = message.split(" ")[1]

            csrf_token = get_csrf_token()
            etherpad_contents, etherpad_slug = get_etherpad_contents(event_url)

            if (
                requests.get(
                    "https://indieweb.org/events/" + etherpad_slug.strip("/")
                ).status_code
                == 200
            ):
                await self.message(target, "These notes have already been archived.")
                return

            create_wiki_page(csrf_token, etherpad_contents, etherpad_slug)
            await self.message(
                target,
                f"Created https://indieweb.org/events/{etherpad_slug.strip('/')}. Please review the page to ensure the document is correctly formatted and remove any unnecessary text.",
            )


# login_to_mediawiki()
# csrf_token = get_csrf_token()
# etherpad_contents, etherpad_slug = get_etherpad_contents(
#     "https://events.indieweb.org/2026/02/homebrew-website-club-eastern-EogbHvI1u8rI"
# )
# # create_wiki_page(csrf_token, etherpad_contents, etherpad_slug)
client = Bot("iwc-archive-bot", realname="iwc-archive-bot")
client.run("irc.libera.chat", tls=True, tls_verify=False)
