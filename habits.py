import os
import re
import logging
from datetime import datetime, timedelta
from todoist.api import TodoistAPI

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

TODOIST_DATE_FORMAT = "%Y-%m-%d"

def get_token():
    token = os.getenv('TODOIST_APIKEY')
    return token


def is_habit(text):
    return re.search(r'\[day\s(\d+)\]', text)

def today_date():
    return (datetime.utcnow() + timedelta(1)).strftime(TODOIST_DATE_FORMAT)

def is_today(text):
    today = (datetime.utcnow() + timedelta(1)).strftime(TODOIST_DATE_FORMAT)
    return text == today


def is_due(text):
    yesterday = datetime.utcnow().strftime(TODOIST_DATE_FORMAT)
    return text == yesterday


def update_streak(task, streak):
    days = '[day {}]'.format(streak)
    text = re.sub(r'\[day\s(\d+)\]', days, task['content'])
    task.update(content=text)


def main():
    API_TOKEN = get_token()
    today = datetime.utcnow().replace(tzinfo=None)
    if not API_TOKEN:
        logging.warn('Please set the API token in environment variable.')
        exit()
    api = TodoistAPI(API_TOKEN)
    api.sync()
    tasks = api.state['items']
    for task in tasks:
        if task['due'] and is_habit(task['content']) and not task['in_history']:
            if is_today(task['due']['date']):
                habit = is_habit(task['content'])
                streak = int(habit.group(1)) + 1
                update_streak(task, streak)
            elif is_due(task['due']['date']):
                update_streak(task, 0)
                task.update(due={'string': 'ev day starting {}'.format(today_date())})
    api.commit()

if __name__ == '__main__':
    main()
