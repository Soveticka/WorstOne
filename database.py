import os
from dotenv import load_dotenv

import pymysql

from discord import Guild, Member, Emoji

load_dotenv()
ip = os.getenv('DB_IP')
port = int(os.getenv('DB_PORT'))
user = os.getenv('DB_USER')
passw = os.getenv('DB_PASSW')
database = os.getenv('DB_DATABASE')

db = pymysql.connect(host = ip,
                     port = port,
                     user = user,
                     password = passw,
                     database = database)

curs = db.cursor()

def registerToDB(guild: Guild):
    global lastID
    lastID = 0
    try:
        curs.execute("INSERT INTO Guild (guildID, guildName) VALUES ('{}','{}')".format(guild.id, guild.name))
        db.commit()
    except:
        db.rollback()

    try:
        curs.execute("SELECT * FROM Guild ORDER BY ID DESC LIMIT 1")
        data = curs.fetchall()
        lastID = data[0][0]
        db.commit()
    except:
        db.rollback()
    
    for member in guild.members:
        try:
            curs.execute("INSERT INTO User (userID, userName, Guild_id) VALUES ('{}','{}',{})".format(member.id, member.name, lastID))
            db.commit()
        except:
            db.rollback()
        
    for emoji in guild.emojis:
        if emoji.animated is True:
            gID = "<a:{}:{}>".format(emoji.name,emoji.id)
        else:
            gID = "<:{}:{}>".format(emoji.name,emoji.id)

        name = ":{}:".format(emoji.name)
        try:
            curs.execute("INSERT INTO Emoji (emojiGID, emojiName, Guild_id, emojiID) VALUES ('{}','{}',{}, '{}')".format(gID, name, lastID, emoji.id))
            db.commit()
        except:
            db.rollback()


def getGuildID(guildID: str):
    try:
        curs.execute("SELECT * FROM Guild WHERE guildID = {}".format(guildID))
        data = curs.fetchall()
        id = data[0][0]
        db.commit()
        return id
    except:
        db.rollback()


def addUser(user: Member):
    guildID = getGuildID(user.guild.id)
    try:
        curs.execute("INSERT INTO User (userID, userName, Guild_id) VALUES ('{}','{}',{}".format(user.id, user.name, guildID))
        db.commit()
    except:
        db.rollback()


def addEmoji(guild: Guild, emoji: Emoji):
    guildID = getGuildID(guild.id)

    if emoji.animated is True:
        gID = "<a:{}:{}>".format(emoji.name, emoji.id)
    else:
        gID = "<:{}:{}>".format(emoji.name, emoji.id)

    name = ":{}:".format(emoji.name)

    try:
        curs.execute("SELECT * FROM Emoji WHERE emojiID = '{}'".format(emoji.id))
        data = curs.fetchall()
        db.commit()
        try:
            if len(data) >= 1:
                curs.execute("UPDATE Emoji SET emojiGID='{}', emojiName='{}' WHERE emojiID='{}'".format(gID, name, emoji.id))
            else:
                curs.execute("INSERT INTO Emoji (emojiGID, emojiName, Guild_id, emojiID) VALUES ('{}', '{}', {}, '{}')".format(gID, name, guildID, emoji.id))
            db.commit()
        except:
            db.rollback()
    except:
        db.rollback()


def removeEmoji(emoji: Emoji):
    if emoji.animated is True:
        gID = "<a:{}:{}>".format(emoji.name, emoji.id)
    else:
        gID = "<:{}:{}>".format(emoji.name, emoji.id)

    try:
        curs.execute("DELETE FROM Emoji WHERE emojiGID='{}'".format(gID))
        db.commit()
    except:
        db.rollback()


def removeFromGuild(guild: Guild):
    try:
        curs.execute("DELETE FROM Guild WHERE guildID='{}'".format(guild.id))
        db.commit()
    except:
        db.rollback()


def query(sql: str):
    try:
        curs.execute(sql)
        data = curs.fetchall()
        return data
    except:
        db.rollback()
