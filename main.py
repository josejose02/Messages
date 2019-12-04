import operator

import matplotlib.pyplot as plt

plt.rcdefaults()
from matplotlib import pylab as plt
import pandas as pd
import numpy as np
import seaborn as sns
# from gui import file_gui
from MessagesToCSV import MessagesToCSV
from emoji import UNICODE_EMOJI
import json
import copy
import datetime

pd.plotting.register_matplotlib_converters()


def has_emoji(word):
    for i in word:
        if i in UNICODE_EMOJI:
            return True
    return False


class Character:
    def __init__(self, w):
        self.char = w
        self.count = 1

    def increment(self):
        self.count += 1

    def __lt__(self, other):
        return self.count < other.count

    def __eq__(self, other):
        return self.char == other

    def __repr__(self):
        return self.char


def word_cleaner(word):
    word = word.lower()
    start, end = 1, 2
    if start == 1:
        return word
    while True:
        if end == len(end):
            break
        if word[-end] == word[-start]:
            word = word[:-1]
        else:
            break
        start += 1
        end += 1
    return word


def word_split(f):
    file = open(f, 'r', encoding="utf8")
    data = {
        'meta': {
            'messages': {'count': 0},
            'users': {
                'count': 0,
                'names': []
            },
            'words': {'count': 0, 'list': []},
            'emojis': {'count': 0, 'list': []},
        },
        'users': {},
    }
    for line in file:
        data['meta']['messages']['count'] += 1
        line = line.split(',')
        if line[0] == 'DateTime':
            continue
        if line[1] not in data['users']:
            data['users'][line[1]] = {
                'messages': {'count': 0},
                'words': {'count': 0, 'list': []},
                'emojis': {'count': 0, 'list': []}
            }
            data['meta']['users']['names'].append(Character(line[1]))
        meta_user_index = data['meta']['users']['names'].index(line[1])
        data['meta']['users']['names'][meta_user_index].increment()
        data['users'][line[1]]['messages']['count'] += 1
        for word in line[2].replace('\n', '').split():
            if has_emoji(word):
                for emoji in word:
                    if emoji not in UNICODE_EMOJI:
                        continue
                    if emoji in data['users'][line[1]]['emojis']['list']:
                        index = data['users'][line[1]]['emojis']['list'].index(emoji)
                        meta_index = data['meta']['emojis']['list'].index(emoji)
                        data['users'][line[1]]['emojis']['list'][index].increment()
                        data['meta']['emojis']['list'][meta_index].increment()
                    else:
                        data['users'][line[1]]['emojis']['list'].append(Character(emoji))
                        if emoji not in data['meta']['emojis']['list']:
                            data['meta']['emojis']['list'].append(Character(emoji))
                    data['users'][line[1]]['emojis']['count'] += 1
                    data['meta']['emojis']['count'] += 1
                continue
            if word in data['users'][line[1]]['words']['list']:
                word = word_cleaner(word)
                index = data['users'][line[1]]['words']['list'].index(word)
                meta_index = data['meta']['words']['list'].index(word)
                data['users'][line[1]]['words']['list'][index].increment()
                data['meta']['words']['list'][meta_index].increment()
            else:
                word = word_cleaner(word)
                data['users'][line[1]]['words']['list'].append(Character(word))
                if word not in data['meta']['words']['list']:
                    data['meta']['words']['list'].append(Character(word))
            data['users'][line[1]]['words']['count'] += 1
            data['meta']['words']['count'] += 1
    for person in data['users']:
        data['meta']['users']['count'] += 1
        data['users'][person]['emojis']['list'].sort(reverse=True)
        data['users'][person]['words']['list'].sort(reverse=True)
    data['meta']['users']['names'].sort(reverse=True)
    data['meta']['emojis']['list'].sort(reverse=True)
    data['meta']['words']['list'].sort(reverse=True)
    file.close()
    print('Dictionary created!')
    return data


# TODO: Controlar day count
def day_count(f):
    file = open(f, 'r', encoding="utf8")
    dates = {}
    newdate = ''
    for line in file:
        line = line.split(',')
        if line[0] == 'DateTime':
            continue
        try:
            date = str(datetime.datetime.strptime(line[0], '%d/%m/%y %H:%M:%S').date())
        except:
            date = str(datetime.datetime.strptime(line[0], '%d/%m/%Y %H:%M:%S').date())
        if date not in dates:
            dates[date] = {line[1]: 1}
            newdate = date
        elif date == newdate:
            if line[1] in dates[date]:
                dates[date][line[1]] += 1
            else:
                dates[date][line[1]] = 1

    file.close()
    return dates


