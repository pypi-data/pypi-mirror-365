import email
import re
from datetime import datetime
from email.header import decode_header
from email.message import Message
from email.utils import parseaddr
from typing import Any

import chardet

from dvrd_imap.models.exception import IMAPException
from dvrd_imap.models.types import Address


class IMAPMessage:
    @staticmethod
    def parse_message(message: Any, include_raw: bool = False) -> "IMAPMessage":
        message_string = _string_message_from_message(message=message)
        uid_string = _string_uid_from_message(message=message)
        email_message = email.message_from_string(message_string)
        uid = None
        raw_content = None
        if uid_list := re.findall(r'[UID ](\d+)', uid_string):
            uid = uid_list[0]
        if include_raw:
            raw_content = message[0][1]
        return IMAPMessage(message=email_message, uid=uid, raw_content=raw_content)

    def __init__(self, message: Message, uid: bytes = None, raw_content: str = None):
        self._message = message
        self._uid = uid
        self._raw_content = raw_content

    @property
    def message(self) -> Message:
        return self._message

    @property
    def uid(self) -> int | None:
        return self._uid

    @property
    def subject(self) -> str:
        return _decode_header(self._message.get('Subject'))

    @property
    def to_addr_raw(self) -> str:
        return _decode_header(self._message.get('To'))

    @property
    def to_addr_list(self) -> list[str]:
        return _addresses_to_list(addresses=self.to_addr_raw)

    @property
    def to_addr(self) -> list[Address]:
        addresses = self.to_addr_list
        return [parseaddr(addr) for addr in addresses]

    @property
    def from_addr_raw(self):
        return _decode_header(self._message.get('From'))

    @property
    def from_addr(self) -> Address:
        return parseaddr(self.from_addr_raw)

    @property
    def sender_raw(self):
        return _decode_header(self._message.get('Sender'))

    @property
    def sender(self) -> Address:
        return parseaddr(self.sender_raw)

    @property
    def cc_raw(self):
        return _decode_header(self._message.get('CC'))

    @property
    def cc_list(self) -> list[str]:
        return _addresses_to_list(addresses=self.cc_raw)

    @property
    def cc(self) -> list[Address]:
        return [parseaddr(cc) for cc in self.cc_list]

    @property
    def delivered_to_raw(self):
        return _decode_header(self._message.get('Delivered-To'))

    @property
    def delivered_to(self) -> Address:
        return parseaddr(self.delivered_to_raw)

    @property
    def content_type(self):
        return _decode_header(self._message.get('Content-Type'))

    @property
    def content_transfer_encoding(self):
        return _decode_header(self._message.get('Content-Transfer-Encoding'))

    @property
    def references(self):
        return _decode_header(self._message.get('References'))

    @property
    def references_list(self) -> list[str]:
        strip_chars = r'\r|\n|\t|\'|"'
        ref = re.sub(strip_chars, '', self.references)
        return [ref for ref in ref.split(' ')]

    @property
    def in_reply_to_raw(self):
        return _decode_header(self._message.get('In-Reply-To'))

    @property
    def in_reply_to(self) -> Address:
        return parseaddr(self.in_reply_to_raw)

    @property
    def reply_to_raw(self):
        return _decode_header(self._message.get('Reply-To'))

    @property
    def reply_to(self) -> Address:
        return parseaddr(self.reply_to_raw)

    @property
    def return_path(self):
        return _decode_header(self._message.get('Return-Path'))

    @property
    def mime_version(self):
        return _decode_header(self._message.get('MIME-Version'))

    @property
    def message_id(self):
        return _decode_header(self._message.get('Message-ID'))

    @property
    def date_raw(self) -> str:
        return _decode_header(self._message.get('Date'))

    @property
    def date(self) -> datetime:
        date_raw = re.sub(r'\([A-Z]+\)', '', self.date_raw).strip()
        return datetime.strptime(date_raw, '%a, %d %b %Y %H:%M:%S %z')

    @property
    def raw_content(self):
        return self._raw_content

    @property
    def body(self) -> str:
        for part in self._message.walk():
            maintype = part.get_content_maintype()
            if maintype != 'multipart' and not part.get_filename():
                return _decode_body(part)
            if maintype == 'multipart':
                for p in part.get_payload():
                    if p.get_content_maintype() == 'text':
                        return _decode_body(p)
        raise IMAPException('Unable to retrieve body from message', message=self)

    @property
    def attachments(self):
        attachments = []
        for part in self._message.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if not (filename := part.get_filename()):
                continue
            data = part.get_payload(decode=True)
            if not data:
                continue
            content_type = part.get_content_type()
            attachments.append((filename, data, content_type))
        return attachments

    def __str__(self):
        template = "{date}", "{sender}", "{title}"
        represent = " || ".join(template).format(
            date=self.date,
            sender=self.sender or self.from_addr,
            title=self.subject
        )
        return represent

    def __repr__(self):
        return str(self)


def _decode_header(data: Any) -> str:
    if data is None:
        return ''
    decoded_headers = decode_header(data)
    headers = []
    for decoded_str, charset in decoded_headers:
        if isinstance(decoded_str, str):
            headers.append(decoded_str)
        elif charset:
            headers.append(str(decoded_str, charset))
        else:
            if encoding := chardet.detect(decoded_str).get('encoding'):
                headers.append(str(decoded_str, encoding))
            else:
                headers.append(decoded_str)
    return ''.join(headers)


def _decode_body(part) -> str:
    charset = str(part.get_content_charset())
    payload = part.get_payload(decode=True)
    try:
        body = str(payload, charset) if charset else part.get_payload()
    except:
        if encoding := chardet.detect(payload).get('encoding'):
            body = str(payload, encoding)
        else:
            body = payload
    return body


def _string_message_from_message(message: Any) -> str:
    string_or_bytes_message = message[0][1]
    if not isinstance(string_or_bytes_message, str):
        if encoding := chardet.detect(string_or_bytes_message).get('encoding'):
            string_or_bytes_message = string_or_bytes_message.decode(encoding)
        else:
            string_or_bytes_message = string_or_bytes_message.decode()
    return string_or_bytes_message


def _string_uid_from_message(message: Any) -> str:
    string_or_bytes_uid = message[0][0]
    if not isinstance(string_or_bytes_uid, str):
        encoding = chardet.detect(string_or_bytes_uid).get('encoding')
        string_or_bytes_uid = string_or_bytes_uid.decode(encoding)
    return string_or_bytes_uid


def _addresses_to_list(addresses: str) -> list[str]:
    strip_chars = r'\r|\n|\t|\'|"'
    address_list: list[str] = list()
    for address in addresses.split(','):
        remaining_address = re.sub(strip_chars, '', address).strip()
        if remaining_address:
            address_list.append(remaining_address)
    return address_list
