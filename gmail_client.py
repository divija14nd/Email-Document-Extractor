import base64
from datetime import datetime, timezone


def iter_pdf_attachments(service, query):
    user_id = "me"
    request = service.users().messages().list(userId=user_id, q=query)
    while request is not None:
        response = request.execute()
        for msg_meta in response.get("messages", []):
            message = service.users().messages().get(userId=user_id, id=msg_meta["id"]).execute()
            received_at = _message_date(message)
            sender = _message_sender(message)
            for filename, pdf_bytes in _walk_parts(service, user_id, message["id"], message.get("payload", {})):
                yield filename, pdf_bytes, received_at, sender
        request = service.users().messages().list_next(previous_request=request, previous_response=response)


def _message_date(message):
    internal_date_ms = int(message.get("internalDate", 0))
    return datetime.fromtimestamp(internal_date_ms / 1000, tz=timezone.utc)


def _message_sender(message):
    headers = message.get("payload", {}).get("headers", [])
    for header in headers:
        if header.get("name", "").lower() == "from":
            return header.get("value", "")
    return ""


def _walk_parts(service, user_id, message_id, part):
    filename = part.get("filename", "")
    if filename.lower().endswith(".pdf"):
        body = part.get("body", {})
        attachment_id = body.get("attachmentId")
        if attachment_id:
            attachment = service.users().messages().attachments().get(
                userId=user_id, messageId=message_id, id=attachment_id
            ).execute()
            data = attachment["data"]
        else:
            data = body.get("data")
        if data:
            pdf_bytes = base64.urlsafe_b64decode(data.encode("utf-8"))
            yield filename, pdf_bytes

    for subpart in part.get("parts", []) or []:
        yield from _walk_parts(service, user_id, message_id, subpart)
