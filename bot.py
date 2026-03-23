import asyncio, random
from aiogram import Bot, Dispatcher, types
from aiogram.types import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import ChatNotFound
from config import TOKEN, ADMIN_ID, CHANNEL_USERNAME
from db import init_db, get_balance, add_balance, remove_balance

bot = Bot(TOKEN)
dp = Dispatcher()

# ====== СТАРТ с проверкой подписки ======
@dp.message(commands=["start"])
async def start(msg: types.Message):
    user_id = msg.from_user.id
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status == "left":
            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("Подписаться на канал", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"))
            return await msg.answer("❌ Для игры нужно подписаться на канал", reply_markup=kb)
    except ChatNotFound:
        return await msg.answer("Ошибка: канал не найден или бот не является админом канала")

    # Если подписан
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🎰 Играть", "💰 Баланс")
    kb.add("💳 Пополнить", "💸 Вывод")
    await msg.answer("Добро пожаловать в StarPlay! ⭐", reply_markup=kb)

# ====== БАЛАНС ======
@dp.message(lambda m: m.text == "💰 Баланс")
async def balance(msg: types.Message):
    bal = await get_balance(msg.from_user.id)
    await msg.answer(f"Ваш баланс: {bal} ⭐")

# ====== ПОПОЛНЕНИЕ ======
@dp.message(lambda m: m.text == "💳 Пополнить")
async def deposit(msg: types.Message):
    prices = [LabeledPrice("100 Stars", 100)]
    await bot.send_invoice(
        msg.chat.id, "Пополнение", "Пополнение баланса", "deposit_100",
        provider_token="", currency="XTR", prices=prices
    )

@dp.message(lambda m: m.successful_payment)
async def payment_success(msg: types.Message):
    await add_balance(msg.from_user.id, 100)
    await msg.answer("✅ Баланс пополнен на 100 ⭐")

# ====== ВЫВОД ======
@dp.message(lambda m: m.text == "💸 Вывод")
async def withdraw(msg: types.Message):
    bal = await get_balance(msg.from_user.id)
    if bal < 500: return await msg.answer("Минимум для вывода 500 ⭐")
    await msg.answer("Заявка на вывод отправлена администратору")

# ====== МЕНЮ ИГР ======
@dp.message(lambda m: m.text == "🎰 Играть")
async def menu_games(msg: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🎲 Кубик", "🪙 Монетка")
    kb.add("🎰 Слоты", "💣 Мины")
    kb.add("🚀 Rocket", "🎡 Рулетка")
    kb.add("🃏 Blackjack")
    await msg.answer("Выбери игру:", reply_markup=kb)

# ====== ИГРЫ ======
async def play_dice(user_id):
    bet = 10
    if await get_balance(user_id) < bet: return "Недостаточно ⭐"
    await remove_balance(user_id, bet)
    roll = random.randint(1,6)
    if roll>=4:
        win = 20
        await add_balance(user_id, win)
        return f"🎲 Выпало {roll}\nТы выиграл {win} ⭐"
    return f"🎲 Выпало {roll}\nТы проиграл"

async def play_coin(user_id):
    bet = 10
    if await get_balance(user_id)<bet: return "Недостаточно ⭐"
    await remove_balance(user_id, bet)
    res = random.choice(["Орел", "Решка"])
    if res=="Орел":
        win=20
        await add_balance(user_id,win)
        return f"🪙 {res}!\nВы выиграли {win} ⭐"
    return f"🪙 {res}!\nВы проиграли"

async def play_slots(user_id):
    bet = 10
    if await get_balance(user_id)<bet: return "Недостаточно ⭐"
    await remove_balance(user_id, bet)
    symbols = ["🍒","🍋","🔔","⭐"]
    spin = [random.choice(symbols) for _ in range(3)]
    if len(set(spin))==1:
        win = 50
        await add_balance(user_id, win)
        return f"{''.join(spin)}\n🎉 Джекпот! +{win} ⭐"
    return f"{''.join(spin)}\nПроиграли"

async def play_mines(user_id):
    bet = 10
    if await get_balance(user_id)<bet: return "Недостаточно ⭐"
    await remove_balance(user_id,bet)
    safe = random.randint(1,5)
    choice = random.randint(1,5)
    if choice==safe:
        win=40
        await add_balance(user_id,win)
        return f"💣 Мина пропущена! +{win} ⭐"
    return "💣 Бах! Проиграли"

async def play_rocket(user_id):
    bet=10
    if await get_balance(user_id)<bet: return "Недостаточно ⭐"
    await remove_balance(user_id,bet)
    multiplier = random.uniform(1.0, 10.0)
    win=int(bet*multiplier)
    await add_balance(user_id,win)
    return f"🚀 Rocket взлетел x{multiplier:.2f}! Вы выиграли {win} ⭐"

async def play_roulette(user_id):
    bet=10
    if await get_balance(user_id)<bet: return "Недостаточно ⭐"
    await remove_balance(user_id,bet)
    number=random.randint(0,36)
    if number%2==0:
        win=20
        await add_balance(user_id,win)
        return f"🎡 Выпало {number} 🎉 Вы выиграли {win} ⭐"
    return f"🎡 Выпало {number}\nВы проиграли"

async def play_blackjack(user_id):
    bet=10
    if await get_balance(user_id)<bet: return "Недостаточно ⭐"
    await remove_balance(user_id,bet)
    user_score=random.randint(15,21)
    dealer_score=random.randint(15,21)
    if user_score>dealer_score:
        win=30
        await add_balance(user_id,win)
        return f"🃏 Вы: {user_score}, Дилер: {dealer_score}\nВы выиграли {win} ⭐"
    return f"🃏 Вы: {user_score}, Дилер: {dealer_score}\nВы проиграли"

# ====== КОМАНДЫ ИГР ======
@dp.message(lambda m: m.text=="🎲 Кубик")
async def cmd_dice(msg): await msg.answer(await play_dice(msg.from_user.id))
@dp.message(lambda m: m.text=="🪙 Монетка")
async def cmd_coin(msg): await msg.answer(await play_coin(msg.from_user.id))
@dp.message(lambda m: m.text=="🎰 Слоты")
async def cmd_slots(msg): await msg.answer(await play_slots(msg.from_user.id))
@dp.message(lambda m: m.text=="💣 Мины")
async def cmd_mines(msg): await msg.answer(await play_mines(msg.from_user.id))
@dp.message(lambda m: m.text=="🚀 Rocket")
async def cmd_rocket(msg): await msg.answer(await play_rocket(msg.from_user.id))
@dp.message(lambda m: m.text=="🎡 Рулетка")
async def cmd_roulette(msg): await msg.answer(await play_roulette(msg.from_user.id))
@dp.message(lambda m: m.text=="🃏 Blackjack")
async def cmd_blackjack(msg): await msg.answer(await play_blackjack(msg.from_user.id))

# ====== АДМИН ======
@dp.message(lambda m: m.text.startswith("/add"))
async def admin_add(msg):
    if msg.from_user.id!=ADMIN_ID: return
    try:
        _, uid, amount = msg.text.split()
        await add_balance(int(uid), int(amount))
        await msg.answer("Готово")
    except:
        await msg.answer("Ошибка")

# ====== ЗАПУСК ======
async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__=="__main__":
    asyncio.run(main())
