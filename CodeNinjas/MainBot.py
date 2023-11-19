import os
import sys
import time
import random
import base64
import requests as req
from datetime import datetime
from threading import Thread
from fake_useragent import UserAgent
from aiohttp import ClientSession
import disnake
from disnake.ext import commands, tasks
from disnake.ui import button, View, Modal
from disnake import AppCmdInter, ApplicationCommandInteraction ,Embed
from disnake.ui import TextInput
from disnake import TextInputStyle
import requests
import json
import asyncio
import qrcode
intents = disnake.Intents.default()
intents.typing = True
intents.messages = True
intents.members = True
intents.message_content = True  
intents.presences = False
intents.guilds = True
client = disnake.Client(intents=intents)

############################################################################################################ SetUPbot

bot = commands.Bot(command_prefix="!", intents=intents)

messages = [
    "เริ่มต้น /help 😘",
    "สำหรับเเอดมิน /setup 🎉",
    "คนทำบอทน่ารักมากครับ 😊"
]
message_index = 0  

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    update_message.start()  

@tasks.loop(seconds=3) 
async def update_message():
    global message_index
    await bot.change_presence(activity=disnake.Game(name=messages[message_index]))
    message_index = (message_index + 1) % len(messages) 

update_message.before_loop(bot.wait_until_ready)

config_file_path = 'config.json'
if os.path.exists(config_file_path):
    with open(config_file_path, 'r') as config_file:
        config = json.load(config_file)
else:
    print("Config file not found. Please create a config.json file.")

admin_ids = config.get("admin_ids", [])

############################################################################################################

@bot.event
async def on_member_join(member):
    channel_id = 1175830451366150164  # รหัสไอดีของช่องที่คุณต้องการให้บอทแจ้งเตือน
    channel = bot.get_channel(channel_id)
    channelM = bot.get_channel(1175832062104698911)
    channel_mention = channelM.mention

    # สร้าง Embed
    embed = disnake.Embed(title=f'ยินดีต้อนรับ {member.name} เข้าสู่เซิร์ฟเวอร์! 💖',
                        description=f'ยินดีต้อนรับครับ สามารถใช้บริการได้เต็มที่ และ อย่าลืมอ่านกฏกันด้วยนะครับ\n\n'
                                    f'อ่านกฏที่ห้อง : {channel_mention}',
                        color=0xCC0000)  # Embed color
    # เพิ่มรูปภาพ GIF
    embed.set_image(url='https://cdn.discordapp.com/attachments/1158812865898217522/1175834652297154692/standard_2.gif?ex=656cac5b&is=655a375b&hm=84f86fe4d84674b485cda31329cdd28e17cee6ef69d0da2a7fc14f105fb0a53e&')

    # เพิ่ม Icon ของคนที่เข้า
    embed.set_thumbnail(url=member.avatar.url)

    # ส่ง Embed ไปยังช่องที่กำหนด
    await channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    channel_id = 1175830581125328976  # รหัสไอดีของช่องที่คุณต้องการให้บอทแจ้งเตือน
    channel = bot.get_channel(channel_id)

    # สร้าง Embed
    embed = disnake.Embed(title=f'คุณ {member.name} ได้ออกจากเซิฟเวอร์! 🥲',
                          description='ใว้เจอกันใหม่นะครับ ขอบคุณที่เคยสนใจร้านของเรา',
                          color=0xBC57FF)  # สี Embed

    # เพิ่มรูปภาพ GIF
    embed.set_image(url='https://cdn.discordapp.com/attachments/1158812865898217522/1175836666733277184/standard_3.gif?ex=656cae3b&is=655a393b&hm=d1ec2bc0bb588fd70034ac2ec13d4a9434f35dcbf5c0a46c59a06d3ab5d6163e&')

    # เพิ่ม Icon ของคนที่เข้า
    embed.set_thumbnail(url=member.avatar.url)

    # ส่ง Embed ไปยังช่องที่กำหนด
    await channel.send(embed=embed)

#####################################################################################################################

class Modalsetpas(disnake.ui.Modal):
    def __init__(self, generated_code):
        components = [
            disnake.ui.TextInput(
                label=f"รหัสของคุณคือ : {generated_code}",
                placeholder="รหัสที่ท่านเห็น = ",
                custom_id="Password",
                max_length=20,
                style=disnake.TextInputStyle.short,
            ),
        ]
        super().__init__(title="ยืนยันตัวตน", components=components)
        self.generated_code = generated_code

    async def callback(self, inter: disnake.MessageInteraction):
        entered_code = inter.text_values["Password"]
        if entered_code == self.generated_code:
            # ทำงานเมื่อรหัสถูกต้อง
            role = disnake.utils.get(inter.guild.roles, name='〘🤵‍♂️〙ยืนยันตัวตนแล้ว')  # แทน YourRoleName ด้วยชื่อยศที่คุณต้องการให้
            if role:
                await inter.user.add_roles(role)
                await inter.response.send_message("ยืนยันตัวตนสำเร็จ", ephemeral=True)
            else:
                print("Error: Role not found.")
        else:
            # หากรหัสไม่ถูกต้อง
            await inter.response.send_message("รหัสไม่ถูกต้อง กรุณาลองอีกครั้ง", ephemeral=True)


