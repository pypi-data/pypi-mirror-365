# xmodules/handlers/help.py

from telethon import TelegramClient, events


def register_help_handler(client: TelegramClient, admin_id: int):
    """
    Yordam menyusini chiqaradigan handler.
    """

    async def help_handler(event):
        if event.sender_id != admin_id:
            return

        await event.edit(
            "🤖 <b>@XModules buyruqlar:</b>\n\n"
            "• <code>.ok</code> – <b>Vaqtli mediadan nusxa olish</b>\n"
            "• <code>.type «matn»</code> – <b>Matnni yozayotgandek chiqarish</b>\n"
            "• <code>.countdown «soniya» «matn»</code> – <b>Sanab chiqib, oxirida o‘chirish</b>\n"
            "• <code>.flood «miqdor» «matn»</code> – <b>Xabarni ko‘p marta yuborish</b>\n"
            "• <code>.math «ifoda»</code> – <b>Matematik ifodani hisoblash</b>",
            parse_mode='html'
        )

    client.add_event_handler(help_handler, events.NewMessage(outgoing=True, pattern=r'^\.help$'))
    return client
