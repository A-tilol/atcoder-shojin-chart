import datetime
import json
import time

import plotly.graph_objects as go
import requests

from logger import get_logger

log = get_logger(__name__, level=10)

SUB_API_URL = "https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions?user={}&from_second={}"
MAX_SUB = 500


def get_user_submissions(user: str, epoch: int) -> dict:
    res = requests.get(SUB_API_URL.format(user, epoch))
    log.debug(SUB_API_URL.format(user, epoch))
    subs = json.loads(res.text)
    if len(subs) < MAX_SUB:
        return subs

    time.sleep(1)
    epochs = [sub["epoch_second"] for sub in subs]
    epochs.sort()
    return subs + get_user_submissions(user, epochs[-1])


def retrieve_unique_AC_subs(user: str, period: int):
    # get subs
    epoch = (datetime.datetime.now() + datetime.timedelta(days=-period)).timestamp()
    subs = get_user_submissions(user, int(epoch))

    # exclude AHC
    subs = [sub for sub in subs if not sub["contest_id"].lower().startswith("ahc")]
    log.debug(f"Algo subs {len(subs)}")

    # extract AC subs
    subs = [sub for sub in subs if sub["result"] == "AC"]
    log.debug(f"AC subs {len(subs)}")

    # add date
    for sub in subs:
        d = datetime.datetime.fromtimestamp(sub["epoch_second"])
        sub["date"] = d.strftime("%Y-%m-%d")

    # sort by date asc
    subs.sort(key=lambda x: x["date"])

    # extract unique AC
    unique_ac_subs = []
    unique_keys = set()
    for sub in subs:
        if sub["problem_id"] in unique_keys:
            continue
        unique_ac_subs.append(sub)
        unique_keys.add(sub["problem_id"])
    log.debug(f"Unique AC subs {len(unique_ac_subs)}")

    return unique_ac_subs


def accumulate_y_score(subs: str, period: int, kind: str) -> list:
    date_to_score = {}
    for i in range(period + 1):
        d = datetime.datetime.now() + datetime.timedelta(days=-i)
        date = d.strftime("%Y-%m-%d")
        date_to_score[date] = 0
    for sub in subs:
        if kind == "獲得スコア":
            date_to_score[sub["date"]] += int(sub["point"])
        elif kind == "AC数":
            date_to_score[sub["date"]] += 1

    points_cum = [date_to_score[date] for date in sorted(date_to_score)]
    for i in range(1, len(points_cum)):
        points_cum[i] += points_cum[i - 1]

    return points_cum


def make_tooltip_text(dates: list, subs: list) -> list:
    day_summary = {}
    for date in dates:
        day_summary[date] = []

    for sub in subs:
        if sub["date"] not in day_summary:
            day_summary[date] = []
        problem = f'{sub["contest_id"]}  {sub["problem_id"].split("_")[-1]}  {int(sub["point"])}'
        day_summary[sub["date"]].append(problem)

    ret = []
    for date, daily_problems in sorted(day_summary.items()):
        daily_points = sum([int(x.split(" ")[-1]) for x in daily_problems])
        text = f"{date}<br>{len(daily_problems)} ACs,  {daily_points} Pts"
        if len(daily_problems) == 0:
            ret.append(text)
            continue

        daily_problems.sort()
        text += f"<br>{'- '*11}<br>" + "<br>".join(daily_problems)
        ret.append(text)

    return ret


def retrieve_chart_data(users: list, period: int, kind):
    dates = []
    for i in range(period + 1):
        d = datetime.datetime.now() + datetime.timedelta(days=-period + i)
        dates.append(d.strftime("%Y-%m-%d"))

    users_data = []
    for user in users:
        subs = retrieve_unique_AC_subs(user, period)
        x = dates
        y = accumulate_y_score(subs, period, kind)
        tooltip_text = make_tooltip_text(dates, subs)
        users_data.append((x, y, tooltip_text))

        time.sleep(1)
    return users_data


def draw_chart(users: list, period: int, kind="獲得スコア"):
    if kind not in ["AC数", "獲得スコア"]:
        log.critical("「獲得スコア」または「AC数」を指定してください")
        exit(1)

    users_data = retrieve_chart_data(users, period, kind)

    fig = go.Figure()

    # plot line chart
    for user, data in zip(users, users_data):
        fig.add_trace(
            go.Scatter(
                x=data[0],
                y=data[1],
                mode="lines",
                name=user,
                text=data[2],
                hovertemplate="%{text}",
            )
        )

    # set x axis date format
    fig.update_xaxes(
        dtick="M1",
        tickformat="%Y-%m",
        tickangle=-45,
    )

    # layout
    fig.update_layout(
        title=f"精進量比較チャート （{kind}）",
        legend_title="Users",
        template="plotly",
        width=1200,
        height=700,
        font=dict(family="Courier New, monospace", size=18, color="Gray"),
    )

    # ツールチップの文字色を白に設定
    fig.update_traces(
        hoverlabel=dict(
            font=dict(color="white"),
        )
    )

    fig.show()


if __name__ == "__main__":
    # USERS = ["gigolo"]
    USERS = ["gigolo", "ktsn_ud"]
    # USERS = ["gigolo", "ktsn_ud", "merudo", "Astroseek"]
    DAY_PERIOD = 90
    kind = "AC数"

    # draw_chart(USERS, DAY_PERIOD, kind="AC数")
    draw_chart(USERS, DAY_PERIOD, kind)
