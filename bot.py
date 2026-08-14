
import os
import re
import html
import requests

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CANAL = "@AchadinhosDaKetty"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 13) "
        "AppleWebKit/537.36 Chrome/120.0 Mobile Safari/537.36"
    )
}


def pegar_dados(link):
    try:
        resposta = requests.get(
            link,
            headers=HEADERS,
            timeout=15,
            allow_redirects=True
        )

        texto = resposta.text

        titulo = None
        imagem = None
        preco = None

        # Título
        resultado = re.search(
            r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)',
            texto,
            re.I
        )

        if resultado:
            titulo = html.unescape(resultado.group(1)).strip()

        # Imagem
        resultado = re.search(
            r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)',
            texto,
            re.I
        )

        if resultado:
            imagem = html.unescape(resultado.group(1)).strip()

        # Preço — tentativa de encontrar valores em reais
        precos = re.findall(
            r'R\$\s?\d{1,5}(?:[.,]\d{2})?',
            texto
        )

        if precos:
            preco = precos[0]

        return titulo, imagem, preco

    except Exception:
        return None, None, None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛍️💗 Oi! Eu sou o bot dos Achadinhos da Ketty!\n\n"
        "Me envie um link de produto da Shopee e vou tentar "
        "montar a oferta para você."
    )


async def receber_link(update: Update, context: ContextTypes.DEFAULT_TYPE):

    link = update.message.text.strip()

    if "shopee" not in link.lower() and "shp.ee" not in link.lower():
        await update.message.reply_text(
            "⚠️ Esse não parece ser um link da Shopee.\n\n"
            "Envie o link de um produto da Shopee 🛍️"
        )
        return

    await update.message.reply_text(
        "🔎 Procurando as informações do produto...\n"
        "Aguarde um pouquinho 💗"
    )

    titulo, imagem, preco = pegar_dados(link)

    if not titulo:
        titulo = "Achadinho da Shopee 🛍️"

    legenda = (
        "🛍️✨ ACHADINHO DA KETTY! ✨🛍️\n\n"
        f"😍 {titulo}\n\n"
    )

    if preco:
        legenda += f"💰 Preço encontrado: {preco}\n\n"

    legenda += (
        "🔥 Vale a pena conferir!\n\n"
        "🛒 COMPRE AQUI 👇\n"
        f"{link}\n\n"
        "💗 Achadinhos, ofertas e coisas que a gente ama!\n\n"
        "#shopee #achadinhos #ofertas "
        "#promocao #achadinhosdaketty"
    )

    botoes = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🟢 PUBLICAR",
                callback_data="publicar"
            ),
            InlineKeyboardButton(
                "❌ CANCELAR",
                callback_data="cancelar"
            )
        ]
    ])

    # Se encontrou uma imagem, tenta enviar com ela
    if imagem:
        try:
            await update.message.reply_photo(
                photo=imagem,
                caption=legenda,
                reply_markup=botoes
            )
            return
        except Exception:
            pass

    # Caso a imagem não possa ser carregada
    await update.message.reply_text(
        legenda,
        reply_markup=botoes
    )


async def botao(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.data == "cancelar":
        await query.edit_message_reply_markup(
            reply_markup=None
        )

        await query.message.reply_text(
            "❌ Oferta cancelada."
        )

    elif query.data == "publicar":

        texto = query.message.caption or query.message.text

        try:

            if query.message.photo:

                await context.bot.send_photo(
                    chat_id=CANAL,
                    photo=query.message.photo[-1].file_id,
                    caption=texto
                )

            else:

                await context.bot.send_message(
                    chat_id=CANAL,
                    text=texto
                )

            await query.edit_message_reply_markup(
                reply_markup=None
            )

            await query.message.reply_text(
                "✅ Publicado no canal Achadinhos da Ketty! 🛍️💗"
            )

        except Exception as erro:

            print("Erro ao publicar:", erro)

            await query.message.reply_text(
                "⚠️ Não consegui publicar.\n\n"
                "Verifique se o bot é administrador do "
                "canal @AchadinhosDaKetty e possui permissão "
                "para publicar mensagens."
            )


def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            receber_link
        )
    )

    app.add_handler(
        CallbackQueryHandler(botao)
    )

    print("🛍️ Achadinhos da Ketty iniciado!")

    app.run_polling()


if __name__ == "__main__":
    main()
