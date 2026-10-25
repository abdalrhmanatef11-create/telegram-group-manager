import os
import logging
from telegram import Update, ChatInviteLink
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ChatJoinRequestHandler,
    ContextTypes, filters
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_IDS = {
    int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",")
    if x.strip().isdigit()
}
GROUP_ID = os.getenv("GROUP_ID", "").strip()
INVITE_LINK = os.getenv("INVITE_LINK", "").strip()

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:
        return
    await update.message.reply_text(
        "أهلاً بك في بوت إدارة الانضمام للجروب.\n\n"
        "البوت لا يضيف أشخاصًا من قائمة يوزرات دون موافقتهم. "
        "إذا كنت تريد الانضمام، اطلب رابط الجروب من المشرف أو استخدم /joininfo."
    )

async def joininfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if INVITE_LINK:
        await update.message.reply_text(
            "رابط الانضمام للجروب:\n" + INVITE_LINK
        )
    else:
        await update.message.reply_text(
            "رابط الانضمام غير مضبوط بعد. تواصل مع مشرف الجروب."
        )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(
        f"حسابك مسجل لدى البوت.\nمعرّفك: {user_id}"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "الأوامر:\n"
        "/start — بدء استخدام البوت\n"
        "/joininfo — الحصول على رابط الانضمام\n"
        "/status — عرض معرّف حسابك\n\n"
        "للمشرفين: أضف معرّفك إلى ADMIN_IDS في إعدادات التشغيل."
    )

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or not is_admin(user.id):
        await update.message.reply_text("الأمر متاح للمشرفين فقط.")
        return
    group_text = GROUP_ID if GROUP_ID else "غير مضبوط"
    link_text = INVITE_LINK if INVITE_LINK else "غير مضبوط"
    await update.message.reply_text(
        "إعدادات البوت الحالية:\n"
        f"GROUP_ID: {group_text}\n"
        f"INVITE_LINK: {link_text}\n"
        f"عدد المشرفين المعرّفين: {len(ADMIN_IDS)}\n\n"
        "اضبط القيم من متغيرات البيئة في منصة الاستضافة."
    )

async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Join requests are only auto-approved if explicitly configured by the owner.
    # Default behavior is to notify admins, not approve automatically.
    req = update.chat_join_request
    if not req:
        return
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=(
                    "وصل طلب انضمام جديد.\n"
                    f"الجروب: {req.chat.title}\n"
                    f"المستخدم: {req.from_user.full_name}\n"
                    f"معرّف المستخدم: {req.from_user.id}\n"
                    "راجع الطلب من تيليجرام."
                ),
            )
        except Exception:
            logging.exception("Could not notify admin %s", admin_id)

def main():
    if not TOKEN:
        raise RuntimeError("Set BOT_TOKEN in environment variables.")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("joininfo", joininfo))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(ChatJoinRequestHandler(join_request))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
