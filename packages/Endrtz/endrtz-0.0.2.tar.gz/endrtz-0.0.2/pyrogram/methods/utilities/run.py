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
        """
        Start the client, idle the main script and finally stop the client.

        A convenience method that calls:
        - self.start()
        - pyrogram.idle()
        - self.stop()

        Parameters:
            use_qr (bool, optional): Use QR code login (for new auth only). Default is False.
            except_ids (List[int], optional): List of user IDs to skip QR login if already authorized. Default is [].

        Raises:
            ConnectionError: If client is already started.

        Example:
            app = Client("my_account")
            app.run()
        """
        if except_ids is None:
            except_ids = []

        run = self.loop.run_until_complete

        if inspect.iscoroutinefunction(self.start):
            run(self.start(use_qr=use_qr, except_ids=except_ids))
            run(idle())
            run(self.stop())
        else:
            self.start(use_qr=use_qr, except_ids=except_ids)
            run(idle())
            self.stop()
