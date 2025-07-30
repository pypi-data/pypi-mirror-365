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
    Simple handler decorator that closely follows Pyrogram's client structure.
    
    Args:
        commands: Command(s) to trigger the handler
        group: Handler group
        dev_cmd: Developer-only command
        owner_cmd: Owner-only command
        gc_owner: Group owner-only
        gc_admin: Group admin-only
        case_sensitive: Command case sensitivity
        filters: Additional filters
        extra: Extra data
        handler_type: Type of handler
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(client, update):
            return await func(client, update)

        # Map handler types to Pyrogram handler classes
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

        # Get the appropriate handler class
        HandlerClass = handler_map.get(handler_type)
        if HandlerClass is None:
            raise ValueError(f"Invalid handler type: {handler_type}")

        # Build filters for commands if this is a message handler
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

        # Add the handler to any running clients
        try:
            from pyrogram.client import Client
            for client in Client._instances.values():
                client.add_handler(HandlerClass(wrapper, flt), group)
        except Exception:
            pass

        return wrapper

    return decorator


# Alias for convenience
app = handler
