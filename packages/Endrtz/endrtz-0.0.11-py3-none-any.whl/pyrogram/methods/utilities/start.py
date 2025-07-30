import logging
from typing import List, Optional

import pyrogram
from pyrogram import raw

log = logging.getLogger(__name__)

class Start:
    async def start(
        self: "pyrogram.Client",
        *,
        use_qr: bool = False,
        except_ids: Optional[List[int]] = None,
    ):
        # Ensure except_ids is a list
        if except_ids is None:
            except_ids = []

        self.load_plugins()

        is_authorized = await self.connect()

        try:
            if not is_authorized:
                if use_qr:
                    try:
                        import qrcode
                        await self.authorize_qr(except_ids=except_ids)
                    except ImportError:
                        log.warning("qrcode package not found, falling back to default login")
                        await self.authorize()
                else:
                    await self.authorize()

            if self.takeout and not await self.storage.is_bot():
                self.takeout_id = (await self.invoke(raw.functions.account.InitTakeoutSession())).id
                log.info("Takeout session %s initiated", self.takeout_id)

            await self.invoke(raw.functions.updates.GetState())
        except (Exception, KeyboardInterrupt):
            await self.disconnect()
            raise
        else:
            self.me = await self.get_me()
            await self.initialize()
            return self
