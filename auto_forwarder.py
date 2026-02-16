import asyncio
from telethon import TelegramClient, events, errors

# =========================
# SETTINGS
# =========================

DELAY_BETWEEN_MESSAGES = 1.5   # seconds
COOLDOWN_AFTER = 600           # messages
COOLDOWN_TIME = 300            # seconds (5 minutes)

# =========================
# READ / WRITE CREDENTIALS
# =========================

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


# =========================
# LOGIN
# =========================

async def login(client, phone):

    await client.connect()

    if not await client.is_user_authorized():

        print("Sending login code...")
        await client.send_code_request(phone)

        try:
            code = input("Enter code: ")
            await client.sign_in(phone, code)

        except errors.SessionPasswordNeededError:
            password = input("Enter 2FA password: ")
            await client.sign_in(password=password)

    print("Login successful\n")


# =========================
# LIST CHATS
# =========================

async def list_chats(client):

    dialogs = await client.get_dialogs()

    for dialog in dialogs:
        print(f"{dialog.name} | ID: {dialog.id}")


# =========================
# COPY MESSAGE
# =========================

async def copy_message(client, destination, message):

    if message.media:

        await client.send_message(
            destination,
            message.text or "",
            file=message.media
        )

    else:

        await client.send_message(
            destination,
            message.text or ""
        )


# =========================
# FORWARD MESSAGE
# =========================

async def forward_message(client, destination, message):

    await client.forward_messages(destination, message)


# =========================
# SAFE PROCESS FUNCTION
# =========================

async def process_message(client, destination, message, mode):

    if mode == 1:
        await forward_message(client, destination, message)
    else:
        await copy_message(client, destination, message)


# =========================
# MAIN FORWARDER
# =========================

async def setup_forwarder(client, source_id, destination_id, mode):

    source = await client.get_entity(source_id)
    destination = await client.get_entity(destination_id)

    print(f"Source: {source.title}")
    print(f"Destination: {destination.title}")

    if mode == 1:
        print("Mode: FORWARD\n")
    else:
        print("Mode: COPY (hidden source)\n")

    print("Starting safe forwarding...\n")

    count = 0

    # =========================
    # OLD MESSAGE FORWARD
    # =========================

    async for message in client.iter_messages(source, reverse=True):

        try:

            await process_message(client, destination, message, mode)

            count += 1

            print(f"Processed: {message.id} | Total: {count}")

            # delay between messages
            await asyncio.sleep(DELAY_BETWEEN_MESSAGES)

            # cooldown protection
            if count % COOLDOWN_AFTER == 0:

                print(f"\nCooldown triggered after {count} messages")
                print(f"Sleeping {COOLDOWN_TIME} seconds...\n")

                await asyncio.sleep(COOLDOWN_TIME)

        except errors.FloodWaitError as e:

            print(f"\nFloodWait detected!")
            print(f"Sleeping {e.seconds} seconds...\n")

            await asyncio.sleep(e.seconds)

        except Exception as e:

            print("Error:", e)
            await asyncio.sleep(5)

    print("\nOld messages completed\n")

    # =========================
    # NEW MESSAGE LISTENER
    # =========================

    @client.on(events.NewMessage(chats=source))
    async def handler(event):

        try:

            await process_message(
                client,
                destination,
                event.message,
                mode
            )

            print(f"New message processed: {event.message.id}")

            await asyncio.sleep(DELAY_BETWEEN_MESSAGES)

        except errors.FloodWaitError as e:

            print(f"FloodWait (new message): sleeping {e.seconds}")
            await asyncio.sleep(e.seconds)

        except Exception as e:

            print("Error:", e)

    print("Now listening for new messages safely...\n")


# =========================
# MAIN
# =========================

async def main():

    api_id, api_hash, phone = read_credentials()

    if not api_id:

        api_id = int(input("Enter API ID: "))
        api_hash = input("Enter API HASH: ")
        phone = input("Enter phone: ")

        write_credentials(api_id, api_hash, phone)

    client = TelegramClient(
        f"safe_session_{phone}",
        api_id,
        api_hash
    )

    await login(client, phone)

    print("Options:")
    print("1. List chats")
    print("2. Start forwarder\n")

    choice = input("Enter choice: ")

    if choice == "1":

        await list_chats(client)
        return

    if choice == "2":

        source_id = int(input("Enter SOURCE chat ID: "))
        destination_id = int(input("Enter DESTINATION chat ID: "))

        print("\nSelect mode:")
        print("1 = Forward mode")
        print("2 = Copy mode (hide source)")

        mode = int(input("Enter mode: "))

        await setup_forwarder(
            client,
            source_id,
            destination_id,
            mode
        )

        await client.run_until_disconnected()


# =========================
# START
# =========================

asyncio.run(main())
