#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Virtual Number bot for Telegram
# Sends random virtual numbers to user
# Service: OnlineSim.io
# SourceCode (https://github.com/kozyol/OnlineSimBot)

# Standard library imports
import json
import random
import time
from typing import ClassVar, NoReturn, Any, Union, List, Dict

# Related third party module imports
import telebot
import phonenumbers
import countryflag

# Local application module imports
from src import utils
from src.utils import User
from src.vneng import VNEngine

# Initialize the bot token
bot: ClassVar[Any] = telebot.TeleBot(utils.get_token())
print(f"\33[1;36m::\33[m Bot is running with ID: {bot.get_me().id}")


@bot.message_handler(commands=["start", "restart"])
def start_command_handler(message: ClassVar[Any]) -> NoReturn:
    """
    Function to handle start commands in bot
    Shows welcome messages to users

    Parameters:
        message (typing.ClassVar[Any]): Incoming message object

    Returns:
        None (typing.NoRe
        turn)
    """

    # Fetch user's data
    user: ClassVar[Union[str, int]] = User(message.from_user)

    # Send welcome message
    bot.send_chat_action(chat_id=message.chat.id, action="typing")
    bot.reply_to(
        message=message,
        text=(
            f"⁀➴ MERHABA {user.pn}\n"
            "Sanal Numara Botuna Hoş Geldiniz\n\n"
            "Yardım mesajı almak için /help gönder\n"
            "Sanal bir numara almak için /number gönderin.\n"
            "BY AETHRA - @kaganlik - @aethrazirve\n"
        )
    )


@bot.message_handler(commands=["help", "usage"])
def help_command_handler(message: ClassVar[Any]) -> NoReturn:
    """
    Function to handle help commands in bot
    Shows help messages to users

    Parameters:
        message (typing.ClassVar[Any]): Incoming message object

    Returns:
        None (typing.NoReturn)
    """

    # Fetch user's data
    user: ClassVar[Union[str, int]] = User(message.from_user)

    # Send Help message
    bot.send_chat_action(chat_id=message.chat.id, action="typing")
    bot.reply_to(
        message=message,
        text=(
           "·ᴥ· Sanal Numara Botu\n\n"
"Bu bot, onlinesim.io'dan API kullanarak çevrimiçi ve aktif numara alır.\n"
"Tek yapmanız gereken birkaç komut göndermek ve bot sizin için rastgele bir numara bulacaktır.\n\n══════════════\n"
"★ Yeni bir numara almak için basitçe /number komutunu gönderebilir veya numaranızı yenilemek için inline butonu (Yenile) kullanabilirsiniz.\n\n"
"★ Gelen kutusu mesajlarını görmek için (inbox) inline butonunu kullanabilirsiniz. Bu, son 5 mesajı gösterecektir.\n\n"
"★ Ayrıca numaranın Telegram profilini inline butonunu kullanarak kontrol edebilirsiniz (telefon numarasının profilini kontrol et)\n══════════════\n\n"
"Bu bot hakkında bilmeniz gereken her şey bu kadar!"

        )
    )


