from aiogram import Bot
from aiogram.dispatcher import Dispatcher
import config
from aiogram import types, executor
import DbInteraction
from aiogram.utils.callback_data import CallbackData


bot = Bot(token = config.token)
dp = Dispatcher(bot)


@dp.message_handler(commands="start")
async def start_method(message: types.Message):
    DbInteraction.create_users_document(message.chat.id)
    current_date = f"{message.date.day}.{message.date.month}.{message.date.year}"
    DbInteraction.set_current_date(message.chat.id, current_date)
    await message.answer(text=f"Добро пожаловать в наш супербот по планированию ваших дел. Если вы случайно удалите список дел, воспользуйтесь командой /repair")
    #we create the message which will contain the list of user's tasks
    await update_task_message(message.chat.id, current_date, create_new_message=True)


#that command will swich list of tasks to state "delete" from "point as completed"
@dp.message_handler(commands="edit")
async def delete_tasks(message: types.Message):
    await bot.delete_message(message.chat.id, message.message_id)
    current_date = f"{message.date.day}.{message.date.month}.{message.date.year}"
    #save=False means that bot will delete task when the user chick on it
    await update_task_message(message.chat.id, current_date, save=False)


#that command will swich the list back to adding-completing regimen
@dp.message_handler(commands="back")
async def continue_tasks(message: types.Message):
    await bot.delete_message(message.chat.id, message.message_id)
    current_date = f"{message.date.day}.{message.date.month}.{message.date.year}"
    await update_task_message(message.chat.id, current_date)


#this command is special for stupid users who will delete message with tasks
@dp.message_handler(commands="repair")
async def create_new_task_list(message: types.Message):
    await bot.delete_message(message.chat.id, message.message_id)
    current_date = f"{message.date.day}.{message.date.month}.{message.date.year}"
    await update_task_message(message.chat.id, current_date, create_new_message=True) 
   

#this command is processes user's message which is new task for today
@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def new_task(message: types.Message):
    #we don't need user's message, its text will become a task
    await bot.delete_message(message.chat.id, message.message_id)
    current_date = f"{message.date.day}.{message.date.month}.{message.date.year}"
    #we add new task for today
    DbInteraction.add_task(message.chat.id, current_date, message.text)
    #we update today's task message - because we added new task
    await update_task_message(message.chat.id, current_date)
        

#this var is for calback date for inlineButtons. I don't know that post means, 
#but task_id is the _id of task, save - true/false (if that button will delete task or point is as completed)
#date is the date of creating the message
callback= CallbackData("post", "task_id", "save", "date")
#this function updates today's task message
async def update_task_message(chat_id, current_date, create_new_message=False, save = True):
    last_date = DbInteraction.get_current_date(chat_id)
    #we don't need message_id if we create new one
    if (not create_new_message):
        message_id = DbInteraction.get_message_id(chat_id)

    #is today new day
    if (last_date!= current_date):
        DbInteraction.set_current_date(chat_id, current_date)
        #we get list of task from yesterday
        yesterday_tasks_list = DbInteraction.get_day(chat_id, last_date)
        #the text which will be sent to user
        yesterday_tasks_message = f"Итоги дня {last_date}:\n"
        total_number_of_tasks = 0
        number_of_completed_tasks = 0
        #this cycle is making list of tasks of last day
        for task in yesterday_tasks_list:#we go through the list of tasks
            total_number_of_tasks += 1
            #task["completed"] True/False
            if (task["completed"]):
                item_box = "✅ - "
                number_of_completed_tasks += 1
            else:
                item_box = "🔲 - "
            yesterday_tasks_message += item_box+task["task"]+"\n"
        yesterday_tasks_message += f"Выполнено {number_of_completed_tasks}/{total_number_of_tasks} поставлено задач"
        
        #delete yesterday message, because it contains buttons
        await bot.delete_message(chat_id, message_id)
        #sent report of completed task
        await bot.send_message(
            text = yesterday_tasks_message,
            chat_id= chat_id
        )
        #we must create new message with tasks
        create_new_message = True
        
    #we get list of tasks for today from DB
    today_tasks_list = DbInteraction.get_day(chat_id, current_date)
    #if Day doesn't contain "tasks" dict, the user doesn't have anytask for today    
    if today_tasks_list is not None:
        #create keyboard
        keyboard = types.InlineKeyboardMarkup()
        #this cycle is making list of tasks as a list of InlineButtons
        for task in today_tasks_list:#we go through the list of tasks
            if (task["completed"]):
                item_box = "✅ - "
            else:
                item_box = "🔲 - "
            item_button = types.InlineKeyboardButton(
                text=item_box+str(task["task"]), 
                callback_data=callback.new(task_id=task["_id"], save = save, date = current_date),
            )
            keyboard.add(item_button)

        #war save is bool, which indicates if we should delete tasks or point them as completed         
        if (save):
            message_text = f"Сегодня {current_date}. Ваши сегодяншние дела:\n(чтобы удалить дела нажмите /edit)"
        else: 
            message_text = f"Сегодня {current_date}. Какие задачи будете удалять?\n(как закончили удалять дела жмянкините /back)"

        if create_new_message:
            msg = await bot.send_message(
                text = message_text,
                reply_markup = keyboard, 
                chat_id = chat_id,
            )
            #update message_id
            DbInteraction.set_message_id(chat_id, msg.message_id)
        else:
            await bot.edit_message_text(
                text = message_text,
                reply_markup = keyboard, 
                chat_id = chat_id,
                message_id = message_id
            )
    else:
        message_text = f"{current_date}. Ваш список дел пустой, добавьте что-нибудь, а то опять день будет просран"
        if create_new_message:
            msg = await bot.send_message(chat_id = chat_id, text = message_text)
            #update message_id
            DbInteraction.set_message_id(chat_id, msg.message_id)
        else:
            await bot.edit_message_text(
                text = message_text,
                chat_id = chat_id,
                message_id = message_id
            )


#if calbackdate is save = True the user conpleted task 
@dp.callback_query_handler(callback.filter(save=["True"]))
async def callbacks(call: types.CallbackQuery, callback_data: dict):
    #swich completed to uncompleted, or uncompleted to completed
    DbInteraction.change_completed(call.from_user.id, callback_data["task_id"])
    await update_task_message(call.from_user.id, callback_data['date'])


#if save is False, we must delete this task
@dp.callback_query_handler(callback.filter(save=["False"]))
async def callbacks_num_change_fab(call: types.CallbackQuery, callback_data: dict):
    DbInteraction.delete_task(call.from_user.id, callback_data["task_id"])
    await update_task_message(call.from_user.id, callback_data['date'], save=False)


executor.start_polling(dp, skip_updates=True)