# standard library imports
from svix.webhooks import Webhook as SvixWebhook, WebhookVerificationError as SvixWebhookVerificationError


Webhook = SvixWebhook
WebhookVerificationError = SvixWebhookVerificationError


class CallbackVerificationError(WebhookVerificationError):
    """Alias for WebhookVerificationError for backward compatibility"""
    pass
