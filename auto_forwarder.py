import asyncio
from telethon import TelegramClient, events, errors

# =============================
# READ / SAVE CREDENTIALS
# =============================

def read_credentials():
    try:
        with open("credentials.txt", "r") as f:
            api_id = int(f.readline().strip())
            api_hash = f.readline().strip()
            phone = f.readline().strip()
            return api_id, api_hash, phone
    except:
        return None, None, None


def write_credentials(api_id, api_hash, phone):
    with open("credentials.txt", "w") as f:
        f.write(str(api_id) + "\n")
        f.write(api_hash + "\n")
        f.write(phone + "\n")


# =============================
# LOGIN FUNCTION
# =============================

async def login(client, phone):
    await client.connect()

    if not await client.is_user_authorized():
        print("Sending code...")
        await client.send_code_request(phone)

        try:
            code = input("Enter login code: ")
            await client.sign_in(phone, code)

        except errors.SessionPasswordNeededError:
            password = input("Enter 2FA password: ")
            await client.sign_in(password=password)

    print("Login successful")


# =============================
# LIST CHATS
# =============================

async def list_chats(client):
    dialogs = await client.get_dialogs()

    print("\nYour chats:\n")

    with open("chats.txt", "w", encoding="utf-8") as f:
        for dialog in dialogs:
            line = f"{dialog.name} | ID: {dialog.id}"
            print(line)
            f.write(line + "\n")

    print("\nSaved to chats.txt\n")


# =============================
# AUTO FORWARD FUNCTION
# =============================

def setup_forwarder(client, source_id, destination_id, keywords):

    @client.on(events.NewMessage(chats=source_id))
    async def handler(event):

        message = event.message

        try:

            # keyword filtering
            if keywords:
                text = message.text or ""
                if not any(k.lower() in text.lower() for k in keywords):
                    return

            # forward EVERYTHING (videos, photos, files, text)
            await client.forward_messages(
                destination_id,
                message
            )

            print(f"Forwarded message ID: {message.id}")

        except Exception as e:
            print("Forward error:", e)


# =============================
# MAIN PROGRAM
# =============================

async def main():

    api_id, api_hash, phone = read_credentials()

    if not api_id:
        api_id = int(input("Enter API ID: "))
        api_hash = input("Enter API HASH: ")
        phone = input("Enter phone number: ")
        write_credentials(api_id, api_hash, phone)

    client = TelegramClient("forwarder_session", api_id, api_hash)

    await login(client, phone)

    print("\nOptions:")
    print("1. List chats")
    print("2. Start auto forward")

    choice = input("Enter choice: ")

    if choice == "1":

        await list_chats(client)
        return

    elif choice == "2":

        source = int(input("Enter SOURCE chat ID: "))
        destination = int(input("Enter DESTINATION chat ID: "))

        keyword_input = input("Enter keywords (comma separated) or press Enter for ALL messages: ")

        keywords = [k.strip() for k in keyword_input.split(",") if k.strip()]

        setup_forwarder(client, source, destination, keywords)

        print("\nAuto forwarding started...")
        print("Press CTRL+C to stop\n")

        await client.run_until_disconnected()

    else:
        print("Invalid choice")


# =============================
# START
# =============================

asyncio.run(main())