def weekday_count(f):
    file = open(f, 'r', encoding="utf8")
    weekdays = {'0':{}, '1':{}, '2':{}, '3':{}, '4':{}, '5':{}, '6':{}}
    newdate = ''
    for line in file:
        line = line.split(',')
        if line[0] == 'DateTime':
            continue
        try:
            date = str(datetime.datetime.strptime(line[0], '%d/%m/%y %H:%M:%S').weekday())
        except:
            date = str(datetime.datetime.strptime(line[0], '%d/%m/%Y %H:%M:%S').weekday())
        for day in weekdays:
            if day==date:
                if line[1] in weekdays[date]:
                    weekdays[date][line[1]] += 1
                else:
                    weekdays[date][line[1]] = 1

    file.close()
    return weekdays


def save_json(_data, file='parsed_data.json'):
    data = copy.deepcopy(_data)
    temp_emojis = data['meta']['emojis']['list'][:]
    temp_words = data['meta']['words']['list'][:]
    temp_meta_names = data['meta']['users']['names'][:]
    data['meta']['emojis']['list'] = {}
    data['meta']['words']['list'] = {}
    data['meta']['users']['names'] = {}
    for names in temp_meta_names:
        data['meta']['users']['names'][names.char] = names.count
    for emoji in temp_emojis:
        data['meta']['emojis']['list'][emoji.char] = emoji.count
    for word in temp_words:
        data['meta']['words']['list'][word.char] = word.count
    for person in data['users']:
        temp_emojis = data['users'][person]['emojis']['list'][:]
        temp_words = data['users'][person]['words']['list'][:]
        data['users'][person]['emojis']['list'] = {}
        data['users'][person]['words']['list'] = {}
        for emoji in temp_emojis:
            data['users'][person]['emojis']['list'][emoji.char] = emoji.count
        for word in temp_words:
            data['users'][person]['words']['list'][word.char] = word.count
    data = (json.dumps(data))
    if file:
        f = open(file, 'w', encoding="utf8")
        f.write(data)
        f.close()
    return data


def get_names(data, number=2):
    if number == 2:
        return [
            data['meta']['users']['names'][0],
            data['meta']['users']['names'][1]
        ]
    if number == 3:
        return [
            data['meta']['users']['names'][0],
            data['meta']['users']['names'][1],
            data['meta']['users']['names'][2],
        ]


def single_plot(data, name):
    if len(data) < 30:
        N = len(data)
    else:
        N = 30
    person1 = []
    for day in data:
        temp = []
        for names in data[day]:
            if names == name:
                person1.append(data[day][name])
            if name not in temp:
                temp.append(name)
        if name not in temp:
            person1.append(0)
    ind = np.arange(N)  # the x locations for the groups
    width = 1  # the width of the bars: can also be len(x) sequence
    plt.subplots(figsize=(18, 10))
    p1 = plt.bar(ind, person1[-30:], width, color='#004445', edgecolor='white')

    plt.ylabel('Messages')
    plt.title(name)
    # order dias
    days = []
    for day in data:
        days.append(day)

    plt.xticks(ind, days[-30:], rotation=45, horizontalalignment='right')
    # media mensages por dia
    person1.sort(reverse=True)
    plt.yticks(np.arange(0, person1[0] + 5, 5))
    plt.savefig('static/singleplot.png', facecolor='#E3E6E3', dpi=1200)
    plt.show()
    return True


