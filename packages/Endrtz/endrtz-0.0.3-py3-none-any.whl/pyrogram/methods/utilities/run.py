import inspect
from typing import List, Optional
import pyrogram
from pyrogram.methods.utilities.idle import idle


class Run:
    def run(
        self: "pyrogram.Client", *,
        use_qr: bool = False,
        except_ids: Optional[List[int]] = None,
    ):
        if except_ids is None:
            except_ids = []

        run = self.loop.run_until_complete
        start_signature = inspect.signature(self.start)

        # Check if start accepts use_qr and except_ids
        accepts_use_qr = "use_qr" in start_signature.parameters
        accepts_except_ids = "except_ids" in start_signature.parameters

        kwargs = {}
        if accepts_use_qr:
            kwargs["use_qr"] = use_qr
        if accepts_except_ids:
            kwargs["except_ids"] = except_ids

        if inspect.iscoroutinefunction(self.start):
            run(self.start(**kwargs))
            run(idle())
            run(self.stop())
        else:
            self.start(**kwargs)
            run(idle())
            self.stop()
