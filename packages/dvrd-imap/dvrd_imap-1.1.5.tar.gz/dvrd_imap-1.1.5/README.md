# dvrd_imap

Object oriented wrapper for the built-in imaplib.

## Example

```python
from dvrd_imap import IMAPServer, IMAPFilter, IMAPMessage

host = 'imap.example.domain'
port = 993
username = 'example@domain.com'
password = 'examplePass123'

with IMAPServer(host=host, port=port, username=username, password=password) as imap_server:
    filters = IMAPFilter(subject='Example subject')
    messages: list[IMAPMessage] = imap_server.fetch(filters=filters, limit=10)
```

## IMAPServer

Instantiate this object to connect to the IMAP server and use the server for further actions. It is recommended to
use `IMAPServer` as a context manager to ensure the connection is closed properly.

### Properties

| **Prop**                | **Type** | **Required** | **Description**                                                                                                                            |
|-------------------------|----------|--------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| `host`                  | str      | yes          | IMAP server host                                                                                                                           |
| `port`                  | int      | yes          | IMAP server port                                                                                                                           |
| `username`              | str      | yes          | Used to login to the IMAP server                                                                                                           |
| `password`              | str      | yes          | Used to login to the IMAP server                                                                                                           |
| `ssl`                   | bool     | no           | If True (default), uses IMAP4_SSL. If False, uses IMAP4                                                                                    |
| `read_only`             | bool     | no           | If True, operate in readonly mode.  Mails are not marked as 'seen' in readonly mode.  Defaults to False.                                   |
| `mailbox`               | str      | no           | Initial mailbox to connect to, defaults to 'INBOX'                                                                                         |
| `default_message_parts` | str      | no           | Parts of the email that are retrieved. Defaults to ('UID RFC822')                                                                          |
| `auto_connect`          | bool     | no           | If False, IMAPServer does not automatically login. For further actions, the 'connect()' function must be called to establish a connection. |

### Functions

| **Function**     | **Parameters**                                                                                                                                     | **Returns**       | **Description**                                                                                                                                                                                                               |
|------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|-------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `connect`        | `mailbox`: str (optional)                                                                                                                          | IMAPServer        | Login to the IMAPServer and connect to the specified mailbox (default 'INBOX'). Use this function only with property `auto_connect=False`.                                                                                    |
| `select_mailbox` | `mailbox`: str <br/>`read_only`: bool (optional)                                                                                                   | IMAPServer        | Connect to the specified mailbox.  Use the `read_only` parameter to optionally override the class' default.                                                                                                                   |
| `fetch_uids`     | `limit`: int (optional)<br/>`filters`: str \| IMAPFilter (optional)                                                                                | list[bytes]       | Fetches UID's from the server using the specified filters. Returns up to `limit` UID's. If `filters` is None, uses filter `(ALL)`.                                                                                            |
| `fetch`          | `limit`: int (optional)<br/>`filters`: str \| IMAPFilter (optional)<br/>`include_raw_message`: bool (optional)<br/>`message_parts`: str (optional) | list[IMAPMessage] | Fetches the specified message parts (see the `default_message_parts` prop) of up to `limit` mails that match the specified filters. Use `include_raw_message=True` to include the original IMAP data in the returned objects. |
| `fetch_mail`     | `uid`: bytes<br/>`include_raw_message`: bool (optional)<br/>`message_parts`: str (optional)                                                        | IMAPMessage       | Fetch a specific email from the server. Raises an IMAPException if the email does not exist.                                                                                                                                  |
| `close`          | -                                                                                                                                                  | -                 | Closes the IMAP connection.                                                                                                                                                                                                   |

## IMAPMessage

The `IMAPMessage` class is used to wrap the actual IMAP message's data. It gives easy access to header values,
attachments, and content. If the parameter `include_raw_message` in any of the server methods is `True`, the original (
raw) data can be accessed using the property `raw_content`.

## Filtering

Filtering can be done by using `IMAPFilter` objects. Multiple filter objects can be combined using the logical
'and' / 'or' (`&` / `|`) operators. See the table below for all possible filter fields. Using the `IMAPFilter` object is
recommended, but not required. It is also possible to filter using a custom string.

The generated IMAP filter can be inspected / debugged by using the `build()` function of `IMAPFilter`. This is also
internally used by the `IMAPServer` to construct the filter string.

### Examples

```python
from dvrd_imap import IMAPFilter

# Get mails received on a specific date, specifying the date as ISO string
imap_filter = IMAPFilter(on_date='2024-02-15')
# (ON "15-Feb-2024)

# Get mails filtered on sender and send date, specifying the date as `date` object
from datetime import date

imap_filter = IMAPFilter(from_addr='exampe@domain.com', date_after=date.fromisoformat('2024-02-10'))
# (FROM "exampe@domain.com" SINCE "10-Feb-2024")

# Get mails from a list of senders
imap_filter = IMAPFilter(from_addr=['example1@domain.com', 'example2@domain2.com'])
# ((OR FROM "example1@domain.com" FROM "example2@domain2.com"))

# Get mails sent from a specific domain
imap_filter = IMAPFilter(from_addr='domain.com')
# (FROM "domain.com")

# Combine filters, generates an OR construct
imap_filter = IMAPFilter(from_addr='example@domain.com', date_after='2024-02-01') | IMAPFilter(
    from_addr='example@domain2.com', date_before='2024-02-01')
# OR (FROM "example@domain.com" SINCE "01-Feb-2024") (FROM "example@domain2.com" BEFORE "01-Feb-2024")
```

### Filter fields

All filter fields are optional.

| **Field**     | **Type**           | **Description**                                            |
|---------------|--------------------|------------------------------------------------------------|
| from_addr     | `str \| list[str]` | Mails sent by given sender(s)                              |
| not_from_addr | `str \| list[str]` | Mails not sent by given sender(s)                          |
| subject       | `str`              |                                                            |
| not_subject   | `str`              |                                                            |
| to_addr       | `str \| list[str]` | Recipient(s)                                               |
| no_to_addr    | `str \| list[str]` |                                                            |
| date_before   | `str \| date`      | Mails sent before given date, string must be in ISO format |
| date_after    | `str \| date`      | Mails sent after given date, string must be in ISO format  |
| on_date       | `str \| date`      | Mails sent on given date, string must be in ISO format     |
| body          | `str`              | Search content of mail                                     |
| not_body      | `str`              |                                                            |
| cc            | `str \| list[str]` | Mails sent to CC address(es)                               |
| not_cc        | `str \| list[str]` | Mails not sent to CC address(es)                           |
| bcc           | `str \| list[str]` | Mails sent to BCC address(es)                              |
| not_bcc       | `str \| list[str]` | Mails not sent to BCC address(es)                          |