def daily_results(data, names, only_data=False):
    totmsg = {}
    for day in data:
        totmsg[day] = sum(data[day].values())

    max_day = ''
    max_msg = 0
    for day in totmsg:
        if totmsg[day] > max_msg:
            max_day = day
            max_msg = totmsg[day]
    if len(data) < 30:
        N = len(data)
    else:
        N = 30
    if only_data:
        return {
            'max_messages': {
                'max_day': max_day,
                'max_msg': max_msg,
            },
            'avg_messages': {
                'avg_day': round((sum(totmsg.values()) / N), 2),
            }
        }
    person1, person2 = [], []
    person1,  person2 = [], []
    for day in data:
        temp = []
        for name in data[day]:
            if name == names[0]:
                person1.append(data[day][name])
            if name == names[1]:
                person2.append(data[day][name])
            if name not in temp:
                temp.append(name)
        if names[0] not in temp:
            person1.append(0)
        if names[1] not in temp:
            person2.append(0)
    ind = np.arange(N)  # the x locations for the groups
    width = 1  # the width of the bars: can also be len(x) sequence
    plt.subplots(figsize=(18, 10))
    p1 = plt.bar(ind, person1[-30:], width, color='#004445', edgecolor='white')
    p2 = plt.bar(ind, person2[-30:], width,
                 bottom=person1[-30:], color='#6FB98F', edgecolor='white')

    plt.ylabel('Messages')
    plt.title('Messages sent every day')
    # order dias
    days = []
    for day in data:
        days.append(day)

    plt.xticks(ind, days[-30:], rotation=45, horizontalalignment='right')
    # media mensages por dia
    plt.yticks(np.arange(0, max_msg + 10, 5))
    plt.legend((p1[0], p2[0]), (names[0], names[1]))
    plt.savefig('static/plot.png', facecolor='#E3E6E3', dpi=1000)
    plt.show()
    '''
    totmsg = {}
    for day in data:
        totmsg[day] = sum(data[day].values())
    max_msg = 0
    for day in totmsg:
        if totmsg[day] > max_msg:
            max_msg = totmsg[day]
    if len(data) < 30:
        N = len(data)
    else:
        N = 30
    
    '''


def weekday_plot(data, names):
    person1, person2 = [], []
    for day in data:
        temp = []
        for name in data[day]:
            if name == names[0]:
                person1.append(data[day][name])
            if name == names[1]:
                person2.append(data[day][name])
            if name not in temp:
                temp.append(name)
        if names[0] not in temp:
            person1.append(0)
        if names[1] not in temp:
            person2.append(0)
    labels = ['M', 'T', 'W', 'T', 'F', 'S', 'X']
    x = np.arange(len(labels))
    width = 0.35  # the width of the bars
    totmes = sum(person1) + sum(person2)

    for i in range(0, 7):
        person1[i] = int(person1[i] / totmes * 100)
        person2[i] = int(person2[i] / totmes * 100)

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width / 2, person1, width, color='#004445', label=names[0])
    rects2 = ax.bar(x + width / 2, person2, width, color='#6FB98F', label=names[1])

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Percentage')
    ax.set_title('Weekly usage')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    plt.yticks(np.arange(0, 105, 10))
    ax.legend()

    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

    autolabel(rects1)
    autolabel(rects2)

    fig.tight_layout()
    plt.savefig('static/plot_7.png', facecolor='#E3E6E3', dpi=1000)
    plt.show()
    return True


def group_plot(data, names):
    totmsg = {}
    for day in data:
        totmsg[day] = sum(data[day].values())
    max_msg = 0
    for day in totmsg:
        if totmsg[day] > max_msg:
            max_msg = totmsg[day]
    if len(data) < 15:
        N = len(data)
    else:
        N = 15
    if len(names) == 3:
        person1, person2, person3 = [], [], []
        for day in data:
            temp = []
            for name in data[day]:
                if name == names[0]:
                    person1.append(data[day][name])
                if name == names[1]:
                    person2.append(data[day][name])
                if name not in temp:
                    temp.append(name)
            if names[0] not in temp:
                person1.append(0)
            if names[1] not in temp:
                person2.append(0)
        fig, ax = plt.subplots()
        ind = np.arange(N)  # the x locations for the groups
        width = 1
        days = []
        for day in data:
            days.append(day)
        p1 = plt.bar(ind, person1[-15:], width, color='#004445', edgecolor='white')
        p2 = plt.bar(ind + width, person2[-15:], width, color='#008C8E', edgecolor='white')
        p3 = plt.bar(ind + width * 2, person3[-15:], width, color='#6FB98F', edgecolor='white')
        ax.set_ylabel('Messages')
        ax.set_title('Messages group chat')
        ax.set_xticks(ind, days[-15:], rotation='horizontal', horizontalalignment='right')
        ax.set_yticks(np.arange(0, max_msg, 5))
        plt.legend((p1[0], p2[0], p3[0]), (names[0], names[1], names[2]))
        fig.tight_layout()
        plt.show()
