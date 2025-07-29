import asyncio
import aiohttp
import aiofiles
from typing import List, Optional, Dict, Any, Literal, Callable, Union
from .exceptions import APIRequestError
from .adaptorrubka import Client as Client_get
from .logger import logger
try:
    from .context import Message, InlineMessage
except (ImportError, ModuleNotFoundError):
    # اگر به صورت مستقیم اجرا شود، از این حالت استفاده می‌کند
    from context import Message, InlineMessage
from pathlib import Path
import time
import datetime
import tempfile
from tqdm import tqdm
import os
import sys
import subprocess

API_URL = "https://botapi.rubika.ir/v3"

def install_package(package_name: str) -> bool:
    """Installs a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

def get_importlib_metadata():
    """Dynamically imports and returns metadata functions from importlib."""
    try:
        from importlib.metadata import version, PackageNotFoundError
        return version, PackageNotFoundError
    except ImportError:
        if install_package("importlib-metadata"):
            try:
                from importlib_metadata import version, PackageNotFoundError
                return version, PackageNotFoundError
            except ImportError:
                return None, None
        return None, None

version, PackageNotFoundError = get_importlib_metadata()

def get_installed_version(package_name: str) -> Optional[str]:
    """Gets the installed version of a package."""
    if version is None:
        return "unknown"
    try:
        return version(package_name)
    except PackageNotFoundError:
        return None

async def get_latest_version(package_name: str) -> Optional[str]:
    """Fetches the latest version of a package from PyPI asynchronously."""
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data.get("info", {}).get("version")
    except Exception:
        return None

async def check_rubka_version():
    """Checks for outdated 'rubka' package and warns the user."""
    package_name = "rubka"
    installed_version = get_installed_version(package_name)
    if installed_version is None:
        return
    
    latest_version = await get_latest_version(package_name)
    if latest_version is None:
        return
    
    if installed_version != latest_version:
        print(f"\n\nWARNING: Your installed version of '{package_name}' is OUTDATED and may cause errors or security risks!")
        print(f"Installed version : {installed_version}")
        print(f"Latest available version : {latest_version}")
        print(f"Please update IMMEDIATELY by running:")
        print(f"\npip install {package_name}=={latest_version}\n")
        print("Not updating may lead to malfunctions or incompatibility.")
        print("To see new methods : @rubka_library\n\n")

# To run the check at startup in an async context
# asyncio.run(check_rubka_version())

def show_last_six_words(text: str) -> str:
    """Returns the last 6 characters of a stripped string."""
    text = text.strip()
    return text[-6:]


class Robot:
    """
    Main async class to interact with Rubika Bot API.
    Initialized with a bot token.
    """

    def __init__(self, token: str, session_name: str = None, auth: str = None, Key: str = None, platform: str = "web", web_hook: str = None, timeout: int = 10, show_progress: bool = False):
        self.token = token
        self._inline_query_handlers: List[dict] = []
        self.timeout = timeout
        self.auth = auth
        self.show_progress = show_progress
        self.session_name = session_name
        self.Key = Key
        self.platform = platform
        self.web_hook = web_hook
        self._offset_id: Optional[str] = None
        self._aiohttp_session: aiohttp.ClientSession = None
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self._callback_handler = None
        self._message_handler = None
        self._inline_query_handler = None
        self._callback_handlers: List[dict] = []
        self._processed_message_ids: Dict[str, float] = {}

        logger.info(f"Initialized RubikaBot with token: {token[:8]}***")
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Lazily creates and returns the aiohttp session."""
        if self._aiohttp_session is None or self._aiohttp_session.closed:
            self._aiohttp_session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        return self._aiohttp_session
        
    async def _initialize_webhook(self):
        """Initializes and sets the webhook endpoint if provided."""
        if not self.web_hook:
            return
        
        session = await self._get_session()
        try:
            async with session.get(self.web_hook, timeout=self.timeout) as response:
                response.raise_for_status()
                data = await response.json()
                print(data)
                json_url = data.get('url', self.web_hook)
                print(self.web_hook)

            for endpoint_type in [
                    "ReceiveUpdate",
                    "ReceiveInlineMessage",
                    "ReceiveQuery",
                    "GetSelectionItem",
                    "SearchSelectionItems"
                ]:
                result = await self.update_bot_endpoint(self.web_hook, endpoint_type)
                print(result)
            self.web_hook = json_url
        except Exception as e:
            logger.error(f"Failed to set webhook from {self.web_hook}: {e}")
            self.web_hook = None


    async def _post(self, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{API_URL}/{self.token}/{method}"
        session = await self._get_session()
        try:
            async with session.post(url, json=data) as response:
                response.raise_for_status()
                try:
                    json_resp = await response.json()
                except aiohttp.ContentTypeError:
                    text_resp = await response.text()
                    logger.error(f"Invalid JSON response from {method}: {text_resp}")
                    raise APIRequestError(f"Invalid JSON response: {text_resp}")
                
                if method != "getUpdates":
                    logger.debug(f"API Response from {method}: {json_resp}")
                
                return json_resp
        except aiohttp.ClientError as e:
            logger.error(f"API request failed: {e}")
            raise APIRequestError(f"API request failed: {e}") from e

    async def get_me(self) -> Dict[str, Any]:
        """Get info about the bot itself."""
        return await self._post("getMe", {})

    def on_message(self, filters: Optional[Callable[[Message], bool]] = None, commands: Optional[List[str]] = None):
        def decorator(func: Callable[[Any, Message], None]):
            self._message_handler = {
                "func": func,
                "filters": filters,
                "commands": commands
            }
            return func
        return decorator

    def on_callback(self, button_id: Optional[str] = None):
        def decorator(func: Callable[[Any, Message], None]):
            if not hasattr(self, "_callback_handlers"):
                self._callback_handlers = []
            self._callback_handlers.append({
                "func": func,
                "button_id": button_id
            })
            return func
        return decorator

    async def _handle_inline_query(self, inline_message: InlineMessage):
        aux_button_id = inline_message.aux_data.button_id if inline_message.aux_data else None

        for handler in self._inline_query_handlers:
            if handler["button_id"] is None or handler["button_id"] == aux_button_id:
                try:
                    await handler["func"](self, inline_message)
                except Exception as e:
                    print(f"Error in inline query handler: {e}")

    def on_inline_query(self, button_id: Optional[str] = None):
        def decorator(func: Callable[[Any, InlineMessage], None]):
            self._inline_query_handlers.append({
                "func": func,
                "button_id": button_id
            })
            return func
        return decorator

    async def _process_update(self, update: dict):
        if update.get("type") == "ReceiveQuery":
            msg = update.get("inline_message", {})
            context = InlineMessage(bot=self, raw_data=msg)
            asyncio.create_task(self._handle_inline_query(context))
            return

        if update.get("type") == "NewMessage":
            msg = update.get("new_message", {})
            try:
                if msg.get("time") and (time.time() - float(msg["time"])) > 20:
                    return
            except (ValueError, TypeError):
                return
                
            context = Message(bot=self, 
                              chat_id=update.get("chat_id"), 
                              message_id=msg.get("message_id"), 
                              sender_id=msg.get("sender_id"), 
                              text=msg.get("text"), 
                              raw_data=msg)
            
            if context.aux_data and self._callback_handlers:
                for handler in self._callback_handlers:
                    if not handler["button_id"] or context.aux_data.button_id == handler["button_id"]:
                        asyncio.create_task(handler["func"](self, context))
                        return

            if self._message_handler:
                handler_info = self._message_handler
                if handler_info["commands"]:
                    if not context.text or not context.text.startswith("/"):
                        return
                    parts = context.text.split()
                    cmd = parts[0][1:]
                    if cmd not in handler_info["commands"]:
                        return
                    context.args = parts[1:]
                
                if handler_info["filters"] and not handler_info["filters"](context):
                    return

                asyncio.create_task(handler_info["func"](self, context))

    async def get_updates(self, offset_id: Optional[str] = None, limit: Optional[int] = None) -> Dict[str, Any]:
        data = {}
        if offset_id: data["offset_id"] = offset_id
        if limit: data["limit"] = limit
        return await self._post("getUpdates", data)

    async def update_webhook(self, offset_id: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        session = await self._get_session()
        params = {}
        if offset_id: params['offset_id'] = offset_id
        if limit: params['limit'] = limit
        async with session.get(self.web_hook, params=params) as response:
            response.raise_for_status()
            # وب‌هوک باید لیستی از رویدادها را برگرداند
            return await response.json()

    def _is_duplicate(self, message_id: str, max_age_sec: int = 300) -> bool:
        now = time.time()
        expired = [mid for mid, ts in self._processed_message_ids.items() if now - ts > max_age_sec]
        for mid in expired:
            del self._processed_message_ids[mid]

        if message_id in self._processed_message_ids:
            return True

        self._processed_message_ids[message_id] = now
        return False

    async def run(self):
        """
        Starts the bot.
        This method is now corrected to handle webhook updates similarly to the original synchronous code.
        """
        await check_rubka_version()
        await self._initialize_webhook()
        print("Bot started running...")

        try:
            while True:
                try:
                    if self.web_hook:
                        # ----- منطق وب‌هوک (اصلاح شده) -----
                        # آپدیت‌ها مستقیما از وب‌هوک گرفته و پردازش می‌شوند
                        webhook_data = await self.update_webhook()
                        if isinstance(webhook_data, list):
                            for item in webhook_data:
                                data = item.get("data", {})

                                received_at_str = item.get("received_at")
                                if received_at_str:
                                    try:
                                        received_at_ts = datetime.datetime.strptime(received_at_str, "%Y-%m-%d %H:%M:%S").timestamp()
                                        if time.time() - received_at_ts > 20:
                                            continue
                                    except (ValueError, TypeError):
                                        pass  # رد شدن در صورت فرمت اشتباه زمان

                                update = None
                                if "update" in data:
                                    update = data["update"]
                                elif "inline_message" in data:
                                    update = {"type": "ReceiveQuery", "inline_message": data["inline_message"]}
                                else:
                                    continue

                                message_id = None
                                if update.get("type") == "NewMessage":
                                    message_id = update.get("new_message", {}).get("message_id")
                                elif update.get("type") == "ReceiveQuery":
                                    message_id = update.get("inline_message", {}).get("message_id")
                                elif "message_id" in update:
                                    message_id = update.get("message_id")
                                
                                if message_id and not self._is_duplicate(str(message_id)):
                                    await self._process_update(update)

                    else:
                        # ----- منطق Polling (بدون تغییر) -----
                        get_updates_response = await self.get_updates(offset_id=self._offset_id, limit=100)
                        if get_updates_response and get_updates_response.get("data"):
                            updates = get_updates_response["data"].get("updates", [])
                            self._offset_id = get_updates_response["data"].get("next_offset_id", self._offset_id)

                            for update in updates:
                                message_id = None
                                if update.get("type") == "NewMessage":
                                    message_id = update.get("new_message", {}).get("message_id")
                                elif update.get("type") == "ReceiveQuery":
                                    message_id = update.get("inline_message", {}).get("message_id")
                                elif "message_id" in update:
                                    message_id = update.get("message_id")
                                
                                if message_id and not self._is_duplicate(str(message_id)):
                                    await self._process_update(update)

                    await asyncio.sleep(0.1) # وقفه کوتاه برای جلوگیری از مصرف CPU
                except Exception as e:
                    print(f"❌ Error in run loop: {e}")
                    await asyncio.sleep(5) # وقفه طولانی‌تر در صورت بروز خطا
        finally:
            if self._aiohttp_session:
                await self._aiohttp_session.close()
            print("Bot stopped and session closed.")
            
    async def send_message(self, chat_id: str, text: str, chat_keypad: Optional[Dict[str, Any]] = None, inline_keypad: Optional[Dict[str, Any]] = None, disable_notification: bool = False, reply_to_message_id: Optional[str] = None, chat_keypad_type: Optional[Literal["New", "Removed"]] = None) -> Dict[str, Any]:
        payload = {"chat_id": chat_id, "text": text, "disable_notification": disable_notification}
        if chat_keypad: payload["chat_keypad"] = chat_keypad
        if inline_keypad: payload["inline_keypad"] = inline_keypad
        if reply_to_message_id: payload["reply_to_message_id"] = reply_to_message_id
        if chat_keypad_type: payload["chat_keypad_type"] = chat_keypad_type
        return await self._post("sendMessage", payload)

    def _get_client(self) -> Client_get:
        if self.session_name:
            return Client_get(self.session_name, self.auth, self.Key, self.platform)
        else:
            return Client_get(show_last_six_words(self.token), self.auth, self.Key, self.platform)
            
    async def check_join(self, channel_guid: str, chat_id: str = None) -> Union[bool, list[str]]:
        client = self._get_client()

        if chat_id:
            chat_info_data = await self.get_chat(chat_id)
            chat_info = chat_info_data.get('data', {}).get('chat', {})
            username = chat_info.get('username')
            user_id = chat_info.get('user_id')
            
            # Since client methods are sync, run them in a thread pool
            if username:
                result = await asyncio.to_thread(self.get_all_member, channel_guid, search_text=username)
                members = result.get('in_chat_members', [])
                return any(m.get('username') == username for m in members)
            elif user_id:
                member_guids = await asyncio.to_thread(client.get_all_members, channel_guid, just_get_guids=True)
                return user_id in member_guids
        return False

    def get_all_member(self, channel_guid: str, search_text: str = None, start_id: str = None, just_get_guids: bool = False):
        # This is a sync method that will be called with asyncio.to_thread
        client = self._get_client()
        return client.get_all_members(channel_guid, search_text, start_id, just_get_guids)

    async def send_poll(self, chat_id: str, question: str, options: List[str]) -> Dict[str, Any]:
        return await self._post("sendPoll", {"chat_id": chat_id, "question": question, "options": options})

    async def send_location(self, chat_id: str, latitude: str, longitude: str, disable_notification: bool = False, inline_keypad: Optional[Dict[str, Any]] = None, reply_to_message_id: Optional[str] = None, chat_keypad_type: Optional[Literal["New", "Removed"]] = None) -> Dict[str, Any]:
        payload = {"chat_id": chat_id, "latitude": latitude, "longitude": longitude, "disable_notification": disable_notification}
        if inline_keypad: payload["inline_keypad"] = inline_keypad
        if reply_to_message_id: payload["reply_to_message_id"] = reply_to_message_id
        if chat_keypad_type: payload["chat_keypad_type"] = chat_keypad_type
        return await self._post("sendLocation", {k: v for k, v in payload.items() if v is not None})

    async def send_contact(self, chat_id: str, first_name: str, last_name: str, phone_number: str) -> Dict[str, Any]:
        return await self._post("sendContact", {"chat_id": chat_id, "first_name": first_name, "last_name": last_name, "phone_number": phone_number})

    async def get_chat(self, chat_id: str) -> Dict[str, Any]:
        return await self._post("getChat", {"chat_id": chat_id})

    async def upload_media_file(self, upload_url: str, name: str, path: Union[str, Path]) -> str:
        is_temp_file = False
        session = await self._get_session()

        if isinstance(path, str) and path.startswith("http"):
            async with session.get(path) as response:
                if response.status != 200:
                    raise Exception(f"Failed to download file from URL ({response.status})")
                
                content = await response.read()
                
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_file.write(content)
                    path = temp_file.name
                    is_temp_file = True

        file_size = os.path.getsize(path) # Note: os.path.getsize is sync, but fast enough for most cases. aiofiles can be used for async alternative if needed on huge file lists.

        progress_bar = tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024, desc=f'Uploading : {name}', bar_format='{l_bar}{bar:100}{r_bar}', colour='cyan', disable=not self.show_progress)

        async def file_progress_generator(file_path, chunk_size=8192):
            async with aiofiles.open(file_path, 'rb') as f:
                while True:
                    chunk = await f.read(chunk_size)
                    if not chunk:
                        break
                    progress_bar.update(len(chunk))
                    yield chunk
        
        data = aiohttp.FormData()
        data.add_field('file', file_progress_generator(path), filename=name, content_type='application/octet-stream')

        async with session.post(upload_url, data=data) as response:
            progress_bar.close()
            if response.status != 200:
                raise Exception(f"Upload failed ({response.status}): {await response.text()}")
            
            json_data = await response.json()
            if is_temp_file:
                os.remove(path)
            
            return json_data.get('data', {}).get('file_id')

    async def get_upload_url(self, media_type: Literal['File', 'Image', 'Voice', 'Music', 'Gif', 'Video']) -> str:
        allowed = ['File', 'Image', 'Voice', 'Music', 'Gif', 'Video']
        if media_type not in allowed:
            raise ValueError(f"Invalid media type. Must be one of {allowed}")
        result = await self._post("requestSendFile", {"type": media_type})
        return result.get("data", {}).get("upload_url")

    async def _send_uploaded_file(self, chat_id: str, file_id: str, text: Optional[str] = None, chat_keypad: Optional[Dict[str, Any]] = None, inline_keypad: Optional[Dict[str, Any]] = None, disable_notification: bool = False, reply_to_message_id: Optional[str] = None, chat_keypad_type: Optional[Literal["New", "Removed", "None"]] = "None") -> Dict[str, Any]:
        payload = {"chat_id": chat_id, "file_id": file_id, "text": text, "disable_notification": disable_notification, "chat_keypad_type": chat_keypad_type}
        if chat_keypad: payload["chat_keypad"] = chat_keypad
        if inline_keypad: payload["inline_keypad"] = inline_keypad
        if reply_to_message_id: payload["reply_to_message_id"] = str(reply_to_message_id)
        return await self._post("sendFile", payload)

    async def _send_file_generic(self, media_type, chat_id, path, file_id, text, file_name, inline_keypad, chat_keypad, reply_to_message_id, disable_notification, chat_keypad_type):
        if path:
            file_name = file_name or Path(path).name
            upload_url = await self.get_upload_url(media_type)
            file_id = await self.upload_media_file(upload_url, file_name, path)
        if not file_id:
            raise ValueError("Either path or file_id must be provided.")
        return await self._send_uploaded_file(chat_id=chat_id, file_id=file_id, text=text, inline_keypad=inline_keypad, chat_keypad=chat_keypad, reply_to_message_id=reply_to_message_id, disable_notification=disable_notification, chat_keypad_type=chat_keypad_type)

    async def send_document(self, chat_id: str, path: Optional[Union[str, Path]] = None, file_id: Optional[str] = None, text: Optional[str] = None, file_name: Optional[str] = None, inline_keypad: Optional[Dict[str, Any]] = None, chat_keypad: Optional[Dict[str, Any]] = None, reply_to_message_id: Optional[str] = None, disable_notification: bool = False, chat_keypad_type: Optional[Literal["New", "Removed", "None"]] = "New") -> Dict[str, Any]:
        return await self._send_file_generic("File", chat_id, path, file_id, text, file_name, inline_keypad, chat_keypad, reply_to_message_id, disable_notification, chat_keypad_type)
        
    async def send_music(self, chat_id: str, path: Optional[Union[str, Path]] = None, file_id: Optional[str] = None, text: Optional[str] = None, file_name: Optional[str] = None, inline_keypad: Optional[Dict[str, Any]] = None, chat_keypad: Optional[Dict[str, Any]] = None, reply_to_message_id: Optional[str] = None, disable_notification: bool = False, chat_keypad_type: Optional[Literal["New", "Removed", "None"]] = "New") -> Dict[str, Any]:
        return await self._send_file_generic("Music", chat_id, path, file_id, text, file_name, inline_keypad, chat_keypad, reply_to_message_id, disable_notification, chat_keypad_type)

    async def send_video(self, chat_id: str, path: Optional[Union[str, Path]] = None, file_id: Optional[str] = None, text: Optional[str] = None, file_name: Optional[str] = None, inline_keypad: Optional[Dict[str, Any]] = None, chat_keypad: Optional[Dict[str, Any]] = None, reply_to_message_id: Optional[str] = None, disable_notification: bool = False, chat_keypad_type: Optional[Literal["New", "Removed", "None"]] = "New") -> Dict[str, Any]:
        return await self._send_file_generic("Video", chat_id, path, file_id, text, file_name, inline_keypad, chat_keypad, reply_to_message_id, disable_notification, chat_keypad_type)

    async def send_voice(self, chat_id: str, path: Optional[Union[str, Path]] = None, file_id: Optional[str] = None, text: Optional[str] = None, file_name: Optional[str] = None, inline_keypad: Optional[Dict[str, Any]] = None, chat_keypad: Optional[Dict[str, Any]] = None, reply_to_message_id: Optional[str] = None, disable_notification: bool = False, chat_keypad_type: Optional[Literal["New", "Removed", "None"]] = "New") -> Dict[str, Any]:
        return await self._send_file_generic("Voice", chat_id, path, file_id, text, file_name, inline_keypad, chat_keypad, reply_to_message_id, disable_notification, chat_keypad_type)

    async def send_image(self, chat_id: str, path: Optional[Union[str, Path]] = None, file_id: Optional[str] = None, text: Optional[str] = None, file_name: Optional[str] = None, inline_keypad: Optional[Dict[str, Any]] = None, chat_keypad: Optional[Dict[str, Any]] = None, reply_to_message_id: Optional[str] = None, disable_notification: bool = False, chat_keypad_type: Optional[Literal["New", "Removed", "None"]] = "New") -> Dict[str, Any]:
        return await self._send_file_generic("Image", chat_id, path, file_id, text, file_name, inline_keypad, chat_keypad, reply_to_message_id, disable_notification, chat_keypad_type)
        
    async def send_gif(self, chat_id: str, path: Optional[Union[str, Path]] = None, file_id: Optional[str] = None, text: Optional[str] = None, file_name: Optional[str] = None, inline_keypad: Optional[Dict[str, Any]] = None, chat_keypad: Optional[Dict[str, Any]] = None, reply_to_message_id: Optional[str] = None, disable_notification: bool = False, chat_keypad_type: Optional[Literal["New", "Removed", "None"]] = "New") -> Dict[str, Any]:
        return await self._send_file_generic("Gif", chat_id, path, file_id, text, file_name, inline_keypad, chat_keypad, reply_to_message_id, disable_notification, chat_keypad_type)

    async def forward_message(self, from_chat_id: str, message_id: str, to_chat_id: str, disable_notification: bool = False) -> Dict[str, Any]:
        return await self._post("forwardMessage", {"from_chat_id": from_chat_id, "message_id": message_id, "to_chat_id": to_chat_id, "disable_notification": disable_notification})

    async def edit_message_text(self, chat_id: str, message_id: str, text: str) -> Dict[str, Any]:
        return await self._post("editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": text})

    async def edit_inline_keypad(self, chat_id: str, message_id: str, inline_keypad: Dict[str, Any]) -> Dict[str, Any]:
        return await self._post("editMessageKeypad", {"chat_id": chat_id, "message_id": message_id, "inline_keypad": inline_keypad})

    async def delete_message(self, chat_id: str, message_id: str) -> Dict[str, Any]:
        return await self._post("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

    async def set_commands(self, bot_commands: List[Dict[str, str]]) -> Dict[str, Any]:
        return await self._post("setCommands", {"bot_commands": bot_commands})

    async def update_bot_endpoint(self, url: str, type: str) -> Dict[str, Any]:
        return await self._post("updateBotEndpoints", {"url": url, "type": type})

    async def remove_keypad(self, chat_id: str) -> Dict[str, Any]:
        return await self._post("editChatKeypad", {"chat_id": chat_id, "chat_keypad_type": "Removed"})

    async def edit_chat_keypad(self, chat_id: str, chat_keypad: Dict[str, Any]) -> Dict[str, Any]:
        return await self._post("editChatKeypad", {"chat_id": chat_id, "chat_keypad_type": "New", "chat_keypad": chat_keypad})

    async def get_name(self, chat_id: str) -> str:
        try:
            chat = await self.get_chat(chat_id)
            chat_info = chat.get("data", {}).get("chat", {})
            first_name = chat_info.get("first_name", "")
            last_name = chat_info.get("last_name", "")
            
            full_name = f"{first_name} {last_name}".strip()
            return full_name if full_name else "Unknown"
        except Exception:
            return "Unknown"

    async def get_username(self, chat_id: str) -> str:
        chat_info = await self.get_chat(chat_id)
        return chat_info.get("data", {}).get("chat", {}).get("username", "None")