import os
import pickle
import subprocess
import PySimpleGUI as sg

sg.ChangeLookAndFeel('Dark')

menu_def = [['&Help', '&About...']]
right_click_menu = ['Right', ['&Explore', 'Close']]

class Gui:
    def __init__(self):
        self.layout = [[sg.Menu(menu_def)],
                       [sg.T('Search Term', size=(10, 1)),
                        sg.Input(size=(45, 1), focus=True, key='TERM'),
                        sg.Radio('Contains', group_id='choice', key='CONTAINS', default=True),
                        sg.Radio('StartsWith', group_id='choice', key='STARTSWITH'),
                        sg.Radio('EndsWith', group_id='choice', key='ENDSWITH')],
                       [sg.T('Root Path', size=(10, 1)),
                        sg.Input('C:/', size=(45, 1), key='PATH'),
                        sg.FolderBrowse('Browse'),
                        sg.Button('Re-Index', size=(10, 1), key='_INDEX_'),
                        sg.Button('Search', size=(10, 1), bind_return_key=True, key='_SEARCH_')],
                       [sg.MLine(size=(110, 30), key='_ML_' + sg.WRITE_ONLY_KEY, right_click_menu=right_click_menu, enable_events=True, reroute_stdout=True, autoscroll=True)],
                       [sg.Button(button_text='Show In Explorer', key='Explore'),
                        sg.Button('Clear', key='CLEAR'),
                        sg.Button('Exit')]]

        self.window = sg.Window('File Search Engine', self.layout)


class SearchEngine:
    def __init__(self):
        self.file_index = []
        self.results = []
        self.matches = 0
        self.records = 0

    def create_new_index(self, values):
        """ create a new index and save to file """
        root_path = values['PATH']
        self.file_index = [(root, files) for root, dirs, files in os.walk(root_path) if files]

        # save to file
        with open('file_index.pkl', 'wb') as f:
            pickle.dump(self.file_index, f)

    def load_existing_index(self):
        """ load existing index """
        try:
            with open('file_index.pkl', 'rb') as f:
                self.file_index = pickle.load(f)
        except:
            self.file_index = []

    def search(self, values):
        """ search for term based on search type """

        # reset variables
        self.results.clear()
        self.matches = 0
        self.records = 0
        term = values['TERM']

        # prevents empty search
        if values['TERM'] == '':
            print('>> Please enter search term.')
            return

        # perform search
        for path, files in self.file_index:
            for file in files:
                self.records += 1
                if (values['CONTAINS'] and term in file or
                        values['STARTSWITH'] and file.startswith(term) or
                        values['ENDSWITH'] and file.endswith(term)):

                    result = path.replace('\\', '/') + '/' + file
                    self.results.append(result)
                    self.matches += 1
                else:
                    continue

        # save search results to file
        with open('search_results.txt', 'w', encoding='utf-8') as f:
            for row in self.results:
                f.write(row + '\n')


def main():
    g = Gui()
    s = SearchEngine()
    s.load_existing_index()

    while True:
        event, values = g.window.Read()

        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        if event == 'About...':
            sg.popup('Upon first use:\n'
                     '1. Choose a path to search from and press Re-Index\n'
                     '2. Wait for indexing to finish\n'
                     '3. Search for your desired files\n\n'
                     'Exploring files:\n'
                     'Highlight the file path and either right click and hit "Explore" or click the "Show In '
                     'Explorer" button.',
                     title='About')
        elif event == 'CLEAR':
            g.window['_ML_' + sg.WRITE_ONLY_KEY].Update('')
            g.window['TERM'].Update('')
        elif event == 'Explore':
            try:
                selection = g.window['_ML_' + sg.WRITE_ONLY_KEY].Widget.selection_get()
                file = selection.replace('/', '\\')
                subprocess.Popen(r'explorer /select, ' + file)
            except:
                print('Nothing selected.')
        elif event == '_INDEX_':
            print('>> Please wait while index is being created...')
            s.create_new_index(values)

            print()
            print('>> New Index has been created.')
            print()
        elif event == '_SEARCH_':
            s.search(values)

            # print results to output element
            print()
            print('>> This query produced the following matches: \n')
            for result in s.results:
                print(result)

            print()
            print('>> There were {:,d} matches out of {:,d} records searched.'.format(s.matches, s.records))
            print()


main()
