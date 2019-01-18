list = ['kumar','satheesh','rajan']

BOLD = '\033[1m'
END = '\033[0m'

for each in list:
    print('{}{}{}'.format(BOLD, each, END))