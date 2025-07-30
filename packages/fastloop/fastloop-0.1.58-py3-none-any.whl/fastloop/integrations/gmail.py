import asyncio
import base64
import email
import imaplib
import uuid
from datetime import datetime
from email.header import decode_header
from typing import TYPE_CHECKING, Any

from ..logging import setup_logger
from ..loop import LoopEvent, LoopState
from ..types import IntegrationType
from . import Integration

if TYPE_CHECKING:
    from ..fastloop import FastLoop

logger = setup_logger(__name__)


class GmailReceivedEvent(LoopEvent):
    type: str = "gmail_received"
    message_id: str
    from_email: str
    to_email: str
    subject: str
    body: str
    html_body: str | None = None
    received_at: float
    headers: dict[str, str]
    attachments: list[dict[str, Any]] | None = None
    uid: str


class GmailIntegration(Integration):
    def __init__(
        self,
        *,
        email_address: str,
        app_password: str,
        poll_interval: int = 30,
    ):
        super().__init__()

        self.email_address = email_address
        self.app_password = app_password
        self.poll_interval = poll_interval

        # Track processed emails
        self.processed_uids: set[str] = set()
        self.imap_task: asyncio.Task[None] | None = None

    def type(self) -> IntegrationType:
        return IntegrationType.GMAIL

    def register(self, fastloop: "FastLoop", loop_name: str) -> None:
        fastloop.register_events([GmailReceivedEvent])

        self._fastloop: FastLoop = fastloop
        self.loop_name: str = loop_name

        # Start IMAP polling
        self.imap_task = asyncio.create_task(self._start_imap_polling())

    async def _start_imap_polling(self):
        """Start polling Gmail for new emails"""
        while True:
            try:
                await self._check_for_new_emails()
                await asyncio.sleep(self.poll_interval)
            except Exception as e:
                logger.error(f"Error in Gmail polling: {e}")
                await asyncio.sleep(self.poll_interval)

    async def _check_for_new_emails(self):
        """Check for new emails via Gmail IMAP"""
        loop = asyncio.get_event_loop()

        def _fetch_emails():
            imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
            imap.login(self.email_address, self.app_password)
            imap.select("INBOX")

            # Search for unread emails
            _, message_numbers = imap.search(None, "UNSEEN")

            emails = []
            for num in message_numbers[0].split():
                _, msg_data = imap.fetch(num, "(RFC822)")
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)

                # Get UID for tracking
                _, uid_data = imap.fetch(num, "(UID)")
                uid = uid_data[0].decode().split()[2].rstrip(")")

                emails.append((uid, email_message))

            imap.close()
            imap.logout()
            return emails

        try:
            emails = await loop.run_in_executor(None, _fetch_emails)

            for uid, email_message in emails:
                if uid not in self.processed_uids:
                    await self._process_email(uid, email_message)
                    self.processed_uids.add(uid)

        except Exception as e:
            logger.error(f"Error fetching emails: {e}")

    async def _process_email(self, uid: str, email_message):
        """Process a single email message"""
        # Extract email data
        from_email = self._decode_email_header(email_message.get("From", ""))
        to_email = self._decode_email_header(email_message.get("To", ""))
        subject = self._decode_email_header(email_message.get("Subject", ""))
        message_id = email_message.get("Message-ID", str(uuid.uuid4()))
        date_str = email_message.get("Date", "")

        # Parse date
        try:
            date_tuple = email.utils.parsedate_to_datetime(date_str)
            received_at = date_tuple.timestamp()
        except BaseException:
            received_at = datetime.now().timestamp()

        # Extract body and attachments
        body, html_body, attachments = self._parse_email_parts(email_message)

        # Create headers dict
        headers = dict(email_message.items())

        # Create event
        email_event = GmailReceivedEvent(
            loop_id=None,
            message_id=message_id,
            from_email=from_email,
            to_email=to_email,
            subject=subject,
            body=body,
            html_body=html_body,
            received_at=received_at,
            headers=headers,
            attachments=attachments,
            uid=uid,
        )

        # Get loop event handler
        loop_event_handler = self._fastloop.loop_event_handlers.get(self.loop_name)
        if loop_event_handler:
            mapped_request = email_event.to_dict()
            loop: LoopState = await loop_event_handler(mapped_request)
            if loop.loop_id:
                await self._fastloop.state_manager.set_loop_mapping(
                    f"gmail_thread:{message_id}", loop.loop_id
                )

    def _decode_email_header(self, header: str) -> str:
        """Decode email header properly"""
        if not header:
            return ""

        decoded_parts = decode_header(header)
        result = ""
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                if encoding:
                    result += part.decode(encoding)
                else:
                    result += part.decode("utf-8", errors="ignore")
            else:
                result += str(part)
        return result

    def _parse_email_parts(
        self, email_message
    ) -> tuple[str, str | None, list[dict[str, Any]]]:
        """Parse email body and attachments"""
        body = ""
        html_body = None
        attachments = []

        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))

                if "attachment" in content_disposition:
                    # Handle attachment
                    filename = part.get_filename()
                    if filename:
                        filename = self._decode_email_header(filename)
                        attachment_data = part.get_payload(decode=True)
                        attachments.append(
                            {
                                "filename": filename,
                                "content_type": content_type,
                                "size": len(attachment_data) if attachment_data else 0,
                                "data": base64.b64encode(attachment_data).decode()
                                if attachment_data
                                else "",
                            }
                        )
                else:
                    # Handle body
                    payload = part.get_payload(decode=True)
                    if payload:
                        text = payload.decode(
                            part.get_content_charset() or "utf-8", errors="ignore"
                        )
                        if content_type == "text/html":
                            html_body = text
                        elif content_type == "text/plain":
                            body = text
        else:
            # Simple email
            payload = email_message.get_payload(decode=True)
            if payload:
                body = payload.decode(
                    email_message.get_content_charset() or "utf-8", errors="ignore"
                )

        return body, html_body, attachments

    def events(self) -> list[Any]:
        return [GmailReceivedEvent]

    async def emit(self, event: Any) -> None:
        # This integration only receives emails, doesn't send them
        logger.info(f"Gmail integration received event: {event}")

    async def cleanup(self):
        """Cleanup resources"""
        if self.imap_task:
            self.imap_task.cancel()
            try:
                await self.imap_task
            except asyncio.CancelledError:
                pass


def get_gmail_app_password_instructions() -> str:
    """Get instructions for setting up Gmail app password"""
    return """
Gmail App Password Setup:
========================

1. Go to https://myaccount.google.com/
2. Click "Security" in the left sidebar
3. Under "Signing in to Google", click "2-Step Verification"
   - If not enabled, enable it first
4. Scroll down and click "App passwords"
5. Select "Mail" from the dropdown
6. Click "Generate"
7. Copy the 16-character password (like: abcd efgh ijkl mnop)
8. Use this password in your FastLoop configuration

Note: This is NOT your regular Gmail password!
"""
