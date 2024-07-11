import datetime
import json
import time

import japanize_matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
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


def retrieve_unique_AC_counts(user: str, period: int) -> list:
    unique_ac_subs = retrieve_unique_AC_subs(user, period)

    # count subs
    date_to_subcnt = {}
    for i in range(period + 1):
        d = datetime.datetime.now() + datetime.timedelta(days=-i)
        date = d.strftime("%Y-%m-%d")
        date_to_subcnt[date] = 0
    for sub in unique_ac_subs:
        date_to_subcnt[sub["date"]] += 1

    # accumulate
    sub_cnts_cum = [date_to_subcnt[date] for date in sorted(date_to_subcnt)]
    for i in range(1, len(sub_cnts_cum)):
        sub_cnts_cum[i] += sub_cnts_cum[i - 1]

    return sub_cnts_cum


def retrieve_total_unique_AC_points(user: str, period: int) -> list:
    unique_ac_subs = retrieve_unique_AC_subs(user, period)

    # count subs
    date_to_points = {}
    for i in range(period + 1):
        d = datetime.datetime.now() + datetime.timedelta(days=-i)
        date = d.strftime("%Y-%m-%d")
        date_to_points[date] = 0
    for sub in unique_ac_subs:
        date_to_points[sub["date"]] += int(sub["point"])

    # accumulate
    points_cum = [date_to_points[date] for date in sorted(date_to_points)]
    for i in range(1, len(points_cum)):
        points_cum[i] += points_cum[i - 1]

    return points_cum


def retrieve_chart_data(users: list, period: int, kind="獲得スコア"):
    users_data = []
    for user in users:
        if kind == "AC数":
            user_data = retrieve_unique_AC_counts(user, period)
        elif kind == "獲得スコア":
            user_data = retrieve_total_unique_AC_points(user, period)
        else:
            log.critical("「獲得スコア」または「AC数」を指定してください")
            exit(1)
        users_data.append(user_data)
        time.sleep(1)
    return users_data


def draw_chart(users: list, period: int, kind="獲得スコア"):
    users_data = retrieve_chart_data(users, period, kind)

    dates = []
    for i in range(period + 1):
        d = datetime.datetime.now() + datetime.timedelta(days=-period + i)
        dates.append(d)

    plt.figure(figsize=(11, 6))

    # plot line chart
    for user, data in zip(users, users_data):
        plt.plot(dates, data, label=user)
        time.sleep(1)

    # set x axis date format
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    plt.gca().xaxis.set_minor_locator(ticker.AutoMinorLocator())
    plt.gcf().autofmt_xdate()

    # other
    plt.title(f"精進量の比較 （{kind}）", pad=20, fontsize=16)
    plt.legend()
    plt.grid(axis="y", linestyle="--")
    plt.tight_layout()

    plt.show()


if __name__ == "__main__":
    USERS = ["gigolo", "ktsn_ud"]
    # USERS = ["gigolo", "ktsn_ud", "merudo", "Astroseek"]
    DAY_PERIOD = 90

    # draw_chart(USERS, DAY_PERIOD, kind="AC数")
    draw_chart(USERS, DAY_PERIOD, kind="獲得スコア")
