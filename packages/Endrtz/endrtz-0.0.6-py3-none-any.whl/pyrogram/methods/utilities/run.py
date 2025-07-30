import inspect
from typing import List, Optional
import pyrogram
from pyrogram.methods.utilities.idle import idle

class Run:
    def run(
        self: "pyrogram.Client",
        *,
        use_qr: Optional[bool] = None,
        except_ids: Optional[List[int]] = None,
    ):
        # Fallback defaults for automation
        if use_qr is None:
            use_qr = False
        if except_ids is None:
            except_ids = []

        run = self.loop.run_until_complete
        start_signature = inspect.signature(self.start)

        kwargs = {}
        if "use_qr" in start_signature.parameters:
            kwargs["use_qr"] = use_qr
        if "except_ids" in start_signature.parameters:
            kwargs["except_ids"] = except_ids

        if inspect.iscoroutinefunction(self.start):
            run(self.start(**kwargs))
            run(idle())
            run(self.stop())
        else:
            self.start(**kwargs)
            run(idle())
            self.stop()