@bot.message_handler(commands=["number"])
def number_command_handler(message: ClassVar[Any]) -> NoReturn:
    """
    Function to handle number commands in bot
    Finds and sends new virtual number to user

    Parameters:
        message (typing.ClassVar[Any]): Incoming message object

    Returns:
        None (typing.NoReturn)
    """

    # Send waiting prompt
    bot.send_chat_action(chat_id=message.chat.id, action="typing")
    prompt: ClassVar[Any] = bot.reply_to(
        message=message,
        text=(
           "Rastgele bir numara alınıyor...\n\n"
"⁀➴ Çevrimiçi ülkeler alınıyor:"

        ),
    )

    # Initialize the Virtual Number engine
    engine: ClassVar[Any] = VNEngine()

    # Get the countries and shuffle them
    countries: List[Dict[str, str]] = engine.get_online_countries()
    random.shuffle(countries)

    # Update prompt based on current status
    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=prompt.message_id,
        text=(
            "Size rastgele bir numara alınıyor......\n\n"
            "⁀➴ Çevrimiçi ülkeler alınıyor:\n"
            f"Got {len(countries)} ülke alındı\n\n"
            "⁀➴ Aktif numaralar test ediliyor:\n"
        ),
    )

    # Find online and active number
    for country in countries:
        # Get numbers in country
        numbers: List[Dict[str, str]] = engine.get_country_numbers(
            country=country['name']
        )
        
        # Format country name
        country_name: str = country["name"].replace("_", " ").title()
    
        # Check numbers for country and find first valid one
        for number in numbers:
            # Parse the country to find it's details
            parsed_number: ClassVar[Union[str, int]] = phonenumbers.parse(
                number=f"+{number[1]}"
            )

            # Format number to make it readable for user
            formatted_number: str = phonenumbers.format_number(
                numobj=parsed_number,
                num_format=phonenumbers.PhoneNumberFormat.NATIONAL
            )

            # Find flag emoji for number
            flag: str = countryflag.getflag(
                [
                    phonenumbers.region_code_for_country_code(
                        country_code=parsed_number.country_code
                    )
                ]
            )

            # Update prompt based on current status
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=prompt.message_id,
                text=(
                    "Size rastgele bir numara alınıyor...\n\n"
                    "⁀➴ Çevrimiçi ülkeler alınıyor:\n"
                    f"Aktif {len(countries)} ülke var\n\n"
                    "⁀➴ Aktif numaralar test ediliyor:\n"
                    f"deneniyor {country_name} ({formatted_number})"
                ),
            ) 

            # Check if number is valid and it's inbox is active
            if engine.get_number_inbox(country['name'], number[1]):
                # Make keyboard markup for number
                Markup: ClassVar[Any] = telebot.util.quick_markup(
                    {
                        "𖥸 Gelen kutusu": {
                            "callback_data": f"msg&{country['name']}&{number[1]}"
                        },

                        "꩜ Yenile": {
                            "callback_data": f"new_phone_number"
                        },

                        "Telefon numarasının profilini kontrol edin": {
                            "url": f"tg://resolve?phone=+{number[1]}"
                        }
                    }, 
                    row_width=2
                )
                
                # Update prompt based on current status
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=prompt.message_id,
                    text=(
                        "Sizin için rastgele bir numara alıyorum...\n\n"
                        "⁀➴ Çevrimiçi ülkeler:\n"
                        f"aktif {len(countries)} ülke var\n\n"
                        "⁀➴ Aktif sayıları test etme:\n"
                        f"Deniyorum {country_name} ({formatted_number})\n\n"
                        f"{flag} İşte numaranız: +{number[1]}\n\n"
                        f"Son Güncelleme: {number[0]}"
                    ),
                    reply_markup=Markup
                )

                # Return the function
                return 1
    
    # Send failure message when no number found
    else:
        # Update prompt based on current status
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=prompt.message_id,
            text=(
                    "Size rastgele bir numara alınıyor...\n\n"
"⁀➴ Çevrimiçi ülkeler alınıyor:\n"
f"{len(countries)} ülke alındı\n\n"
"⁀➴ Aktif numaralar test ediliyor:\n"
"Şu anda çevrimiçi numara yok!"

                ),
        ) 

        # Return the function
        return 0


@bot.callback_query_handler(func=lambda x:x.data.startswith("msg"))
def number_inbox_handler(call: ClassVar[Any]) -> NoReturn:
    """
    Gelen kutusu mesajlarını işlemek için callback sorgu işleyici
    Numaranın gelen kutusundaki son 5 mesajı gönderir

    Parametreler:
        call (typing.ClassVar[Any]): Gelen çağrı nesnesi

    Döndürür:
        Yok (typing.NoReturn)
"""

    # Initialize the Virtual Number engine
    engine: ClassVar[Any] = VNEngine()

    # Get country name and number from call's data
    country: str
    number: str
    _, country, number = call.data.split("&")

    # Get all messages and select last 5 messages
    messages: List[Dict[str, str]] = engine.get_number_inbox(
        country=country, 
        number=number
    )[:5]

    # Send messages to user
    for message in messages:
        for key, value in message.items():
            bot.send_message(
                chat_id=call.message.chat.id,
                reply_to_message_id=call.message.message_id,
                text=(
                    f"⚯͛ Time: {key}\n\n"
                    f"{value.split('received from OnlineSIM.io')[0]}"
                )
            )

    # Answer callback query
    bot.answer_callback_query(
        callback_query_id=call.id,
        text=(
           "⁀➴ İşte son 5 mesaj\n\n"
      "Mesajınızı almadıysanız, 1 dakika sonra tekrar deneyin!"
      "@AethraZirve"

        ),
        show_alert=True
    )


