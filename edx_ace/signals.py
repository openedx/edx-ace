"""
Signals for the edx_ace app
"""
from django.dispatch import Signal

# signal to indicate that a message has been sent using ace
ACE_EMAIL_SENT = Signal()