'''
        def autolabel(rects, xpos='center'):
            """
            Attach a text label above each bar in *rects*, displaying its height.

            *xpos* indicates which side to place the text w.r.t. the center of
            the bar. It can be one of the following {'center', 'right', 'left'}.
            """

            ha = {'center': 'center', 'right': 'left', 'left': 'right'}
            offset = {'center': 0, 'right': 1, 'left': -1}

            for rect in rects:
                height = rect.get_height()
                ax.annotate('{}'.format(height),
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(offset[xpos] * 3, 3),  # use 3 points offset
                            textcoords="offset points",  # in both directions
                            ha=ha[xpos], va='bottom')

        autolabel(person1, "left")
        autolabel(person2, "center")
        autolabel(person3, "right")
'''


def simple_results(data):
    STR = '{:10} ................... {:5}'
    print("These are the result from the analysis.")
    for person in data['users'].keys():
        print('\n\nThe most used words by {} are:'.format(person))
        count = 0
        print(STR.format('Word', 'Count'))
        for word in data['users'][person]['words']['list']:
            count += 1
            if count > 5:
                break
            print(STR.format(word.char, word.count))
        print('\nThe emojis {} has used the most are:'.format(person))
        count = 0
        print(STR.format('Emojis', 'Count'))
        for word in data['users'][person]['emojis']['list']:
            count += 1
            if count > 5:
                break
            print(STR.format(word.char, word.count))


def file_prepare(f='text.txt'):
    return word_split(MessagesToCSV(f))


def main():
    f = '_chat.txt'
    f = MessagesToCSV(f)
    words = word_split(f)
    data = day_count(f)
    names = get_names(words)
    # save_json(words)
    # simple_results(words)
    # daily_results(data, names)
    # single_plot(data, "Giancarlo")
    weekday = weekday_count(f)
    weekday_plot(weekday, names)



class API:
    def __init__(self, file, cache=None):
        print(file)
        if len(file.split()) > 1:
            self.file = file.replace(' ', '_')
        else:
            self.file = file
        if cache:
            self.csv = '{}_converted.csv'.format(file)
        else:
            self.csv = MessagesToCSV(self.file)
        self.data = word_split(self.csv)
        self.days = day_count(self.csv)
        print('Day count done!')
        self._extra = {}
        self.user_cache = {}

    def user_exists(self, user):
        if user in self.data['users']:
            return True

    def getMeta(self):
        return self.data['meta']

    def getJson(self):
        return save_json(self.data, None)

    def getTopEmojis(self, n=5):
        return self.data['meta']['emojis']['list'][:n]

    def getEmojis(self, n=5):
        return self.data['meta']['emojis']['list'][n:]

    def getTopEmojisUser(self, user, n=5):
        if self.user_exists(user):
            return self.data['users'][user]['emojis']['list'][:n]

    def getEmojisUser(self, user):
        if self.user_exists(user):
            return self.data['users'][user]['emojis']['list']

    def getEmojiCount(self, user):
        if self.user_exists(user):
            return self.data['users'][user]['emojis']['count']

    def getWords(self):
        return self.data['meta']['words']['list']

    def getTopWords(self, n=5):
        return self.data['meta']['words']['list'][:n]

    def getTopWordsUser(self, user, n=5):
        if self.user_exists(user):
            return self.data['users'][user]['words']['list'][:n]

    def getWordsUser(self, user):
        if self.user_exists(user):
            return self.data['users'][user]['words']['list']

    def getTopActiveUsers(self, n=5):
        return self.data['meta']['users']['names'][:n]

    def getUsers(self):
        return self.data['meta']['users']['names']

    def getWordsCount(self, user):
        if self.user_exists(user):
            return self.data['users'][user]['words']['count']

    def getUser(self, user):
        if self.user_exists(user):
            return self.data['users'][user]

    def getFirstTwoNames(self):
        return get_names(self.data)

    def generateGraph(self, names, extra=False):
        print('Generating graphs!')
        for name in names:
            if name not in self.data['meta']['users']['names']:
                return False
        if len(names) == 2:
            data = self.days
            extra = daily_results(data, names, only_data=extra)
            if extra:
                return extra
            weekday = weekday_count(self.csv)
            weekday_plot(weekday, names)
            return True
        return False

    def generateSingleGraph(self, user):
        if self.user_exists(user):
            return single_plot(day_count(self.csv), user)

    def getExtra(self):
        return self.generateGraph(get_names(self.data), extra=True)

    def getNumberUsers(self):
        return len(self.data['meta']['users']['names'])


if __name__ == '__main__':
    main()
