import africastalking
from app.config import settings

# Initialize Africa's Talking
africastalking.initialize(settings.AFRICASTALKING_USERNAME, settings.AFRICASTALKING_API_KEY)
sms = africastalking.SMS

async def send_sms(phone_number: str, message: str) -> dict:
    """
    Send an SMS using Africa's Talking API.
    """
    try:
        # Ensure phone number is in international format (e.g., +2519XXXXXXXX)
        if not phone_number.startswith("+"):
            phone_number = "+251" + phone_number.lstrip("0")
        response = sms.send(message, [phone_number], sender_id=settings.SMS_SENDER_ID)
        return {"success": True, "response": response}
    except Exception as e:
        return {"success": False, "error": str(e)}
