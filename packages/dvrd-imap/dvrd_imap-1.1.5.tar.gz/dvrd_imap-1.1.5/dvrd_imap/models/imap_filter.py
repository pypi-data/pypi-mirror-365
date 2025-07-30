from datetime import date

from dvrd_imap.models.exception import IMAPException
from dvrd_imap.models.types import Recipient

_DATE_FILTER_FORMAT = '%d-%b-%Y'


class IMAPFilter:
    def __init__(self, *, from_addr: Recipient = None, not_from_addr: Recipient = None, subject: str = None,
                 not_subject: str = None, to_addr: Recipient = None, no_to_addr: Recipient = None,
                 date_before: date | str = None, date_after: date | str = None, on_date: date | str = None,
                 body: str = None, not_body: str = None, cc: Recipient = None, not_cc: Recipient = None,
                 bcc: Recipient = None, not_bcc: Recipient = None):
        self._from_addr = from_addr
        self._not_from_addr = not_from_addr
        self._subject = subject
        self._not_subject = not_subject
        self._to_addr = to_addr
        self._not_to_addr = no_to_addr
        self._date_before = _ensure_date(date_before)
        self._date_after = _ensure_date(date_after)
        self._on_date = _ensure_date(on_date)
        self._body = body
        self._not_body = not_body
        self._cc = cc
        self._not_cc = not_cc
        self._bcc = bcc
        self._not_bcc = not_bcc
        self._and_filters: list["IMAPFilter"] = list()
        self._or_filters: list["IMAPFilter"] = list()

    def __and__(self, other: "IMAPFilter") -> "IMAPFilter":
        self._and_filters.append(other)
        return self

    def __or__(self, other: "IMAPFilter") -> "IMAPFilter":
        self._or_filters.append(other)
        return self

    @property
    def from_addr(self) -> Recipient | None:
        return self._from_addr

    @from_addr.setter
    def from_addr(self, value: Recipient):
        self._from_addr = value

    @property
    def not_from_addr(self) -> Recipient | None:
        return self._not_from_addr

    @not_from_addr.setter
    def not_from_addr(self, value: Recipient):
        self._not_from_addr = value

    @property
    def subject(self) -> str | None:
        return self._subject

    @subject.setter
    def subject(self, value: str):
        self._subject = value

    @property
    def not_subject(self) -> str | None:
        return self._not_subject

    @not_subject.setter
    def not_subject(self, value: str):
        self._not_subject = value

    @property
    def to_addr(self) -> Recipient | None:
        return self._to_addr

    @to_addr.setter
    def to_addr(self, value: Recipient):
        self._to_addr = value

    @property
    def not_to_addr(self) -> Recipient | None:
        return self._not_to_addr

    @not_to_addr.setter
    def not_to_addr(self, value: Recipient):
        self._not_to_addr = value

    @property
    def date_before(self) -> date | None:
        return self._date_before

    @date_before.setter
    def date_before(self, value: date | str):
        self._date_before = _ensure_date(value)

    @property
    def date_after(self) -> date | None:
        return self._date_after

    @date_after.setter
    def date_after(self, value: date | str):
        self._date_after = _ensure_date(value)

    @property
    def on_date(self) -> date | None:
        return self._on_date

    @on_date.setter
    def on_date(self, value: date | str):
        self._on_date = _ensure_date(value)

    @property
    def body(self) -> str | None:
        return self._body

    @body.setter
    def body(self, value: str):
        self._body = value

    @property
    def not_body(self) -> str | None:
        return self._not_body

    @not_body.setter
    def not_body(self, value: str):
        self._not_body = value

    @property
    def cc(self) -> Recipient | None:
        return self._cc

    @cc.setter
    def cc(self, value: Recipient):
        self._cc = value

    @property
    def not_cc(self) -> Recipient | None:
        return self._not_cc

    @not_cc.setter
    def not_cc(self, value: Recipient):
        self._not_cc = value

    @property
    def bcc(self) -> Recipient | None:
        return self._bcc

    @bcc.setter
    def bcc(self, value: Recipient):
        self._bcc = value

    @property
    def not_bcc(self) -> Recipient | None:
        return self._not_bcc

    @not_bcc.setter
    def not_bcc(self, value: Recipient):
        self._not_bcc = value

    def build(self) -> str:
        filter_parts: list[str] = list()
        if self._from_addr:
            filter_parts.append(_build_recipient_filter(self._from_addr, header_name='FROM'))
        if self._not_from_addr:
            filter_parts.append(f'NOT {_build_recipient_filter(self._not_from_addr, header_name="FROM")}')
        if self._subject:
            filter_parts.append(f'SUBJECT "{self._subject}"')
        if self._not_subject:
            filter_parts.append(f'NOT SUBJECT "{self._not_subject}"')
        if self._to_addr:
            filter_parts.append(_build_recipient_filter(self._to_addr, header_name='TO'))
        if self._not_to_addr:
            filter_parts.append(f'NOT {_build_recipient_filter(self._not_to_addr, header_name="TO")}')
        if self._date_after:
            filter_parts.append(f'SINCE "{self._date_after.strftime(_DATE_FILTER_FORMAT)}"')
        if self._date_before:
            filter_parts.append(f'BEFORE "{self._date_before.strftime(_DATE_FILTER_FORMAT)}"')
        if self._on_date:
            filter_parts.append(f'ON "{self._on_date.strftime(_DATE_FILTER_FORMAT)}')
        if self._body:
            filter_parts.append(f'BODY "{self._body}"')
        if self._not_body:
            filter_parts.append(f'NOT BODY "{self._not_body}"')
        if self._bcc:
            filter_parts.append(_build_recipient_filter(self._bcc, header_name='BCC'))
        if self._not_bcc:
            filter_parts.append(f'NOT {_build_recipient_filter(self._not_bcc, header_name="BCC")}')
        if self._cc:
            filter_parts.append(_build_recipient_filter(self._cc, header_name='CC'))
        if self._not_cc:
            filter_parts.append(f'NOT {_build_recipient_filter(self._not_cc, header_name="CC")}')
        string_filter = " ".join(filter_parts)
        string_filter = self._include_and_filters(string_filter=string_filter)
        string_filter = self._include_or_filters(string_filter=string_filter)
        return string_filter

    def _include_and_filters(self, *, string_filter: str) -> str:
        if not self._and_filters:
            return f'({string_filter})'
        string_filters = [string_filter] + [imap_filter.build() for imap_filter in self._and_filters]
        return f'({" ".join(string_filters)})'

    def _include_or_filters(self, *, string_filter: str) -> str:
        if not self._or_filters:
            return string_filter
        string_filters = [string_filter] + [imap_filter.build() for imap_filter in self._or_filters]
        return f'OR {" ".join(string_filters)}'


