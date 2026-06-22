import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import requests
import os
import re
import time
import threading
import json

# ====================================================
# الإعدادات
# ====================================================

TOKEN = "8800842068:AAGFCkqAiSXBgIRAbo0_nl22xp0DGUqqH_4"
CHANNEL_USERNAME = "@xa_3g"
CHANNEL_LINK = "https://t.me/xa_3g"

bot = telebot.TeleBot(TOKEN)

DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

user_data = {}

# ====================================================
# دوال التحقق من الاشتراك
# ====================================================

def is_subscribed(user_id):
    """التحقق من اشتراك المستخدم في القناة"""
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def check_subscription(message):
    """التحقق من الاشتراك قبل تنفيذ أي أمر"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if not is_subscribed(user_id):
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("📢 اشترك في القناة", url=CHANNEL_LINK),
            InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub")
        )
        bot.send_message(
            chat_id,
            f"⚠️ **للوصول إلى بوت التحميل، يجب الاشتراك في قناتنا أولاً!**\n\n"
            f"📢 **قناتنا:** {CHANNEL_LINK}\n\n"
            f"بعد الاشتراك، اضغط على زر 'تحقق من الاشتراك'.",
            reply_markup=markup,
            parse_mode='Markdown'
        )
        return False
    return True

# ====================================================
# دوال التحميل
# ====================================================

def download_youtube(url):
    """تحميل من يوتيوب"""
    try:
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_FOLDER}/youtube_%(title)s_%(id)s.%(ext)s',
            'format': 'best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if not os.path.exists(filename):
                for file in os.listdir(DOWNLOAD_FOLDER):
                    if file.startswith(f"youtube_{info.get('title', '')[:30]}"):
                        return os.path.join(DOWNLOAD_FOLDER, file)
            return filename
    except Exception as e:
        return None

def download_tiktok(url):
    """تحميل من تيك توك"""
    try:
        api_url = "https://www.tikwm.com/api/"
        response = requests.post(api_url, data={'url': url})
        data = response.json()
        
        if data.get('code') == 0:
            video_url = data['data']['play']
            video_data = requests.get(video_url)
            filename = f"{DOWNLOAD_FOLDER}/tiktok_{int(time.time())}.mp4"
            with open(filename, 'wb') as f:
                f.write(video_data.content)
            return filename
        return None
    except Exception as e:
        return None

def download_instagram(url):
    """تحميل من إنستغرام"""
    try:
        api_url = f"https://instagram-video-downloader-download-instagram-videos.p.rapidapi.com/?url={url}"
        headers = {
            'x-rapidapi-key': 'your_rapidapi_key_here',
            'x-rapidapi-host': 'instagram-video-downloader-download-instagram-videos.p.rapidapi.com'
        }
        response = requests.get(api_url, headers=headers)
        data = response.json()
        
        if data.get('success'):
            video_url = data.get('media', {}).get('video', {}).get('url')
            if video_url:
                video_data = requests.get(video_url)
                filename = f"{DOWNLOAD_FOLDER}/instagram_{int(time.time())}.mp4"
                with open(filename, 'wb') as f:
                    f.write(video_data.content)
                return filename
        return None
    except Exception as e:
        return None

def download_facebook(url):
    """تحميل من فيسبوك"""
    try:
        api_url = "https://api.fdownloader.net/api/ajaxSearch"
        response = requests.post(api_url, data={'q': url})
        data = response.json()
        
        if data.get('success'):
            video_url = data.get('links', {}).get('Download High Quality', {}).get('url')
            if not video_url:
                video_url = data.get('links', {}).get('Download Low Quality', {}).get('url')
            
            if video_url:
                video_data = requests.get(video_url)
                filename = f"{DOWNLOAD_FOLDER}/facebook_{int(time.time())}.mp4"
                with open(filename, 'wb') as f:
                    f.write(video_data.content)
                return filename
        return None
    except Exception as e:
        return None

# ====================================================
# معالج الأزرار والرسائل
# ====================================================

@bot.message_handler(commands=['start', 'menu'])
def start(message):
    chat_id = message.chat.id
    
    # التحقق من الاشتراك
    if not check_subscription(message):
        return
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📹 يوتيوب", callback_data="youtube"),
        InlineKeyboardButton("🎵 تيك توك", callback_data="tiktok"),
        InlineKeyboardButton("📸 إنستغرام", callback_data="instagram"),
        InlineKeyboardButton("📘 فيسبوك", callback_data="facebook")
    )
    bot.send_message(
        chat_id,
        "📥 **بوت التحميل الشامل**\n\n"
        "اختر المنصة التي تريد التحميل منها، ثم أرسل الرابط.\n\n"
        "✅ يدعم: يوتيوب، تيك توك، إنستغرام، فيسبوك",
        reply_markup=markup,
        parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    
    # التحقق من الاشتراك
    if not is_subscribed(user_id):
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("📢 اشترك في القناة", url=CHANNEL_LINK),
            InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub")
        )
        bot.send_message(
            chat_id,
            f"⚠️ **يجب الاشتراك في القناة أولاً!**\n\n📢 {CHANNEL_LINK}",
            reply_markup=markup,
            parse_mode='Markdown'
        )
        return
    
    if call.data == "check_sub":
        if is_subscribed(user_id):
            bot.send_message(chat_id, "✅ **تم التحقق!** اشتراكك مؤكد.", parse_mode='Markdown')
            start(call.message)
        else:
            bot.send_message(chat_id, "❌ **لم يتم العثور على اشتراكك.**", parse_mode='Markdown')
        return
    
    platform = call.data
    
    platforms = {
        'youtube': 'يوتيوب',
        'tiktok': 'تيك توك',
        'instagram': 'إنستغرام',
        'facebook': 'فيسبوك'
    }
    
    bot.send_message(
        chat_id,
        f"📤 **أرسل رابط {platforms.get(platform, platform)}**\n\n"
        f"مثال: `https://www.{platform}.com/...`",
        parse_mode='Markdown'
    )
    
    user_data[chat_id] = {'platform': platform}

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # التحقق من الاشتراك
    if not is_subscribed(user_id):
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("📢 اشترك في القناة", url=CHANNEL_LINK),
            InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub")
        )
        bot.send_message(
            chat_id,
            f"⚠️ **يجب الاشتراك في القناة أولاً!**\n\n📢 {CHANNEL_LINK}",
            reply_markup=markup,
            parse_mode='Markdown'
        )
        return
    
    text = message.text.strip()
    
    if chat_id not in user_data:
        bot.send_message(chat_id, "⚠️ **يرجى اختيار المنصة أولاً من القائمة.**\nاستخدم /start", parse_mode='Markdown')
        return
    
    platform = user_data[chat_id]['platform']
    
    if not text.startswith('http'):
        bot.send_message(chat_id, "❌ **الرجاء إرسال رابط صحيح يبدأ بـ http**", parse_mode='Markdown')
        return
    
    status_msg = bot.send_message(chat_id, "⏳ **جاري التحميل...**", parse_mode='Markdown')
    
    filename = None
    if platform == 'youtube':
        filename = download_youtube(text)
    elif platform == 'tiktok':
        filename = download_tiktok(text)
    elif platform == 'instagram':
        filename = download_instagram(text)
    elif platform == 'facebook':
        filename = download_facebook(text)
    
    bot.delete_message(chat_id, status_msg.message_id)
    
    if filename and os.path.exists(filename):
        try:
            with open(filename, 'rb') as f:
                bot.send_video(chat_id, f, caption="✅ **تم التحميل بنجاح!**", parse_mode='Markdown')
            
            os.remove(filename)
            
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("📹 يوتيوب", callback_data="youtube"),
                InlineKeyboardButton("🎵 تيك توك", callback_data="tiktok"),
                InlineKeyboardButton("📸 إنستغرام", callback_data="instagram"),
                InlineKeyboardButton("📘 فيسبوك", callback_data="facebook")
            )
            bot.send_message(chat_id, "📥 **اختر منصة أخرى للتحميل:**", reply_markup=markup, parse_mode='Markdown')
            
        except Exception as e:
            bot.send_message(chat_id, f"❌ **حدث خطأ أثناء الإرسال:** {e}", parse_mode='Markdown')
            if os.path.exists(filename):
                os.remove(filename)
    else:
        bot.send_message(
            chat_id,
            "❌ **فشل التحميل!**\n\n"
            "تأكد من أن الرابط صحيح وأن الملف متاح.\n"
            "إذا استمرت المشكلة، جرب منصة أخرى.",
            parse_mode='Markdown'
        )

if __name__ == "__main__":
    print("🚀 بوت التحميل الشامل يعمل...")
    print(f"📢 القناة: {CHANNEL_LINK}")
    print("📹 يدعم: يوتيوب، تيك توك، إنستغرام، فيسبوك")
    bot.infinity_polling()