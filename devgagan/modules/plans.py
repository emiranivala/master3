#devgaganin

from datetime import timedelta
import pytz
import datetime, time
from devgagan import app
from config import OWNER_ID
from devgagan.core.func import get_seconds
from devgagan.core.mongo import plans_db  
from pyrogram import filters 

@app.on_message(filters.command("rem") & filters.user(OWNER_ID))
async def remove_premium(client, message):
    if len(message.command) == 2:
        user_id = int(message.command[1])  
        user = await client.get_users(user_id)
        data = await plans_db.check_premium(user_id)  
        
        if data and data.get("_id"):
            await plans_db.remove_premium(user_id)
            await message.reply_text("User removed successfully!")
            await client.send_message(
                chat_id=user_id,
                text=f"Hey {user.mention},\n\nYour premium access has been removed.\nThank you for using our service. 😊"
            )
        else:
            await message.reply_text("Unable to remove user!\nAre you sure it was a premium user ID?")
    else:
        await message.reply_text("Usage: /rem user_id") 

@app.on_message(filters.command("myplan"))
async def myplan(client, message):
    user_id = message.from_user.id
    user = message.from_user.mention
    data = await plans_db.check_premium(user_id)  
    if data and data.get("expire_date"):
        expiry = data.get("expire_date")
        expiry_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata"))
        expiry_str_in_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y\n⏱️ Expiry Time: %I:%M:%S %p")            
        
        current_time = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
        time_left = expiry_ist - current_time
            
        days = time_left.days
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
            
        time_left_str = f"{days} days, {hours} hours, {minutes} minutes"
        await message.reply_text(f"⚜️ Premium User Data:\n\n👤 User: {user}\n⚡ User ID: <code>{user_id}</code>\n⏰ Time Left: {time_left_str}\n⌛ Expiry Date: {expiry_str_in_ist}")   
    else:
        await message.reply_text(f"Hey {user},\n\nYou do not have any active premium plans.")

@app.on_message(filters.command("check") & filters.user(OWNER_ID))
async def get_premium(client, message):
    if len(message.command) == 2:
        user_id = int(message.command[1])
        user = await client.get_users(user_id)
        data = await plans_db.check_premium(user_id)  
        if data and data.get("expire_date"):
            expiry = data.get("expire_date") 
            expiry_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata"))
            expiry_str_in_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y\n⏱️ Expiry Time: %I:%M:%S %p")            
            
            current_time = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
            time_left = expiry_ist - current_time
            
            days = time_left.days
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            time_left_str = f"{days} days, {hours} hours, {minutes} minutes"
            await message.reply_text(f"⚜️ Premium User Data:\n\n👤 User: {user.mention}\n⚡ User ID: <code>{user_id}</code>\n⏰ Time Left: {time_left_str}\n⌛ Expiry Date: {expiry_str_in_ist}")
        else:
            await message.reply_text("No premium data of the user was found in the database!")
    else:
        await message.reply_text("Usage: /check user_id")

@app.on_message(filters.command("add") & filters.user(OWNER_ID))
async def give_premium_cmd_handler(client, message):
    if len(message.command) == 4:
        time_zone = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
        current_time = time_zone.strftime("%d-%m-%Y\n⏱️ Joining Time: %I:%M:%S %p") 
        user_id = int(message.command[1])
        user = await client.get_users(user_id)
        time = message.command[2] + " " + message.command[3]
        seconds = await get_seconds(time)
        if seconds > 0:
            expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)  
            await plans_db.add_premium(user_id, expiry_time)  
            data = await plans_db.check_premium(user_id)
            expiry = data.get("expire_date")   
            expiry_str_in_ist = expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y\n⏱️ Expiry Time: %I:%M:%S %p")         
            await message.reply_text(f"Premium added successfully ✅\n\n👤 User: {user.mention}\n⚡ User ID: <code>{user_id}</code>\n⏰ Premium Access: <code>{time}</code>\n\n⏳ Joining Date: {current_time}\n\n⌛ Expiry Date: {expiry_str_in_ist} \n\nAll Set ✅", disable_web_page_preview=True)
            await client.send_message(
                chat_id=user_id,
                text=f"👋 Hey {user.mention},\nThank you for purchasing premium.\nEnjoy! ✨🎉\n\n⏰ Premium Access: <code>{time}</code>\n⏳ Joining Date: {current_time}\n\n⌛ Expiry Date: {expiry_str_in_ist}", disable_web_page_preview=True              
            )                    
        else:
            await message.reply_text("Invalid time format. Please use '1 day for days', '1 hour for hours', or '1 min for minutes', or '1 month for months' or '1 year for year'")
    else:
        await message.reply_text("Usage : /add user_id time (e.g., '1 day for days', '1 hour for hours', or '1 min for minutes', or '1 month for months' or '1 year for year')")
