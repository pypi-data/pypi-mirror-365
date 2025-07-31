### Welcome

This is a small module that can be used to generate prompts for text-to-image generative AI.

The package is available on [pypi](https://pypi.org/project/prompter-r3ap3rpy).

In order to install the package you would use the following command.

``` bash
pip install propmpter-r3ap3rpy
```

Then all you have to do is import the module and use it as follows.

``` python
from prompter import PromptGenerator
p = PromptGenerator()
p()
'Madonna grilling at Jerusalem.'
p()
'Natalie Portman cycling at Mumbai.'
p()
'John von Neumann baseball at Tower of London.'
```

You have the option to update the **data.json**.

``` python
from prompter import PromptGenerator
p = PromptGenerator()
p.update("People","Dani Ernő")
```

When updating the data the section is converted to lower-case and verified, also the value is checked whether it's in the section converted to lower-case before checking, if not it's added, otherwise an exception is thrown.

You can also delete from the **data.json** entries. By default it will delete first occurence from each section, but you can pass the **all_occurence=True** to remove all occurences.

``` python
from prompter import PromptGenerator
p = PromptGenerator()
p.delete("Dani Ernő") # deletes value from every sections
p.delete("people","Pablo Picasso") # deletes value from given section
```

You have the option to get basic stats from your database.

``` python
from prompter import PromptGenerator
p = PromptGenerator()
p.stats
###############################################
#        people        #         107          #
#       activity       #         107          #
#       location       #         107          #
###############################################
```

The **details** attribute will print the content in a table format to your terminal.

You have **restore_db()** which is a static method, it allows you to restore any backups in the **data** folder, the **backup_db()** which is an instance method allows you to backup the actual state of the database to a default or custom filename!

In order to run the tests you can do the following.

``` bash
git clone https://github.com/r3ap3rpy/prompter
cd prompter
pip install -r requirements.txt
pytest -vvvvv
```

You can also use **pylint**, currently the passing score is **9,5**, the workflow will fail if score goes under it.

