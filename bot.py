import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CANAL = "@AchadinhosDaKetty"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛍️ Oi! Eu sou o bot dos Achadinhos da Ketty! 💗\n\n"
        "Me envie um link de produto da Shopee e eu preparo uma legenda para você."
    )

async def receber_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text.strip()

    if "shopee" not in link.lower() and "shp.ee" not in link.lower():
        await update.message.reply_text(
            "⚠️ Parece que esse não é um link da Shopee.\n"
            "Me envie o link de um produto da Shopee 🛍️"
        )
        return

    legenda = (
        "🛍️✨ ACHADINHO DA KETTY! ✨🛍️\n\n"
        "😍 Olha esse achadinho que encontrei na Shopee!\n\n"
        "🔥 Vale super a pena conferir!\n\n"
        "🛒 COMPRE AQUI 👇\n"
        f"{link}\n\n"
        "💗 Achadinhos, ofertas e coisas que a gente ama!\n\n"
        "#shopee #achadinhos #ofertas #promocao #achadinhosdaketty"
    )

    botoes = [
        [
            InlineKeyboardButton("🟢 PUBLICAR", callback_data="publicar"),
            InlineKeyboardButton("❌ CANCELAR", callback_data="cancelar")
        ]
    ]

    await update.message.reply_text(
        legenda,
        reply_markup=InlineKeyboardMarkup(botoes)
    )

async def botao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "cancelar":
        await query.edit_message_text("❌ Oferta cancelada.")

    elif query.data == "publicar":
        mensagem = query.message.text

        try:
            await context.bot.send_message(
                chat_id=CANAL,
                text=mensagem
            )

            await query.edit_message_reply_markup(reply_markup=None)
            await query.message.reply_text("✅ Oferta publicada no canal! 🛍️💗")

        except Exception:
            await query.message.reply_text(
                "⚠️ Não consegui publicar no canal.\n\n"
                "Confira se o bot é administrador do canal e possui permissão para publicar mensagens."
            )

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receber_link))
    app.add_handler(CallbackQueryHandler(botao))

    print("Bot iniciado!")
    app.run_polling()

if __name__ == "__main__":
    main()
