#  This file is part of the VIDEOconvertor distribution.
#  Copyright (c) 2021 vasusen-code ; All rights reserved. 
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, version 3.
#
#  This program is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  General Public License for more details.
#
#  License can be found in < https://github.com/vasusen-code/VIDEOconvertor/blob/public/LICENSE> .

import os, time, requests

from datetime import datetime as dt
from telethon import events
from telethon.tl.types import DocumentAttributeVideo
from ethon.telefunc import fast_download, fast_upload
from ethon.pyutils import rename
from ethon.pyfunc import video_metadata

from .. import Drone, BOT_UN, MONGODB_URI

from main.Database.database import Database
from LOCAL.localisation import JPG3 as t
from LOCAL.localisation import SUPPORT_LINK

async def media_rename(event, msg, new_name):
    edit = await event.client.send_message(event.chat_id, 'Trying to process.', reply_to=msg.id)
    db = Database(MONGODB_URI, 'videoconvertor')
    T = await db.get_thumb(event.sender_id)
    if T is not None:
        ext = T.split("/")[4]
        r = requests.get(T, allow_redirects=True)
        path = dt.now().isoformat("_", "seconds") + ext
        open(path , 'wb').write(r.content)
        THUMB = path
    else:
        THUMB = t
    Drone = event.client
    DT = time.time()
    file = msg.media.document if hasattr(msg.media, "document") else msg.media
    mime = msg.file.mime_type
    if 'mp4' in mime:
        name = "media_" + dt.now().isoformat("_", "seconds") + ".mp4"
        out = f"{new_name}.mp4"
    elif msg.video:
        name = "media_" + dt.now().isoformat("_", "seconds") + ".mp4"
        out = f"{new_name}.mp4"
    elif 'x-matroska' in mime:
        name = "media_" + dt.now().isoformat("_", "seconds") + ".mkv"
        out = f"{new_name}.mkv"
    elif 'webm' in mime:
        name = "media_" + dt.now().isoformat("_", "seconds") + ".webm"
        out = f"{new_name}.webm"
    elif 'zip' in mime:
        name = "media_" + dt.now().isoformat("_", "seconds") + ".zip"
        out = f"{new_name}.zip"
    elif 'jpg' in mime:
        name = "media_" + dt.now().isoformat("_", "seconds") + ".jpg"
        out = f"{new_name}.jpg"
    elif 'png' in mime:
        name = "media_" + dt.now().isoformat("_", "seconds") + ".png"
        out = f"{new_name}.png"
    elif 'pdf' in mime:
        name = "media_" + dt.now().isoformat("_", "seconds") + ".pdf"
        out = f"{new_name}.pdf"
    elif 'rar' in mime:
        name = "media_" + dt.now().isoformat("_", "seconds") + ".rar"
        out = f"{new_name}.rar"
    elif 'mp3' in mime:
        name = "media_" + dt.now().isoformat("_", "seconds") + ".mp3"
        out = f"{new_name}.mp3"
    elif 'ogg' in mime:
        name = "media_" + dt.now().isoformat("_", "seconds") + ".ogg"
        out = f"{new_name}.ogg"
    elif 'flac' in mime:
        name = "media_" + dt.now().isoformat("_", "seconds") + ".flac"
        out = f"{new_name}.flac"
    elif 'wav' in mime:
        name = "media_" + dt.now().isoformat("_", "seconds") + ".wav"
        out = f"{new_name}.wav"
    elif 'webp' in mime:
        name = "media_" + dt.now().isoformat("_", "seconds") + ".webp"
        out = f"{new_name}.webp"
    elif default_name := msg.file.name:
        try:
            name = msg.file.name
            ext = (name.split("."))[1]
            out = f"{new_name}.{ext}"
            await fast_download(name, file, Drone, edit, DT, "**DOWNLOADING:**")
            rename(name, out)
            UT = time.time()
            uploader = await fast_upload(out, out, UT, Drone, edit, '**UPLOADING:**')
            net_time = round(DT - UT)
            await Drone.send_file(event.chat_id, uploader, caption=f"**Renamed by** : @{BOT_UN}\n\nTotal time:{net_time} seconds.", thumb=THUMB, force_document=True)
        except Exception as e:
            await edit.edit(f"An error occured.\n\nContact [SUPPORT]({SUPPORT_LINK})", link_preview=False)
            print(e)
            return
    else:
        await edit.edit("Failed fetching extension of your file.")
    try:  
        await fast_download(name, file, Drone, edit, DT, "**DOWNLOADING:**")
    except Exception as e:
        await edit.edit(f"An error occured while downloading.\n\nContact [SUPPORT]({SUPPORT_LINK})", link_preview=False)
        print(e)
        return
    await edit.edit("Renaming.")
    try:
        rename(name, out)
    except Exception as e:
        await edit.edit(f"An error occured while renaming.\n\nContact [SUPPORT]({SUPPORT_LINK})", link_preview=False)
        print(e)
        return
    try:
        if 'video' in mime and ('mp4' in mime or msg.video):
            metadata = video_metadata(out)
            width = metadata["width"]
            height = metadata["height"]
            duration = metadata["duration"]
            attributes = [DocumentAttributeVideo(duration=duration, w=width, h=height, supports_streaming=True)]
            UT = time.time()
            uploader = await fast_upload(f'{out}', f'{out}', UT, Drone, edit, '**UPLOADING:**')
            net_time = round(DT - UT)
            await Drone.send_file(event.chat_id, uploader, caption=f"**Renamed by** : @{BOT_UN}\n\nTotal time:{net_time} seconds.", thumb=THUMB, attributes=attributes, force_document=False)
        else:
            UT = time.time()
            uploader = await fast_upload(out, out, UT, Drone, edit, '**UPLOADING:**')
            net_time = round(DT - UT)
            await Drone.send_file(event.chat_id, uploader, caption=f"**Renamed by** : @{BOT_UN}\n\nTotal time:{net_time} seconds.", thumb=THUMB, force_document=True)
    except Exception as e:
        await edit.edit(f"An error occured while uploading.\n\nContact [SUPPORT]({SUPPORT_LINK})", link_preview=False)
        print(e)
        return
    await edit.delete()
    os.remove(out)
