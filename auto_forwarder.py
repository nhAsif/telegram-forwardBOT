import asyncio
from telethon import TelegramClient, events, errors

# ============================
# READ / WRITE CREDENTIALS
# ============================

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


# ============================
# LOGIN FUNCTION
# ============================

async def login(client, phone):

    await client.connect()

    if not await client.is_user_authorized():

        print("Sending login code...")
        await client.send_code_request(phone)

        try:
            code = input("Enter login code: ")
            await client.sign_in(phone, code)

        except errors.SessionPasswordNeededError:
            password = input("Enter 2FA password: ")
            await client.sign_in(password=password)

    print("Login successful\n")


# ============================
# LIST CHATS FUNCTION
# ============================

async def list_chats(client):

    dialogs = await client.get_dialogs()

    print("\nYour chats:\n")

    with open("chats.txt", "w", encoding="utf-8") as f:

        for dialog in dialogs:

            name = dialog.name
            chat_id = dialog.id

            line = f"{name}  |  ID: {chat_id}"

            print(line)
            f.write(line + "\n")

    print("\nSaved to chats.txt\n")


# ============================
# AUTO FORWARDER FUNCTION
# ============================

async def setup_forwarder(client, source_id, destination_id, keywords):

    try:
        # Convert IDs to entities (CRITICAL FIX)
        source = await client.get_entity(source_id)
        destination = await client.get_entity(destination_id)

    except Exception as e:
        print("Error getting channel entities:", e)
        return

    print(f"Listening from: {source.title}")
    print(f"Forwarding to: {destination.title}")
    print("Waiting for new messages...\n")

    # Event listener
    @client.on(events.NewMessage(chats=source))
    async def handler(event):

        message = event.message

        print(f"New message detected: ID {message.id}")

        try:

            # Keyword filter
            if keywords:
                text = message.text or ""
                if not any(k.lower() in text.lower() for k in keywords):
                    print("Skipped (no keyword match)")
                    return

            # Forward message (supports ALL media)
            await client.forward_messages(
                destination,
                message
            )

            print(f"Forwarded message ID: {message.id}\n")

        except Exception as e:
            print("Forward failed:", e)


# ============================
# MAIN PROGRAM
# ============================

async def main():

    api_id, api_hash, phone = read_credentials()

    if not api_id:

        api_id = int(input("Enter API ID: "))
        api_hash = input("Enter API HASH: ")
        phone = input("Enter phone number: ")

        write_credentials(api_id, api_hash, phone)

    client = TelegramClient(
        "forwarder_session",
        api_id,
        api_hash
    )

    await login(client, phone)

    print("Options:")
    print("1. List chats")
    print("2. Start auto forward\n")

    choice = input("Enter choice: ")

    if choice == "1":

        await list_chats(client)
        return

    elif choice == "2":

        source_id = int(input("Enter SOURCE chat ID: "))
        destination_id = int(input("Enter DESTINATION chat ID: "))

        keyword_input = input(
            "Enter keywords (comma separated) or press Enter for ALL messages: "
        )

        keywords = [
            k.strip().lower()
            for k in keyword_input.split(",")
            if k.strip()
        ]

        await setup_forwarder(
            client,
            source_id,
            destination_id,
            keywords
        )

        print("Auto forwarding is now running.")
        print("Send a new message in source channel to test.\n")

        await client.run_until_disconnected()

    else:
        print("Invalid choice")


# ============================
# START SCRIPT
# ============================

if __name__ == "__main__":
    asyncio.run(main())
