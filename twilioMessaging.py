import os
from twilio.rest import Client

account_sid = 'AC5ad84788b7d0be1a50b6493d86497b42'
auth_token = 'd6618c32459025ccd2378485c38c38e3'
client = Client(account_sid, auth_token)

def send_message(body, to):
    client.messages \
            .create(
                body=body,
                from_='+18647778115',
                to=to
            )

def send_assign_message(to):
    send_message("A locker has been assigned to your card.", to)

def send_unassign_message(to):
    send_message("Thank you for using our smart locker! Have a good day.", to)

def send_tampering_message(to):
    send_message("Your locker is being tampered with, probably. Reach there ASAP. and file a complaint if found to be tampered with", to)
