from datetime import date
from storage import load_data, save_data

def today():
    return str(date.today())


def calc_points(difficulty, percent):
    return difficulty * (percent / 100)


def handle_command(cmd, args, state, user_id):
    user = state.setdefault(user_id, {})
    today_str = today()

    response = None
    changed = False

    # AUTO RESET DIÁRIO (mantém streak)
    if user.get("last_day") != today_str:
        last = user.get("last_result")

        if last is not None and last >= 50:
            user["streak"] = user.get("streak", 0) + 1
        else:
            user["streak"] = 0

        user["goal"] = None
        user["last_day"] = today_str
        user["last_result"] = None

        changed = True

    elif cmd == "register":
        name = " ".join(args[:])

        if not name:
            return "!register <nome aqui boi>"
        
        user["name"] = name
        response = f"novo níck é {name}"

        changed = True

    elif cmd == "goal":
        if len(args) < 2:
            return "uso: !goal <texto> <1-5>"

        try:
            difficulty = int(args[-1])
        except ValueError:
            return "a dificuldade tem de ser um número de 1 a 5"

        if difficulty < 1 or difficulty > 5:
            return "a dificuldade tem de estar entre 1 e 5"

        text = " ".join(args[:-1])

        user["goal"] = {
            "text": text,
            "difficulty": difficulty
        }

        response = f"goal: {text} ({difficulty}/5)"

        changed = True

    elif cmd == "result":
        if len(args) != 1:
            return "uso: !result <0-100>"

        try:
            percent = int(args[0])
        except ValueError:
            return "a percentagem tem de ser um número"

        if percent < 0 or percent > 100:
            return "a percentagem tem de estar entre 0 e 100"
        
        if not user.get("goal"):
            return "sem goal hoje"

        g = user["goal"]

        score = calc_points(g["difficulty"], percent)

        user["score"] = user.get("score", 0) + score
        user["today_score"] = score

        user["goal"] = None
        user["last_result"] = percent
        user["last_day"] = today_str

        response = (
            f"score: {score:.2f} | "
            f"total: {user['score']:.2f} | "
            f"streak: {user.get('streak', 0)}"
        )

        changed = True
    
    elif cmd == "resetday":
        removed_score = user.get("today_score", 0)

        if removed_score:
            user["score"] = max(0, user.get("score", 0) - removed_score)

        user["goal"] = None
        user["last_result"] = None
        user["last_day"] = today_str
        user["today_score"] = 0

        response = (
            f"dia resetado | "
            f"removido: {removed_score:.2f} pts | "
            f"total: {user.get('score', 0):.2f}"
        )

        changed = True

    elif cmd == "reset":
        user["score"] = 0
        user["goal"] = None
        user["last_result"] = None
        user["last_day"] = today_str
        user["today_score"] = 0
        user["streak"] = 0

        changed = True

        response = f"score resetado"

    elif cmd == "stats":
        response = f"score: {user.get('score', 0):.2f} | streak: {user.get('streak', 0)}"

    elif cmd == "leaderboard":
        lb = sorted(
            [(uid, d.get("score", 0), d.get("streak", 0)) for uid, d in state.items()],
            key=lambda x: x[1],
            reverse=True
        )

        msg = "leaderboard:\n"
        for i, (uid, score, streak) in enumerate(lb[:10], 1):
            nick = state[uid].get("name", uid)
            msg += f"{i}. {nick} | {score:.1f} pts | streak {streak}\n"

        response = msg
    
    elif cmd == "help":
        response = (
            "commands:\n"
            "!register <donald trump> -> define o teu nick\n"
            "!goal <texto> <1-5> -> define o objetivo do dia\n"
            "!result <0-100> -> finaliza o dia e calcula score\n"
            "!stats -> mostra score e streak\n"
            "!leaderboard -> ranking \n"
            "!resetday -> apaga o score de hoje\n"
            "!reset -> apaga o score total\n"
        )

    if changed:
        save_data(state)

    return response