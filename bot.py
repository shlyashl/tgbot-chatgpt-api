# -*- coding: utf-8 -*-
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.utils.helper import HelperMode
import openai

import config as cfg


openai.api_key = cfg.oai_token
bot = Bot(token=cfg.tg_token, timeout=None)
dp = Dispatcher(bot, storage=MemoryStorage())


def generate_response(prompt):
    completion = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.6,
    )
    message = completion.choices[0].text
    return message


class Talk(StatesGroup):
    mode = HelperMode.snake_case
    ACTIVE = State()


@dp.message_handler(commands=['help', 'start'])
async def process_help_command(message: types.Message):
    await message.reply(
        '— Что бы включить бота напиши "Раджеш, проснись"\n'
        '— Что бы выключить - "Раджеш, усни"\n'
        '— Бот отвечает только тому кто его разбудил\n'
        '— Попросить уснуть бота могут все'
    )


@dp.message_handler()
async def process_help_command(message: types.Message, state: FSMContext):
    if message.text.lower().startswith('раджеш, проснись'):
        await Talk.ACTIVE.set()
        await state.update_data(user_id=message['from']['id'])
        await message.reply('Привет, я проснулся. Напиши "Раджеш, усни", если нужно что бы я уснул')


@dp.message_handler(state=Talk.ACTIVE)
async def process_help_command(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    if message.text.lower().startswith('раджеш, усни'):
        await message.reply('Пока!')
        await state.finish()
    elif user_data['user_id'] == message['from']['id']:
        await message.reply(generate_response(message.text))


if __name__ == '__main__':
    executor.start_polling(dp)
