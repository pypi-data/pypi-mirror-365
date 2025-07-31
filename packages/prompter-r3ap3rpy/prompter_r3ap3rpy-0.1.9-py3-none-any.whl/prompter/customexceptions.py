""" Module for custom exception definition """
class PrompterException(Exception):
    """ Inherit from base exception """
    ...

class PrompterSectionUpdateException(PrompterException):
    """ Exceptions for section updates """
    ...

class PromptDataEmpty(PrompterException):
    """ Exceptions for no data """
    ...

class PromptDataFileNotFound(PrompterException):
    """ Exception for missing database file """
    ...

class PromptDataFilePermissionError(PrompterException):
    """ Exception if permission gets broken """
    ...

class PromptDataFileCorrupted(PrompterException):
    """ Exception for corrupted datafile """
    ...

class PromptInconsistentSectionsError(PrompterException):
    """ Exception for section inconsistency """
    ...

class PrompterSectionValueExists(PrompterException):
    """ Exception for duplicate sections """
    ...

class PrompterDeletionArgsError(PrompterException):
    """ Exception for deletion argument error """
    ...

class PrompterSectionDeleteException(PrompterException):
    """ Exception for section deletion """
    ...

class PrompterAddError(PrompterException):
    """ Exception for addition error """
    ...

class PrompterSectionAddException(PrompterException):
    """ Exception for section add """
    ...

class PrompterRestoreOriginalDbNotFound(PrompterException):
    """ Exception for original DB restoration """
    ...

class PrompterRestoreOriginalCopyError(PrompterException):
    """ Exception for copy original """
    ...

class PrompterExitRestore(SystemExit):
    """ Restore exception graceful exit """
    ...

class PrompterRestoreNoBackupsFound(PrompterException):
    """ Exception for attempting to restore when there is nothing to restore """
    ...
