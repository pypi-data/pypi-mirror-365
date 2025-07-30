import os
import sys
sys.path.insert(0, os.path.dirname(os.getcwd()))

import requests
from zikomo.constants import WA_BUSINESS_ACCOUNT_ID, WA_PHONE_NUMBER_ID, WA_TOKEN, WA_USERS
from zikomo.utils import get_formatted_datetime

def get_whatsapp_templates(waba_id: str, access_token: str) -> dict:    
    url = f"https://graph.facebook.com/v22.0/{waba_id}/message_templates"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("✅ Templates fetched successfully.")
        return response.json()
    else:
        print(f"❌ Failed with status {response.status_code}")

        return response.json()

def send_whatsapp_template(
    access_token: str,
    from_phone_number_id: str,
    to_phone_number: str,
    template_name: str,
    language_code: str,
    named_params: list[dict] = None,
    positional_params: list[dict] = None,
    header_params: list[dict] = None,
    button_params: list[dict] = None,
    api_version: str = "v22.0"
):
    import requests

    url = f"https://graph.facebook.com/{api_version}/{from_phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Build the "components" section
    components = []

    if header_params:
        components.append({
            "type": "header",
            "parameters": header_params
        })

    if named_params:
        components.append({
            "type": "body",
            "parameters": named_params
        })

    if positional_params:
        components.append({
            "type": "body",
            "parameters": positional_params
        })

    if button_params:
        components.append({
            "type": "button",
            "sub_type": "url",
            "index": 0,
            "parameters": button_params
        })

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone_number,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {
                "code": language_code
            },
            "components": components
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.status_code, response.json()


def send_updates_on_whatsapp(environment,header,project,version,datetime): 
    for phone_number in WA_USERS:
        status, result = send_whatsapp_template(
            access_token=WA_TOKEN,
            from_phone_number_id=WA_PHONE_NUMBER_ID,
            to_phone_number=phone_number,
            template_name="software_update",
            language_code="en_US",
            button_params=[{"type": "text", "text": environment.lower()}],
            header_params=[{"type": "text", "text": header}],
            positional_params=[
            {
                "type": "text",            
                "text": project
            },
            {
                "type": "text",           
                "text": environment.upper()
            },
            {
                "type": "text",           
                "text": project
            },
            {
                "type": "text",           
                "text": version
            },
            {
                "type": "text",           
                "text": datetime
            }
        ])
        
        if status==200:
            print(f"WhatsApp message sent to {phone_number}")
        else:
            print("Status",status)
            print("WhatsApp Result:", result)
        

        

def test_template():    
    send_updates_on_whatsapp("staging","staging updated","Backoffice","v1.2.3-staging",get_formatted_datetime())

if __name__=="__main__":   
    test_template()
    #print(get_whatsapp_templates(WA_BUSINESS_ACCOUNT_ID,WA_TOKEN))