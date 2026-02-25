# IndieWeb Etherpad Archiver (Cali)

A tool that accepts an [IndieWeb Events](https://events.indieweb.org) page and archives the associated Etherpad page to the [IndieWeb wiki](https://indieweb.org).

> [!NOTE]  
> This project replaced https://github.com/capjamesg/indieweb-etherpad-archiver, which was a Perl program that was relatively had to maintain.

## IRC Usage

This tool provides an interface over IRC through which an Etherpad page linked to an IndieWeb events page can be archived.

To archive a document using the bot, you can use the following command in the IRC channel to which the archiver is connected:

```
!archive <events_page_url> <example/page> - Archive an events.indieweb.org page, save to example/page
!archive help - Show help
```

## Getting Started

To use this project, first install the required dependencies:

```
git clone https://github.com/capjamesg/indieweb-etherpad-archiver-v2
cd indieweb-etherpad-archiver-v2
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

Next, register a *bot account* on the MediaWiki to which you want to save archives. This will give you the credentials you need for the next step. Take note of the bot username and password MediaWiki provides.

Once you have your bot account credentials, create a .env file and add the following values:

    LGNAME=MEDIAWIKI_LOGIN_NAME
    LGPASS=MEDIAWIKI_LOGIN_PASSWORD
    WIKI_URL=LINK_TO_MEDIAWIKI_API

You will need to set your IRC network and channel names in the `app.py` file.

All of these values are required.

Next, run the archiver script:

```
python3 app.py
```

The archiver script will connect to the provided IRC channel and expose the !archive command for use in the chat.

## Technology

This project was built using Python.

## License

This project is licensed under an [MIT 0 license](LICENSE).

## Contributing

Have an idea on how to improve the archiver? Feel free to open an issue or pull request in this repository.

## Contributors

- capjamesg