class setpas(disnake.ui.View):
    def __init__(self, timeout=None):
        super().__init__(timeout=timeout)

    @disnake.ui.button(label='ยืนยันตัวตน', style=disnake.ButtonStyle.grey, emoji='<:SafetyJim:1175850271314808862>')
    async def ModalTokenChecker(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        generated_code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
        await interaction.response.send_modal(modal=Modalsetpas(generated_code))


@bot.command()
async def SetupSCN(inter: disnake.ApplicationCommandInteraction):
    user_id = inter.author.id
    if user_id in admin_ids:

        embed = disnake.Embed(
            title='กดปุ่มยืนยันตัวด้วยรหัส',
            color=disnake.Color.from_rgb(0, 0, 0),
            description="""```
กดปุ่มข้างล่าง

[+] เพื่อยืนยันตัวตน
```"""
        )
        embed.set_image(url='https://cdn.discordapp.com/attachments/1158812865898217522/1175850006515818566/standard_4.gif?ex=656cbaa7&is=655a45a7&hm=9f322994de16f3971a3c30589dbead84155a344966cc54b28f6b5c2c6eb666e0&')

        view = setpas()

        await inter.channel.purge()

        await inter.send(embed=embed, view=view)
    else:
        await inter.send("คุณไม่ได้รับอนุญาตให้ใช้คำสั่งนี้", ephemeral=True)

###################################################################################################################

@bot.command()
async def storeon(inter: disnake.ApplicationCommandInteraction):
    user_id = inter.author.id
    if user_id in admin_ids:
        embed = disnake.Embed(
            title='ร้านของเราเปิดแล้ว!',
            description='ยินดีต้อนรับทุกท่านที่มาเยี่ยมชม',
            color=disnake.Color.green()
        )
        embed.set_image(url='https://cdn.discordapp.com/attachments/1158812865898217522/1175857991770181715/standard_5.gif?ex=656cc217&is=655a4d17&hm=1ba4c37cbfe5bdb6335a004d43ff7f80293f6bf00f9c0ea7cdee981c1e66b137&')

        # แทนที่ 1175851927624491070 ด้วย ID ของห้องที่คุณต้องการ
        channel = bot.get_channel(1175851927624491070)
        
        await channel.send(embed=embed)
    else:
        await inter.send("คุณไม่ได้รับอนุญาตให้ใช้คำสั่งนี้", ephemeral=True)

@bot.command()
async def storeoff(inter: disnake.ApplicationCommandInteraction):
    user_id = inter.author.id
    if user_id in admin_ids:
        embed = disnake.Embed(
            title='ตอนนี้ร้านเราปิดทำการชั่วคราวครับผม!',
            description='ขออภัยในความไม่สะดวกนะที่นี้นะครับ',
            color=disnake.Color.red()
        )
        embed.set_image(url='https://cdn.discordapp.com/attachments/1158812865898217522/1175858011911237662/standard_6.gif?ex=656cc21c&is=655a4d1c&hm=1498df400fb6f5d19e1ae1ec17f10f07384e740282efcd14ee9a3fde32c3d3da&')

        # แทนที่ 1175851927624491070 ด้วย ID ของห้องที่คุณต้องการ
        channel = bot.get_channel(1175851927624491070)
        
        await channel.send(embed=embed)
    else:
        await inter.send("คุณไม่ได้รับอนุญาตให้ใช้คำสั่งนี้", ephemeral=True)

###################################################################################################################

@bot.command()
async def add_credit(inter: disnake.ApplicationCommandInteraction, member: disnake.Member, points: int):
    user_id = inter.author.id
    if user_id in admin_ids:
        user = member
        file_DatabasePoint = os.path.join('DataBase.json')
        
        with open(file_DatabasePoint, 'r') as file:
            database = json.load(file)

        user_id_str = str(user.id)
        
        if user_id_str not in database:
            database[user_id_str] = {"Point": 0}

        # ตรวจสอบว่ามีคีย์ "Point" ใน dictionary หรือไม่
        if "Point" not in database[user_id_str]:
            database[user_id_str]["Point"] = 0

        database[user_id_str]["Point"] += points

        with open(file_DatabasePoint, 'w') as file:
            json.dump(database, file, indent=4)

        total_points = database[user_id_str]['Point']
        await inter.send(f"เพิ่ม Points จำนวน {points:,} ให้กับ {user.display_name}. Point คงเหลือ: {total_points:,}")
    else:
        await inter.send("คุณไม่ได้รับอนุญาตให้ใช้คำสั่งนี้", ephemeral=True)

@bot.command(name="check_point", aliases=["cp"])
async def check_point(ctx, member: disnake.Member = None):
    if member is None:
        user_id_str = str(ctx.author.id)
        file_DatabasePoint = os.path.join('DataBase.json')

        with open(file_DatabasePoint, 'r') as file:
            database = json.load(file)

        if user_id_str in database and "Point" in database[user_id_str]:
            total_points = database[user_id_str]["Point"]
            formatted_points = "{:,}".format(total_points)
            await ctx.send(f"Points ของคุณ คือ: {formatted_points}")
        else:
            await ctx.send("ไม่พบข้อมูล Points สำหรับคุณ")
        return

    user_id_str = str(member.id)
    file_DatabasePoint = os.path.join('DataBase.json')

    with open(file_DatabasePoint, 'r') as file:
        database = json.load(file)

    if user_id_str in database and "Point" in database[user_id_str]:
        total_points = database[user_id_str]["Point"]
        formatted_points = "{:,}".format(total_points)
        await ctx.send(f"Points ของ {member.display_name} คือ: {formatted_points}")
    else:
        await ctx.send("ไม่พบข้อมูล Points สำหรับผู้ใช้นี้")

###################################################################################################################

bot.run('MTE3NTgzNzM2MTE4ODM4ODg2NA.Gi5YZ4.L51UjI6JgpTtCKfsKBZjMMhGtozaGLnFFh_2Go')