def _ensure_date(value: date | str | None) -> date | None:
    if value is None:
        return None
    elif isinstance(value, str):
        try:
            value = date.fromisoformat(value)
        except (TypeError, ValueError) as exc:
            raise IMAPException(f'Date string \'{value}\' is not ISO format') from exc
    return value


def _build_recipient_filter(recipient: Recipient | None, *, header_name: str) -> str | None:
    if recipient is None:
        return None
    elif isinstance(recipient, list):
        split_recipients = _split_recipients(recipients=recipient)
        if len(split_recipients) > 1:
            num_or = len(split_recipients) + 1
        else:
            num_or = 1
        rec_filter = 'OR ' * num_or
        rec_filter += ' '.join([f'{header_name} "{rec}"' for rec in recipient])
        rec_filter = f'({rec_filter})'
    else:
        rec_filter = f'{header_name} "{recipient}"'
    return rec_filter


def _split_recipients(recipients: list[str]) -> list[tuple[str, str] | tuple[str]]:
    split_recipients: list[tuple[str, str] | tuple[str]] = list()
    idx = 0
    while idx < len(recipients):
        first = recipients[idx]
        if idx < len(recipients) - 1:
            split_recipients.append((first, recipients[idx + 1]))
        else:
            split_recipients.append((first,))
        idx += 2
    return split_recipients
