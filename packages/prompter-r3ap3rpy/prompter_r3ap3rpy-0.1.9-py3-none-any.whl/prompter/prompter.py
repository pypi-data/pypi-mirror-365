""" Main module file. """
import json
import os
import random
import shutil
from datetime import datetime
from .customexceptions import *

dirname, filename = os.path.split(os.path.abspath(__file__))

class PromptGenerator:
    """ Main class of the module that drives the logic. """
    expected_sections = ['people','activity','location']
    def __init__(self, module = dirname, folder = 'data', file = 'data.json' ):
        self.module = module
        self.folder = folder
        self.file = file

        if not os.path.isfile(os.path.sep.join([module,folder,file])):
            raise PromptDataFileNotFound(f"Cannot find file {file} at location {os.path.sep.join([module,folder])}")

        try:
            with open(os.path.sep.join([module,folder,file]), encoding = "utf-8") as jfile:
                self.data = json.loads(jfile.read())
        except PermissionError as e:
            raise PromptDataFilePermissionError(f"Could not read the {file}, permission denied") from e
        except json.decoder.JSONDecodeError as e:
            raise PromptDataFileCorrupted("Invalid structure of the data, likely not json!") from e
        except Exception as e:
            raise SystemExit(f"The following error prevented initialization: {e}") from e

        if not self.data:
            raise PromptDataEmpty("The file was empty, can't find any sections!")

        self.sections = self.data.keys()

        if self.expected_sections != list(self.sections):
            raise PromptInconsistentSectionsError(f"The source file seems to be corrupted, expected sections {','.join(self.expected_sections)} while sections in the file are {','.join(self.sections)}")

    def __call__(self):
        """ Allow users to call an instance to get a random prompt! """
        return f"{random.choice(self.data['people'])} {random.choice(self.data['activity']).lower()} at {random.choice(self.data['location'])}."

    def update(self, section, old_value, new_value, all_occurence = False):
        """ Allow users to update data.json database """
        if not section.lower() in self.sections:
            raise PrompterSectionUpdateException(f"Either the following sections are allowed to be updated: {','.join(self.sections)}")
        if all_occurence:
            while (count := self.data[section.lower()].count(old_value)) != 0:
                self.data[section.lower()][self.data[section.lower()].index(old_value)] = new_value
        else:
            if self.data[section.lower()].count(old_value):
                self.data[section.lower()][self.data[section.lower()].index(old_value)] = new_value
        with open(os.path.sep.join([self.module,self.folder,self.file]),'w', encoding = "utf-8") as jfile:
            jfile.write(json.dumps(self.data))
    def delete(self, *args, all_occurence = False):
        """ Deletes a virtual row from the data.json, finds the index matching the row and deletes the item at index from all rows. """
        if len(args) == 2:
            section, value = args
            if not section.lower() in self.sections:
                raise PrompterSectionDeleteException(f"The specified section {section} does not exist, these are the available sections: {','.join(self.sections)}")
            if value in self.data[section.lower()]:
                self.data[section.lower()].remove(value)
                with open(os.path.sep.join([self.module,self.folder,self.file]),'w', encoding = "utf-8") as jfile:
                    jfile.write(json.dumps(self.data))
            else:
                raise PrompterSectionDeleteException(f"The specified value {value} does not exist in section: {section}, cannot delete!")
        elif len(args) == 1:
            value = args[0]
            for section in self.sections:
                if all_occurence:
                    while (count := self.data[section].count(value)) != 0:
                        self.data[section].remove(value)
                else:
                    if self.data[section].count(value):
                        self.data[section].remove(value)
            with open(os.path.sep.join([self.module,self.folder,self.file]),'w', encoding = "utf-8") as jfile:
                jfile.write(json.dumps(self.data))
        else:
            raise PrompterDeletionArgsError("You either have to speciy one argument to delete value from all the sections, or specify section and value to delete only from the given section.")

    def add(self, *args):
        """ You may add new entries to the data.json, the only criteria is that none of the values you specify should exist in either of the columns. """
        if len(args) != len(self.sections):
            raise PrompterAddError(f"In order to add a row you have to provide {len(self.sections)} values for the current sections: {','.join(self.sections)}")
        for i in range(len(args)):
            for j in self.data[list(self.sections)[i]]:
                if args[i] in self.data[list(self.sections)[i]]:
                    raise PrompterAddError(f"We already have a value {args[i]} in section {list(self.sections)[i]}")
        try:
            for i in range(len(args)):
                self.data[list(self.sections)[i]].append(args[i])
            with open(os.path.sep.join([self.module,self.folder,self.file]),'w', encoding = "utf-8") as jfile:
                jfile.write(json.dumps(self.data))
        except Exception as e:
            raise PrompterAddError(f"Failed to add new data because: {e}") from e

    def add_to_section(self, section, value):
        """ This function will add a given value to the specified section """
        if not section.lower() in self.sections:
            raise PrompterSectionAddException(f"The specified section {section} does not exist, these are the available sections: {','.join(self.sections)}")
        if value in self.data[section.lower()]:
            raise PrompterSectionAddException(f"The specified value is already in the section: {section}")
        self.data[section.lower()].append(value)
        with open(os.path.sep.join([self.module,self.folder,self.file]),'w', encoding = "utf-8") as jfile:
            jfile.write(json.dumps(self.data))

    def widest_cell(self):
        """ Returns the width of the widest cell in the table, used for formatting. """
        column_width = 0
        for key in self.data:
            if len(key) > column_width:
                column_width = len(key)
            for row in self.data[key]:
                if len(row) > column_width:
                    column_width = len(row)
        return column_width

    def longest_section(self):
        """ Returns the longest section's length. """
        return max(len(self.data[key]) for key in self.data.keys())

    @staticmethod
    def restore_db(original = False, backup_file = None):
        """ This function restores backup from either the origin or the selected file. """
        rdirname, _ = os.path.split(os.path.abspath(__file__))
        origin = os.path.sep.join([rdirname, 'data','data.json.original'])
        if original:
            print("Overwriting the data.json file with data.json.original")
            if os.path.isfile(origin):
                try:
                    shutil.copy(origin, os.path.sep.join([rdirname, 'data','data.json']))
                except Exception as e:
                    raise PrompterRestoreOriginalCopyError(f"Could not restore data.json.original because of the following error when calling shutil.copy : {e}") from e
            else:
                raise PrompterRestoreOriginalDbNotFound(f"Cannot find origin at {origin}, restore is impossible!")
            return True
        else:
            if backup_file is not None:
                print(f"Restoring specified file: {backup_file}")
                to_restore = os.path.sep.join([dirname, 'data', backup_file])
                data_file = os.path.sep.join([dirname, 'data', 'data.json'])
                shutil.copy(to_restore, data_file)
                return True
            else:
                backups = [ _ for _ in os.listdir(os.path.sep.join([dirname,'data'])) if (not _ in ['data.json.original','data.json']) and ('.json' in _)]
                if backups:
                    backups.append('Exit')
                    options = list(enumerate(backups))
                    os.system('clear')
                    print("Available backups: ")
                    for _ in options:
                        print(f"\t {_[0]} - {_[1]}")
                    while not (choice := int(input("Which one to restore: "))) in [_[0] for _ in options]:
                        os.system('clear')
                        print("Available backups: ")
                        for _ in options:
                            print(f"\t {_[0]} - {_[1]}")
                    print(f"You have choosen: {options[choice][1]}")
                    if options[choice][1] == 'Exit':
                        print("Skipping restore...")
                    else:
                        print("Restoring file...")
                        to_restore = os.path.sep.join([dirname, 'data', options[choice][1]])
                        data_file = os.path.sep.join([dirname, 'data', 'data.json'])
                        shutil.copy(to_restore, data_file)
                else:
                    raise PrompterRestoreNoBackupsFound("No valid backups were found, restore is impossible!")
    def backup_db(self, backup_file = None):
        """ This function creates a new backup from the database in-memory to a given filename or a filename with the timestamp. """
        print("Save  database with timestamp!")
        if backup_file is not None:
            backup_file += "_data.json"
            print(f"Saving database with name: {backup_file}")
        else:
            stamp = datetime.now()
            backup_file = f"{stamp.year}_{stamp.month}_{stamp.day}_{stamp.hour}_{stamp.minute}_{stamp.second}_data.json"
            print(f"Using timestamp based backup: {backup_file}")
        with open(os.path.sep.join([self.module,self.folder,backup_file]),'w', encoding = "utf-8") as jfile:
            jfile.write(json.dumps(self.data))
        return True



    @property
    def raw_data(self):
        """ Return raw database content """
        return self.data
    @property
    def stats(self):
        """ Function to print short stats about sections and number of values. """
        keys = self.data.keys()
        print("#" * 47)
        for key in self.data:
            print(f"# {key:^20} # {len(self.data[key]):^20} #")
        print("#" * 47)

    @property
    def details(self, padding = 10):
        """ Detailed information about the data.json content. """
        max_length = self.longest_section()
        column_width = self.widest_cell()
        print("#" * (column_width * len(self.data) + padding))
        print("# " +" # ".join(f"{key:^{column_width}}" for key in self.data.keys()) + " #")
        print("#" * (column_width * len(self.data) + padding))
        for i in range(max_length):
            row = []
            for key in self.data:
                row.append(self.data[key][i] if i < len(self.data[key]) else "N.A.")
            print("# " +" # ".join(f"{key:^{column_width}}" for key in row) + " #")
        print("#" * (column_width * len(self.data) + padding))
