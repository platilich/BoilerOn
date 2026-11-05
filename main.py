import requests
import tinytuya
from dotenv import load_dotenv
import os
from time import sleep



load_dotenv('.env')


DEVICE_ID = os.getenv('DEVICE_ID')
DEVICE_IP = os.getenv('DEVICE_IP')
LOCAL_KEY = os.getenv('LOCAL_KEY')

TG_TOKEN = os.getenv('TOKEN_BOT')
ADMINS_ID = [int(i.strip()) for i in os.getenv("ADMINS_ID", "").split(",") if i.strip()]



d = tinytuya.OutletDevice(str(DEVICE_ID), str(DEVICE_IP), str(LOCAL_KEY))
d.set_version(3.5)


def notify(text):
    try:
        for ADMIN_ID in ADMINS_ID:
            requests.post(
                f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                data={"chat_id": ADMIN_ID, "text": text},
                timeout=10,
            )

    except Exception as e:
        print("Не удалось отправить уведомление:", e)



def init():
    status = d.status()
    dps = status.get("dps", {})
    return dps


def get_status(dps):
    is_on = dps.get("1") # status
    mode = dps.get('13') # mode
    temperature = dps.get('10') # current temperature



    return is_on, mode, temperature



def warm_bath():
    d.set_value('13', 'heating')
    d.set_value('9', '75')




def send_info():
    dps = init()
    is_on, mode, temperature = get_status(dps)

    notify(
        "🔥 The water heater wasn’t heating, so I’m turning on the heating now.\n"
        f"Power: {'On' if is_on else 'Off'}\n"
        f"Mode: {mode}\n"
        f"Current temperature: {temperature}° С"
    )



while True:
    dps = init()

    is_on, mode, temperature = get_status(dps)


    if dps:
        if is_on:
            if mode == 'standby':
                warm_bath()
                send_info()


        else:
            d.set_status(True) # --- turn on boiler ---
            warm_bath()
            send_info()



    else:
        notify("⚠️ The water heater is off.\nPlease turn it on.")

    sleep(5)