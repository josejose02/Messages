"""
TODO: Check multi line messages
TODO: Android CSV creation
Python program that converts a python conversation to a .csv file
"""
import string
from regex import check_file

EXPORT = '{}_converted.csv'

REMOVE = [
    '<Media omitted>'
]

def MessagesToCSV(fl):
    return_name = EXPORT.format(fl)
    file_in = open(fl, 'r', encoding="utf8")
    file_out = open(return_name, 'w', encoding="utf8")
    file_out.write('DateTime,Name,Message')
    for line in file_in:
        type_device = check_file(line)
        break
    if type_device == 'ios':
        '''
        [17/10/18 19:55:29] Name: Message
        '''
        for line in file_in:
            check = check_file(line)
            for check_remove in REMOVE:
                if check_remove in line:
                    continue
            if not check:
                file_out.write(' ' + line.replace('\n', '').translate(str.maketrans('', '', string.punctuation)))
                continue
            line = line.split()
            invalid = True
            for w in line[2:]:
                if ':' in w:
                    invalid = False
                    break
            if invalid:
                continue
            try:
                if '+' in line[2]:
                    for o in range(3, len(line)):
                        line[2] += line[o]
                        if ':' in line[o]:
                            line[o] = ''
                            break
                        line[o] = ''
                out = '\n{} {},{},{}'.format(
                    line[0].replace('[', ''),
                    line[1].replace(']', ''),
                    line[2].replace(':', ''),
                    ' '.join(line[3:]).translate(str.maketrans('', '', string.punctuation))
                )
                file_out.write(out)
            except:
                # Multi-Line Problem
                pass
    elif type_device == 'android':
        '''
        17/10/2018, 19:55 - Name: Message
        '''
        for line in file_in:
            check = check_file(line)
            for check_remove in REMOVE:
                if check_remove in line:
                    continue
            if not check:
                file_out.write(' ' + line.replace('\n', '').translate(str.maketrans('', '', string.punctuation)))
                continue
            line = line.split('-')
            name = line[1].split(':')[0]
            time = line[0].replace(' ', '').split(',')
            message = line[1].split(':')[1:]
            if ':' not in line[1]:
                continue
            try:
                out = '\n{} {}:00,{},{}'.format(
                    time[0],
                    time[1],
                    name,
                    message[0].replace('\n', '').translate(str.maketrans('', '', string.punctuation))
                )
                file_out.write(out)
            except:
                # Multi-Line Problem
                pass
    else:
        raise TypeError('Not a valid whatsapp file!')
    file_in.close()
    file_out.close()
    print('CSV Conversion Done!')
    return return_name


if __name__ == '__main__':
    file = input("File >>")
    csv = MessagesToCSV(file)
    print('File ({}) ready!'.format(csv))