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

    if cmd == "goal":
        text = " ".join(args[:-1])
        difficulty = int(args[-1])

        user["goal"] = {
            "text": text,
            "difficulty": difficulty
        }

        return f"goal: {text} ({difficulty}/5)"

    if cmd == "finish":
        if not user.get("goal"):
            return "sem goal hoje"

        percent = int(args[0])
        g = user["goal"]

        score = calc_points(g["difficulty"], percent)

        # acumular score
        user["score"] = user.get("score", 0) + score

        user["goal"] = None
        user["last_result"] = percent
        user["last_day"] = today_str

        return f"score: {score:.2f} | total: {user['score']:.2f} | streak: {user['streak']}"

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
        )

    return None