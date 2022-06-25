import csv
import pandas as pd
from datetime import datetime


msg_p2p = "Messages and calls are end-to-end encrypted. No one outside of this chat, not even WhatsApp, can read or listen to them."
msg_deleted = "This message was deleted."
msg_video = "video omitted"
wa_messages = [msg_p2p, msg_deleted, msg_video]


def processLink(_text):
    """Format links to keep only domain.de/domain.com."""
    if "http" not in _text:
        return _text

    _split = _text.split(" ")
    _out = []
    for _link in _split:
        if "http" not in _link:
            _out += [_link]
            continue

        if "//www." in _link or "//m." in _link \
                or "//mobile." in _link:
            _split2 = _link.split(".")
            _out += [_split2[1] + "."
                     + _split2[2].split("/")[0]]
        else:
            _split2 = _link.split("/")
            _out += [_split2[2]]

    return " ".join(_out)


def readChat(filename):
    """Read whatsapp chat, clean lines, return df."""
    # TODO: abbreviate links
    times, authors, text = [], [], []
    with open(filename, "r") as _f:
        data = csv.reader(_f, delimiter=" ")
        for row in data:
            if not len(row) or not len(row[0]):
                continue

            row[0] = row[0].split("\u200e")[-1]
            if row[0][0].startswith("["):
                colonSep = " ".join(row).split(": ")

                # Remove attachment posts and whatsapp notifications
                if len(colonSep) == 1 or colonSep[1].endswith("attached") or \
                        any(": ".join(colonSep[1:]).endswith(msg)
                            for msg in wa_messages):
                    continue

                times += [datetime.strptime(
                          " ".join([row[0][1:-1], row[1][:-1]]),
                          "%d.%m.%y %H:%M:%S")]
                authors += [colonSep[0].split("] ")[1]]
                _text = processLink(": ".join(colonSep[1:]))
                text += [_text]

            else:
                text[-1] += processLink(" ".join(row))

    _dict = {"timestamp": times, "author": authors, "text": text}
    return pd.DataFrame(_dict)


if __name__ == '__main__':
    data = readChat("data/_chat.txt")
    print(data)
