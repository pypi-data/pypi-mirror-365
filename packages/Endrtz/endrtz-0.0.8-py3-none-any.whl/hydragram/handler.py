from functools import wraps
from typing import Union, List, Optional
from pyrogram import filters as hydra_filters
from hydragram.filters import command as hydra_command
from pyrogram.handlers import (
    MessageHandler, CallbackQueryHandler, InlineQueryHandler,
    ChosenInlineResultHandler, EditedMessageHandler, PollHandler,
    PollAnswerHandler, ChatMemberUpdatedHandler
)

HANDLER_MAP = {
    "message": MessageHandler,
    "callback_query": CallbackQueryHandler,
    "inline_query": InlineQueryHandler,
    "chosen_inline_result": ChosenInlineResultHandler,
    "edited_message": EditedMessageHandler,
    "poll": PollHandler,
    "poll_answer": PollAnswerHandler,
    "chat_member_updated": ChatMemberUpdatedHandler
}


def handler(
    commands: Optional[Union[str, List[str]]] = None,
    *,
    group: int = 9999999,
    dev_cmd: bool = False,
    owner_cmd: bool = False,
    gc_owner: bool = False,
    gc_admin: bool = False,
    case_sensitive: bool = False,
    filters=None,
    extra=None,
    handler_type: str = "message"
):
    def decorator(func):
        @wraps(func)
        async def wrapper(client, update):
            return await func(client, update)

        wrapper._client_ref = None

        def register_handler(client):
            handler_cls = HANDLER_MAP.get(handler_type)
            if not handler_cls:
                raise ValueError(f"Unsupported handler type: {handler_type}")

            flt = filters or hydra_filters.all

            if commands and handler_type == "message":
                cmd_list = [commands] if isinstance(commands, str) else commands
                command_filter = hydra_command(
                    cmd_list,
                    dev_cmd=dev_cmd,
                    owner_cmd=owner_cmd,
                    gc_owner=gc_owner,
                    gc_admin=gc_admin,
                    case_sensitive=case_sensitive
                )
                flt = command_filter & flt

            client.add_handler(handler_cls(wrapper, flt), group)
            wrapper._client_ref = client

        try:
            from hydragram.client import Client as HydraClient
            pyro_client = HydraClient.get_client()
            register_handler(pyro_client)
        except RuntimeError:
            # Probably being registered later in startup
            pass

        return wrapper
    return decorator


# Alias for easier usage
app = handler
