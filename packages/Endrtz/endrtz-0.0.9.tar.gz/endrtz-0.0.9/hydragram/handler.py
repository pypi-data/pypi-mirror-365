from functools import wraps
from typing import Union, List, Optional
from pyrogram import filters as pyro_filters
from pyrogram.handlers import (
    MessageHandler,
    CallbackQueryHandler,
    InlineQueryHandler,
    ChosenInlineResultHandler,
    EditedMessageHandler,
    PollHandler,
    ChatJoinRequestHandler,
    ChatMemberUpdatedHandler,
    PreCheckoutQueryHandler,
    ShippingQueryHandler,
    RawUpdateHandler,
    StoryHandler,
    UserStatusHandler,
)
from pyrogram.types import Message, CallbackQuery


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
    """
    Decorator to register handlers for different Pyrogram handler types.

    commands: command(s) for message handler.
    group: handler group priority.
    dev_cmd, owner_cmd, gc_owner, gc_admin: custom filter flags.
    case_sensitive: command matching case sensitivity.
    filters: additional filters.
    handler_type: type of handler to register (e.g. 'message', 'callback_query', etc).
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(client, update):
            return await func(client, update)

        wrapper._client_ref = None

        def register_handler(client):
            # Build filters for commands if handler_type is message
            if commands is not None and handler_type == "message":
                from .filters import command as hydra_command
                cmd_list = [commands] if isinstance(commands, str) else commands
                flt = hydra_command(
                    cmd_list,
                    dev_cmd=dev_cmd,
                    owner_cmd=owner_cmd,
                    gc_owner=gc_owner,
                    gc_admin=gc_admin,
                    case_sensitive=case_sensitive
                )
                if filters:
                    flt = flt & filters
            else:
                flt = filters if filters else pyro_filters.all

            # Map handler_type to Pyrogram handler class
            handler_map = {
                "message": MessageHandler,
                "callback_query": CallbackQueryHandler,
                "inline_query": InlineQueryHandler,
                "chosen_inline_result": ChosenInlineResultHandler,
                "edited_message": EditedMessageHandler,
                "poll": PollHandler,
                "chat_join_request": ChatJoinRequestHandler,
                "chat_member_updated": ChatMemberUpdatedHandler,
                "pre_checkout_query": PreCheckoutQueryHandler,
                "shipping_query": ShippingQueryHandler,
                "raw_update": RawUpdateHandler,
                "story": StoryHandler,
                "user_status": UserStatusHandler,
            }

            HandlerClass = handler_map.get(handler_type)
            if HandlerClass is None:
                raise ValueError(f"Unknown handler_type: {handler_type}")

            client.add_handler(HandlerClass(wrapper, flt), group)
            wrapper._client_ref = client

        try:
            from pyrogram.client import Client as PyroClient
            pyro_client = PyroClient.get_client()
            register_handler(pyro_client)
        except RuntimeError:
            # Client not ready yet, defer registration
            pass

        return wrapper

    return decorator


app = handler
