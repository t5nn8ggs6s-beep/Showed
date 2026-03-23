import random
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import ChatNotFound
from config import TOKEN, ADMIN_ID, CHANNEL_USERNAME

# ====== ИНИЦИАЛИЗАЦИЯ ======
bot = Bot(TOKEN)
dp = Dispatcher(bot)

# ====== БАЗА ПОЛЬЗОВАТЕЛЕЙ (звёзды) ======
users_balance = {}  # user_id: stars

# ====== ПРОВЕРКА ПОДПИСКИ ======
async def check_subscribed(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status not in ["left", "kicked"]
    except ChatNotFound:
        return False

# ====== МЕНЮ ИГР ======
def games_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    games = [
        ("Рулетка", "roulette"), ("Слот", "slot"), ("Баскетбол", "basketball"),
        ("Футбол", "football"), ("Блекджек", "blackjack"), ("Мины", "mines"),
        ("Монетка", "coin"), ("Кубик", "dice"), ("Башня", "tower"),
        ("Боулинг", "bowling"), ("Рокет", "rocket")
    ]
    for name, callback in games:
        kb.insert(InlineKeyboardButton(name, callback_data=callback))
    return kb

# ====== СТАРТ ======
@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    user_id = msg.from_user.id
    if not await check_subscribed(user_id):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(
            "Подписаться на канал", 
            url=f"https://t.me/{CHANNEL_USERNAME[1:]}"
        ))
        return await msg.answer(
            "❌ Для игры нужно подписаться на канал", 
            reply_markup=kb
        )

    if user_id not in users_balance:
        users_balance[user_id] = 1000  # стартовый баланс

    await msg.answer(
        f"✅ Привет! У тебя {users_balance[user_id]} ⭐\nВыбери игру:",
        reply_markup=games_keyboard()
    )

# ====== ОБРАБОТКА ИГР ======
@dp.callback_query_handler(lambda c: True)
async def game_callback(cq: types.CallbackQuery):
    user_id = cq.from_user.id
    game = cq.data

    if users_balance.get(user_id, 0) < 50:
        await cq.answer("Недостаточно звёзд для игры (минимум 50 ⭐)")
        return

    # Минимальная ставка
    bet = 50
    users_balance[user_id] -= bet

    win = 0
    if game == "roulette":
        win = bet * random.choice([0, 2])  # 50% шанс удвоить
    elif game == "slot":
        win = bet * random.choice([0, 3])
    elif game == "coin":
        win = bet * random.choice([0, 2])
    elif game == "dice":
        win = bet * random.choice([0, 2])
    elif game == "basketball":
        win = bet * random.choice([0, 3])
    elif game == "football":
        win = bet * random.choice([0, 3])
    elif game == "blackjack":
        win = bet * random.choice([0, 5])
    elif game == "mines":
        win = bet * random.choice([0, 4])
    elif game == "tower":
        win = bet * random.choice([0, 2])
    elif game == "bowling":
        win = bet * random.choice([0, 3])
    elif game == "rocket":
        win = bet * random.choice([0, 6])

    users_balance[user_id] += win

    await cq.answer(f"Игра: {game}\nСтавка: {bet} ⭐\nВыигрыш: {win} ⭐\nБаланс: {users_balance[user_id]} ⭐")

# ====== АДМИНКА ======
@dp.message_handler(commands=["admin"])
async def admin(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return await msg.answer("❌ Доступ запрещён")
    await msg.answer("✅ Привет, админ! Здесь можно добавлять или снимать звёзды вручную.")

# ====== ВЫВОД БАЛАНСА ======
@dp.message_handler(commands=["balance"])
async def balance(msg: types.Message):
    user_id = msg.from_user.id
    bal = users_balance.get(user_id, 0)
    await msg.answer(f"💰 Твой баланс: {bal} ⭐")

# ====== ЗАПУСК БОТА ======
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
