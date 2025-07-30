import logging
from imaplib import IMAP4_SSL, IMAP4

from dvrd_imap.models.exception import IMAPException
from dvrd_imap.models.imap_filter import IMAPFilter
from dvrd_imap.models.imap_message import IMAPMessage

_OK_STATUS = 'OK'
_DEFAULT_MESSAGE_PARTS = '(UID RFC822)'

logger = logging.getLogger('dvrd_imap_server')


class IMAPServer:
    def __init__(self, *, host: str, port: int, username: str, password: str, ssl: bool = True,
                 read_only: bool = False, mailbox: str = 'INBOX', default_message_parts: str = _DEFAULT_MESSAGE_PARTS,
                 auto_connect: bool = True):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._ssl = ssl
        self._read_only = read_only
        self._connection: IMAP4_SSL | IMAP4 | None = None
        self._default_message_parts = default_message_parts

        # If mailbox is given, connect directly
        if auto_connect:
            self.connect(mailbox=mailbox)

    def connect(self, mailbox: str = 'INBOX') -> "IMAPServer":
        try:
            if self._ssl:
                self._connection = IMAP4_SSL(host=self._host, port=self._port)
            else:
                self._connection = IMAP4(host=self._host, port=self._port)
            self._connection.login(user=self._username, password=self._password)
            status, _ = self._connection.select(mailbox=mailbox, readonly=self._read_only)
            if status != _OK_STATUS:
                raise IMAPException(f'Unable to select mailbox {mailbox}')
            return self
        except Exception as exc:
            raise IMAPException('Unable to connect to IMAP server') from exc

    def select_mailbox(self, *, mailbox: str, read_only: bool = None) -> "IMAPServer":
        if read_only is not None:
            self._read_only = read_only
        status, _ = self._get_connection().select(mailbox=mailbox, readonly=self._read_only)
        if status != _OK_STATUS:
            raise IMAPException(f'Unable to select mailbox {mailbox}')
        return self

    def fetch_uids(self, *, limit: int = None, filters: str | IMAPFilter = None) -> list[bytes]:
        connection = self._get_connection()
        if not filters:
            filters = 'ALL'
        filters = _filter_to_string(filters)
        status, data = connection.uid('search', '', filters)
        if status != _OK_STATUS:
            raise IMAPException('Fetching UIDs failed')
        email_ids = data[0].split()
        if limit is not None:
            start = min(len(email_ids), limit)
            email_ids = email_ids[-1:-(start + 1):-1]
        return email_ids

    def fetch_unseen(self, limit: int = None, include_raw_message: bool = False, message_parts: str = None):
        return self.fetch(limit=limit, filters='UNSEEN', include_raw_message=include_raw_message,
                          message_parts=message_parts)

    def fetch(self, *, limit: int = None, filters: str | IMAPFilter = None, include_raw_message: bool = False,
              message_parts: str = None) -> list[IMAPMessage]:
        if not message_parts:
            message_parts = self._default_message_parts
        email_ids = self.fetch_uids(limit=limit, filters=filters)
        return [self.fetch_email(uid=uid, include_raw_message=include_raw_message, message_parts=message_parts) for uid
                in email_ids]

    def fetch_email(self, uid: bytes, include_raw_message: bool = False, message_parts: str = None) -> IMAPMessage:
        if not message_parts:
            message_parts = self._default_message_parts
        status, data = self._get_connection().uid('fetch', uid, message_parts)
        if status != _OK_STATUS:
            raise IMAPException(f'Could not fetch email with uid {uid}')
        return IMAPMessage.parse_message(message=data, include_raw=include_raw_message)

    def close(self):
        if not self._connection:
            return
        self._connection.close()
        self._connection.logout()
        self._connection = None

    def _get_connection(self) -> IMAP4_SSL | IMAP4:
        if not self._connection:
            raise IMAPException('Not connected to IMAP server yet. Use `connect()` to establish a connection first, '
                                'or use `auto_connect=True` to automatically connect to the server.')
        return self._connection

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def _filter_to_string(filters: str | IMAPFilter):
    if isinstance(filters, IMAPFilter):
        return filters.build()
    return filters
