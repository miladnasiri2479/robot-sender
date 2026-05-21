from typing import Dict, Any

def normalize_soroush_message(msg: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes a Soroush Plus message payload into a standard format.
    Standard Format:
    {
        "id": "original_id",
        "type": "text" | "image" | "video" | "file",
        "text": "optional caption or body",
        "file_url": "optional url for media"
    }
    """
    msg_id = str(msg.get("id"))
    msg_type = msg.get("type", "TEXT").upper()
    body = msg.get("body", "")
    file_url = msg.get("fileUrl")

    normalized = {
        "id": msg_id,
        "text": body,
        "type": "text"
    }

    if msg_type == "IMAGE":
        normalized["type"] = "image"
        normalized["file_url"] = file_url
    elif msg_type == "VIDEO":
        normalized["type"] = "video"
        normalized["file_url"] = file_url
    elif msg_type == "FILE" or msg_type == "PUSH_TO_TALK":
        normalized["type"] = "file"
        normalized["file_url"] = file_url
    
    return normalized