@bot.callback_query_handler(func=lambda x:x.data == "new_phone_number")
def new_number_handler(call):
    """
    Numara yenilemek için callback sorgu işleyici
    Yeni telefon numarası bulur ve mesajı günceller

    Parametreler:
        call (typing.ClassVar[Any]): Gelen çağrı nesnesi

    Döndürür:
        Yok (typing.NoReturn)
"""

    # Get chat id and message id from call object
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    # Edit message based on current status
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=(
            "Size rastgele bir sayı alınıyor...\n\n"
          "⁀➴ Çevrimiçi ülkeler alınıyor:"

        ),
    )

    # Initialize the Virtual Number engine
    engine: ClassVar[Any] = VNEngine()

    # Get the countries and shuffle them
    countries: List[Dict[str, str]] = engine.get_online_countries()
    random.shuffle(countries)

    # Update prompt based on current status
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=(
            "Size rastgele bir sayı alınıyor...\n\n"
"⁀➴ Çevrimiçi ülkeler alınıyor:\n"
f"{len(countries)} ülke alındı\n\n"
"⁀➴ Aktif numaralar test ediliyor:\n"

        ),
    )

    # Find online and active number
    for country in countries:
        # Get numbers in country
        numbers: List[Dict[str, str]] = engine.get_country_numbers(
            country=country['name']
        )
        
        # Format country name
        country_name: str = country["name"].replace("_", " ").title()
    
        # Check numbers for country and find first valid one
        for number in numbers:
            # Parse the country to find it's details
            parsed_number: ClassVar[Union[str, int]] = phonenumbers.parse(
                number=f"+{number[1]}"
            )

            # Format number to make it readable for user
            formatted_number: str = phonenumbers.format_number(
                numobj=parsed_number,
                num_format=phonenumbers.PhoneNumberFormat.NATIONAL
            )

            # Find flag emoji for number
            flag: str = countryflag.getflag(
                [
                    phonenumbers.region_code_for_country_code(
                        country_code=parsed_number.country_code
                    )
                ]
            )

            # Update prompt based on current status
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=(
                    "Size rastgele bir numara alınıyor...\n\n"
"⁀➴ Çevrimiçi ülkeler alınıyor:\n"
f"{len(countries)} numara alındı\n\n"
"⁀➴ Aktif numaralar test ediliyor:\n"
f"{country_name} ({formatted_number}) deneniyor"

                ),
            ) 

            # Check if number is valid and it's inbox is active
            if engine.get_number_inbox(country['name'], number[1]):
                # Make keyboard markup for number
                Markup: ClassVar[Any] = telebot.util.quick_markup(
                    {
                        "𖥸 Gelen Kutusu": {
                            "callback_data": f"msg&{country['name']}&{number[1]}"
                        },

                        "꩜ Yenile": {
                            "callback_data": f"new_phone_number"
                        },

                        "Telefon numarasının profili var mı bakın": {
                            "url": f"tg://resolve?phone=+{number[1]}"
                        }
                    }, 
                    row_width=2
                )
                
                # Update prompt based on current status
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=(
                        "Size rastgele bir numara alınıyor...\n\n"
"⁀➴ Çevrimiçi ülkeler alınıyor:\n"
f"{len(countries)} numara alındı\n\n"
"⁀➴ Aktif numaralar test ediliyor:\n"
f"{country_name} ({formatted_number}) deneniyor\n\n"
f"{flag} İşte numaranız: +{number[1]}\n\n"
f"Son Güncelleme: {number[0]}"

                    ),
                    reply_markup=Markup
                )

                # Answer callback query
                bot.answer_callback_query(
                    callback_query_id=call.id,
                    text="⁀➴ Talebiniz güncellendi",
                    show_alert=False
                )

                # Return the function
                return 1
    
    # Send failure message when no number found
    else:
        # Update prompt based on current status
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=(
                    "Size rastgele bir numara alınıyor...\n\n"
"⁀➴ Çevrimiçi ülkeler alınıyor:\n"
f"{len(countries)} numara alındı\n\n"
"⁀➴ Aktif numaralar test ediliyor:\n"
"Şu anda çevrimiçi numara yok!"

                ),
        ) 

        # Return the function
        return 0


# Run the bot on polling mode
if __name__ == '__main__':
    try:
        bot.infinity_polling(
            skip_pending=True
        )
    except KeyboardInterrupt:
        raise SystemExit("\n\33[1;31m::\33[m Kullanıcı tarafından sonlandırıldı")
