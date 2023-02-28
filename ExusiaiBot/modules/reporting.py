#    Haruka Aya (A telegram bot project)
#    Copyright (C) 2017-2019 Paul Larsen
#    Copyright (C) 2019-2020 Akito Mizukito (Haruka Network Development)

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import html
from typing import List, Optional
from telegram import Message, Chat, Update, Bot, User, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest, Unauthorized
from telegram.ext import CommandHandler, RegexHandler, run_async, Filters, CallbackQueryHandler
from telegram.utils.helpers import mention_html

from ExusiaiBot import dispatcher, LOGGER
from ExusiaiBot.modules.helper_funcs.chat_status import user_not_admin, user_admin
from ExusiaiBot.modules.log_channel import loggable
from ExusiaiBot.modules.sql import reporting_sql as sql
from ExusiaiBot.modules.tr_engine.strings import tld

REPORT_GROUP = 5


@run_async
@user_admin
def report_setting(bot: Bot, update: Update, args: List[str]):
    chat = update.effective_chat  # type: Optional[Chat]
    msg = update.effective_message  # type: Optional[Message]

    if chat.type == chat.PRIVATE:
        if args:
            if args[0] in ("yes", "on"):
                sql.set_user_setting(chat.id, True)
                msg.reply_text(tld(chat.id, "reports_pm_on"))

            elif args[0] in ("no", "off"):
                sql.set_user_setting(chat.id, False)
                msg.reply_text(tld(chat.id, "reports_pm_off"))
        else:
            msg.reply_text(tld(chat.id, "reports_pm_pref").format(
                sql.user_should_report(chat.id)),
                           parse_mode=ParseMode.MARKDOWN)

    elif args:
        if args[0] in ("yes", "on"):
            sql.set_chat_setting(chat.id, True)
            msg.reply_text(tld(chat.id, "reports_chat_on"))

        elif args[0] in ("no", "off"):
            sql.set_chat_setting(chat.id, False)
            msg.reply_text(tld(chat.id, "reports_chat_off"))
    else:
        msg.reply_text(tld(chat.id, "reports_chat_pref").format(
            sql.chat_should_report(chat.id)),
                       parse_mode=ParseMode.MARKDOWN)


