import re

REGEX_IOS = '(\[[0-3]?[0-9]\/[0-1]?[0-9]\/[0-9][0-9][ ][0-2]?[0-9]\:[0-6][0-9]\:[0-5][0-9]\])'
REGEX_ANDROID = '([0-3]?[0-9]\/[0-1]?[0-9]\/[2]?[0-2]?[0-9][0-9]\,[ ][0-2]?[0-9]\:[0-5][0-9])'


def check_file(line):
    r_ios = re.match(REGEX_IOS, line)
    if r_ios:
        return 'ios'
    r_android = re.match(REGEX_ANDROID, line)
    if r_android:
        return 'android'
    return False


if __name__ == '__main__':
    file = input("File >>")
    f = open(file, 'r')
    for i in f:
        print(i)
        print(check_file(i))
        break
