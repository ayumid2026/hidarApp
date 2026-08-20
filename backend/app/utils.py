import africastalking
from app.config import settings

# Initialize Africa's Talking (only if credentials are set)
if settings.AFRICASTALKING_USERNAME and settings.AFRICASTALKING_API_KEY:
    africastalking.initialize(settings.AFRICASTALKING_USERNAME, settings.AFRICASTALKING_API_KEY)
    sms = africastalking.SMS
else:
    sms = None

async def send_sms(phone_number: str, message: str) -> dict:
    """Send SMS via Africa's Talking (if configured)."""
    if not sms:
        return {"success": False, "error": "SMS service not configured"}
    try:
        if not phone_number.startswith("+"):
            phone_number = "+251" + phone_number.lstrip("0")
        response = sms.send(message, [phone_number], sender_id=settings.SMS_SENDER_ID)
        return {"success": True, "response": response}
    except Exception as e:
        return {"success": False, "error": str(e)}