@run_async
@user_not_admin
@loggable
def report(bot: Bot, update: Update) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]

    message = update.effective_message
    if chat and message.reply_to_message and sql.chat_should_report(chat.id):
        reported_user = message.reply_to_message.from_user  # type: Optional[User]
        chat_name = chat.title or chat.first or chat.username
        admin_list = chat.get_administrators()

        if int(reported_user.id) == int(user.id):
            return

        if chat.username and chat.type == Chat.SUPERGROUP:
            msg = f"<b>{html.escape(chat.title)}:</b>\n<b>Reported user:</b> {mention_html(reported_user.id, reported_user.first_name)} (<code>{reported_user.id}</code>)\n<b>Reported by:</b> {mention_html(user.id, user.first_name)} (<code>{user.id}</code>)"
            link = f'\n<b>Link:</b> <a href=\"http://telegram.me/{chat.username}/{message.message_id}\">click here</a>'

            keyboard = [
                [
                    InlineKeyboardButton(
                        u"➡ Message",
                        url=f"https://t.me/{chat.username}/{str(message.reply_to_message.message_id)}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        u"⚠ Kick",
                        callback_data=f"report_{chat.id}=kick={reported_user.id}={reported_user.first_name}",
                    ),
                    InlineKeyboardButton(
                        u"⛔️ Ban",
                        callback_data=f"report_{chat.id}=banned={reported_user.id}={reported_user.first_name}",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        u"❎ Delete Message",
                        callback_data=f"report_{chat.id}=delete={reported_user.id}={message.reply_to_message.message_id}",
                    )
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

        else:
            msg = f'{mention_html(user.id, user.first_name)} is calling for admins in \"{html.escape(chat_name)}\"!'
            link = ""
        should_forward = True
        for admin in admin_list:
            if admin.user.is_bot:  # can't message bots
                continue

            if sql.user_should_report(admin.user.id):
                try:
                    if chat.type != Chat.SUPERGROUP:
                        bot.send_message(admin.user.id,
                                         msg + link,
                                         parse_mode=ParseMode.HTML,
                                         disable_web_page_preview=True)

                        if should_forward:
                            message.reply_to_message.forward(admin.user.id)

                            if len(
                                    message.text.split()
                            ) > 1:  # If user is giving a reason, send his message too
                                message.forward(admin.user.id)

                    if not chat.username:
                        bot.send_message(admin.user.id,
                                         msg + link,
                                         parse_mode=ParseMode.HTML,
                                         disable_web_page_preview=True)

                        if should_forward:
                            message.reply_to_message.forward(admin.user.id)

                            if len(
                                    message.text.split()
                            ) > 1:  # If user is giving a reason, send his message too
                                message.forward(admin.user.id)

                    if chat.username and chat.type == Chat.SUPERGROUP:
                        bot.send_message(admin.user.id,
                                         msg + link,
                                         parse_mode=ParseMode.HTML,
                                         reply_markup=reply_markup,
                                         disable_web_page_preview=True)

                        if should_forward:
                            message.reply_to_message.forward(admin.user.id)

                            if len(
                                    message.text.split()
                            ) > 1:  # If user is giving a reason, send his message too
                                message.forward(admin.user.id)

                except Unauthorized:
                    pass
                except BadRequest as excp:  # TODO: cleanup exceptions
                    LOGGER.exception(
                        f"Exception while reporting user : {excp}")

        message.reply_to_message.reply_text(tld(
            chat.id,
            "reports_success").format(mention_html(user.id, user.first_name)),
                                            parse_mode=ParseMode.HTML,
                                            disable_web_page_preview=True)
        return msg

    return ""


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def buttons(bot: Bot, update):
    query = update.callback_query
    splitter = query.data.replace("report_", "").split("=")
    if splitter[1] == "kick":
        try:
            bot.kickChatMember(splitter[0], splitter[2])
            bot.unbanChatMember(splitter[0], splitter[2])
            query.answer("✅ Succesfully kicked")
            return ""
        except Exception as err:
            query.answer("❎ Failed to kick")
            bot.sendMessage(
                text=f"Error: {err}",
                chat_id=query.message.chat_id,
                parse_mode=ParseMode.HTML,
            )
    elif splitter[1] == "banned":
        try:
            bot.kickChatMember(splitter[0], splitter[2])
            query.answer("✅  Succesfully Banned")
            return ""
        except Exception as err:
            bot.sendMessage(
                text=f"Error: {err}",
                chat_id=query.message.chat_id,
                parse_mode=ParseMode.HTML,
            )
            query.answer("❎ Failed to ban")
    elif splitter[1] == "delete":
        try:
            bot.deleteMessage(splitter[0], splitter[3])
            query.answer("✅ Message Deleted")
            return ""
        except Exception as err:
            bot.sendMessage(
                text=f"Error: {err}",
                chat_id=query.message.chat_id,
                parse_mode=ParseMode.HTML,
            )
            query.answer("❎ Failed to delete message!")


__help__ = True

REPORT_HANDLER = CommandHandler("report", report, filters=Filters.group)
SETTING_HANDLER = CommandHandler("reports", report_setting, pass_args=True)
ADMIN_REPORT_HANDLER = RegexHandler("(?i)@admin(s)?", report)

report_button_user_handler = CallbackQueryHandler(buttons, pattern=r"report_")
dispatcher.add_handler(report_button_user_handler)

dispatcher.add_handler(REPORT_HANDLER, REPORT_GROUP)
dispatcher.add_handler(ADMIN_REPORT_HANDLER, REPORT_GROUP)
dispatcher.add_handler(SETTING_HANDLER)
