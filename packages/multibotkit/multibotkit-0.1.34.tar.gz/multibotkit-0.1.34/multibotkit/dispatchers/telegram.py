import inspect
from datetime import datetime
from multibotkit.dispatchers.base_dispatcher import BaseDispatcher
from multibotkit.schemas.telegram.incoming import Update


class TelegramDispatcher(BaseDispatcher):

    async def process_event(
        self, event: Update
    ):
        if event.message is not None:
            sender_id = event.message.from_.id
        elif event.callback_query is not None:
            sender_id = event.callback_query.from_.id
        elif event.chat_member is not None:
            sender_id = event.chat_member.from_.id
        elif event.chat_join_request is not None:
            sender_id = event.chat_join_request.from_.id
        elif event.my_chat_member is not None:
            sender_id = event.my_chat_member.from_.id
        else:
            sender_id = None

        state_id = f"telegram_{sender_id}"
        state_object = await self.state_manager.get_state(state_id)

        for (func, state_func, handler) in self._handlers:
            
            state_func_result = True
            if state_func is not None:
                try:
                    if inspect.iscoroutinefunction(state_func):
                        state_func_result = await state_func(state_object)
                    else:
                        state_func_result = state_func(state_object)
                except Exception:
                    continue
            
            func_result = True
            if func is not None:
                try:
                    if inspect.iscoroutinefunction(func):
                        func_result = await func(event)
                    else:
                        func_result = func(event)
                except Exception:
                    continue

            summary_result = state_func_result * func_result
            
            if summary_result:
                await handler(event, state_object)
                
                if self.logger:
                    new_state_object = await self.state_manager.get_state(state_id)
                    event_log = {
                        "created_at": datetime.now(),
                        "user_id": state_object.id,
                        "paltform": "Telegram",
                        "old_state": state_object.state,
                        "old_state_data": state_object.data,
                        "new_state": new_state_object.state,
                        "new_state_data": new_state_object.data,
                        "event": event.dict()
                    }
                    if callable(self.logger):
                        await self.logger(event_log)
                        return
                    self.logger.info(f"Incoming Telegram event: {event_log}")
                return
