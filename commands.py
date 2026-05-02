from datetime import date

def today():
    return str(date.today())


def calc_points(difficulty, percent):
    return difficulty * (percent / 100)


def handle_command(cmd, args, state, user_id):
    user = state.setdefault(user_id, {})
    today_str = today()

    # AUTO RESET DIÁRIO (mantém streak)
    if user.get("last_day") != today_str:
        last = user.get("last_result")

        if last is not None and last >= 70:
            user["streak"] = user.get("streak", 0) + 1
        else:
            user["streak"] = 0

        user["goal"] = None
        user["last_day"] = today_str
        user["last_result"] = None

    if cmd == "goal":
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

        return f"goal: {text} ({difficulty}/5)"

    if cmd == "finish":
        if len(args) != 1:
            return "uso: !finish <0-100>"

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

        return (
            f"score: {score:.2f} | "
            f"total: {user['score']:.2f} | "
            f"streak: {user.get('streak', 0)}"
        )
    
    if cmd in ("resetday", "reset"):
        removed_score = user.get("today_score", 0)

        if removed_score:
            user["score"] = max(0, user.get("score", 0) - removed_score)

        user["goal"] = None
        user["last_result"] = None
        user["last_day"] = today_str
        user["today_score"] = 0

        return (
            f"dia resetado | "
            f"removido: {removed_score:.2f} pts | "
            f"total: {user.get('score', 0):.2f}"
        )

    if cmd == "stats":
        return f"score: {user.get('score', 0):.2f} | streak: {user.get('streak', 0)}"

    if cmd == "leaderboard":
        lb = sorted(
            [(uid, d.get("score", 0), d.get("streak", 0)) for uid, d in state.items()],
            key=lambda x: x[1],
            reverse=True
        )

        msg = "leaderboard:\n"
        for i, (uid, score, streak) in enumerate(lb[:10], 1):
            msg += f"{i}. {uid} | {score:.1f} pts | streak {streak}\n"

        return msg
    
    if cmd == "help":
        return (
            "commands:\n"
            "!goal <texto> <1-5> -> define o objetivo do dia\n"
            "!finish <0-100> -> finaliza o dia e calcula score\n"
            "!stats -> mostra score e streak\n"
            "!leaderboard -> ranking \n"
            "!resetday -> apaga o objetivo/finish de hoje se fizeste merda\n"
        )

    return None