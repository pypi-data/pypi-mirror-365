# system imports.
from datetime import datetime
import glob
import os

# our package imports.
from .smartinspectexception import SmartInspectException

# auto-generate the "__all__" variable with classes decorated with "@export".
from .siutils import export


@export
class SIFileHelper:
    """
    Responsible for the log file rotate management as used by the
    SIFileProtocol class.

    This class implements a flexible log file rotate management
    system. For a detailed description of how to use this class,
    please refer to the documentation of the Initialize(DateTime)
    and Update(DateTime) methods and the Mode property.

    Threadsafety:
        This class is not guaranteed to be thread-safe.
    """

    ALREADY_EXISTS_SUFFIX:str = "a"

    # Do not change - required by SI console.
    DATETIME_FORMAT:str = "yyyy-MM-dd-HH-mm-ss"
    DATETIME_FORMAT_LEN:int = len(DATETIME_FORMAT)
    DATETIME_SEPARATOR:chr = '-'
    DATETIME_TOKENS:int = 6


    @staticmethod
    def _ExpandFileName(baseName:str) -> str:
        """
        Returns a new log file path that includes the base name path along with a timestamp value.

        Args:
            baseName (str):
                Base name path of a log file (e.g. "C:\\logfile-hourly.txt").

        Returns:
            A new log file path that includes the base name path along with a 
            timestamp value (e.g. "C:\\logfile-hourly-2023-05-22-12-00-00.txt").
        """
        # get the file prefix and extension from the base file name (e.g. "C:\\logfile-hourly" and ".txt").
        fileExtn:str = ""
        filePrefix, fileExtn = os.path.splitext(baseName)

        # formulate the log file path (e.g. "C:\\logfile-hourly-2023-05-22-15-31-11.txt")
        # IMPORTANT: date has to be in "yyyy-MM-dd-HH-mm-ss" format!!!
        result:str = filePrefix + \
                     SIFileHelper.DATETIME_SEPARATOR + \
                     datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S") + \
                     fileExtn

        # Append a special character/suffix to the expanded
        # file name if the file already exists in order to
        # not overwrite an existing log file. 

        while (os.path.isfile(result)):
        
            # if the log file path already exists, then add
            # the ALREADY_EXISTS_SUFFIX after the timestamp.
            # e.g. "C:\\logfile-hourly-2023-05-22-15-31-11a.txt"
            filePrefix, fileExtn = os.path.splitext(result)

            # formulate the log file path (e.g. "C:\\logfile-hourly-2023-05-22-15-31-11a.txt")
            result:str = filePrefix + \
                         SIFileHelper.ALREADY_EXISTS_SUFFIX + \
                         fileExtn

        return result


    @staticmethod
    def _FindFileName(baseName:str) -> str:
        """
        Searches for the first log file that matches the specified base name path.

        Args:
            baseName (str):
                Base name path of a log file (e.g. "C:\\logfile-hourly.txt").

        Returns:
            The first (newest) matching log file name that was found; otherwise, null if no log files were found.

        This function removes any files from a directory list that do not conform to a valid log-file naming format.
        """
        files:list[str] = SIFileHelper._GetFiles(baseName)

        if ((files == None) or (len(files) == 0)):
            return None

        return files[len(files) - 1]  # the newest


    @staticmethod
    def _GetFiles(baseName:str) -> list[str]:
        """
        Returns a string array of all matching log files that begin with the specified baseName.

        Args:
            baseName (str):
                Base name path of a log file (e.g. "C:\\logfile-hourly.txt").

        Returns:
            A string array of all matching log files that begin with the specified baseName.
        """
        # get the filename and extension value from the base path (e.g. "logfile-hourly.txt").
        fileName = os.path.basename(baseName)

        # get the file name and extension from the base file name (e.g. "logfile-hourly" and ".txt").
        fileExtn:str = ""
        fileName, fileExtn = os.path.splitext(fileName)

        # create file pattern to search for existing log files (e.g. "logfile-hourly-*.txt").
        pattern:str = fileName + "-*" + fileExtn

        # get directory name from base name path (e.g. "C:\\").
        fileDir:str = os.path.dirname(baseName)

        # if directory name could not be found then use current directory specification.
        if ((fileDir == None) or (len(fileDir) == 0)):
            fileDir = "."

        # get the list of files in the directory that match our search pattern, and sort them.
        # note that this COULD contain other files besides SI log files.
        files:list[str] = glob.glob(fileDir + os.sep + pattern, recursive=False)
        files.sort()

        # Only return files with a valid file name (see
        # _IsValidFile) and ignore all others.
        # Directory.GetFiles lists all files which match the
        # given path, so it might return files which are not
        # really related to our current log file. */

        # only return files with a valid log-file naming format.
        return SIFileHelper._ValidateFiles(baseName, files)


    @staticmethod
    def _IsValidFile(baseName:str, path:str) -> bool:
        """ 
        Determines if a baseName and path are in valid log-file naming format or not.

        Args:
            baseName (str):
                Base name path of a log file (e.g. "C:\\logfile-hourly.txt").
            path (str):
                Full name of a log file, which is comprised of the base name path and a timestamp before the extension (e.g. "C:\\logfile-hourly-2023-05-22-00-49-55.txt").

        Returns:
            boolean
                True if the timestamp portion of the filename path argument could be converted to a datetime object, indicating a valid log file path; otherwise, False.
        """
        fileDate:datetime
        fileDateFound:bool = False
        fileDateFound,fileDate = SIFileHelper._TryGetFileDate(baseName, path)
        return fileDateFound


    @staticmethod
    def _TryGetFileDate(baseName:str, path:str) -> bool:
        """ 
        Trys to return a datetime object of the timestamp portion of the filename path argument.

        Args:
            baseName (str):
                Base name path of a log file (e.g. "C:\\logfile-hourly.txt").
            path (str):
                Full name of a log file, which is comprised of the base name path and a timestamp before the extension (e.g. "C:\\logfile-hourly-2023-05-22-00-49-55.txt").

        Returns:
            boolean
                True if the timestamp portion of the filename path argument could be converted to a datetime object.
            fileDate
                The datetime object of the timestamp portion of the filename path argument.  Value is not valid if the return value is False.
        """
        fileDate:datetime = datetime.min # DateTime.MinValue; # Required

        # get the file name (base name + timestamp + extension - e.g. "logfile-hourly-2023-05-22-00-49-55.txt").
        fileName:str = os.path.basename(path)

        # drop the path and extension from the base name (e.g. from "C:\\logfile-hourly.txt" to "logfile-hourly").
        baseName = os.path.splitext(os.path.basename(baseName))[0]

        # In order to avoid possible bugs with the creation
        # time of file names (log files on Windows or Samba
        # shares, for instance), we parse the name of the log
        # file and do not use its creation time.

        # find the position in the filename where the basename starts.
        # note that this position should be zero, if the filename is formatted properly.
        # if it's not zero, then  we are done.
        index:int = fileName.rfind(baseName)
        if (index != 0):
            return False, None

        # get the timestamp portion of the filename (e.g. "2023-05-22-00-49-55").
        value:str = os.path.splitext(fileName[len(baseName) + 1:])[0]

        # Strip any added ALREADY_EXISTS_SUFFIX characters.
        # This can happen if we are non-append mode and need
        # to add this special character/suffix in order to
        # not override an existing file.

        if (len(value) > SIFileHelper.DATETIME_FORMAT_LEN):
            value = value.Substring(0, SIFileHelper.DATETIME_FORMAT_LEN)

        # try to create a datetime object from the file timestamp.
        fileDate:datetime
        fileDateParsedOk:bool = False
        fileDateParsedOk,fileDate = SIFileHelper._TryParseFileDate(value)
        if (not fileDateParsedOk):
            return False, None

        return True, fileDate


    @staticmethod
    def _TryParseFileDate(fileDate:str) -> bool:
        """
        Tries to create a datetime object of a timestamp string value.

        Args:
            fileDate (str):
                The timestamp string value in "yyyy-MM-dd-HH-mm-ss" format (e.g. "2023-05-22-00-49-55").

        Returns:
            boolean:
                True if the timestamp string value could be converted to a datetime object; otherwise, False.
            dateTime:
                The datetime object of the timestamp string.  Value is invalid if the return value is False.
        """
        dateTime = datetime.min  # Required

        if (fileDate == None):
            return False, None

        # if it's not our format length, then don't bother.
        if (len(fileDate) != SIFileHelper.DATETIME_FORMAT_LEN):
            return False, None

        # ensure value is all digits and separator characters.
        for i in range(len(fileDate)):
        
            c:str = fileDate[i]
            if ((not c.isdigit()) and (c != SIFileHelper.DATETIME_SEPARATOR)):
                return False, None
            
        # create an array of timestamp values, delimited by separator character.
        # e.g. [2023,05,22,00,49,55]
        values = fileDate.split(SIFileHelper.DATETIME_SEPARATOR)

        # if we don't have the exact number of tokens then it's an invalid timestamp - don't bother.
        if ((values == None) or (len(values) != SIFileHelper.DATETIME_TOKENS)):
            return False, None

        try:
        
            # create new date based upon array timestamp values.
            dateTime = datetime(
                int(values[0]), # Year
                int(values[1]), # Month
                int(values[2]), # Day
                int(values[3]), # Hour
                int(values[4]), # Minute
                int(values[5])  # Second
            )
        
        except Exception as ex:
        
            return False, None
        
        return True, dateTime


    @staticmethod
    def _ValidateFiles(baseName:str, files:list[str]) -> list[str]:
        """
        Returns a list of all VALID matching log file paths that begin with the specified baseName.

        Args:
            baseName (str):
                Base name path of a log file (e.g. "C:\\logfile-hourly.txt").
            files (list[str]):
                A list of POSSIBLE log file paths that match the base name of the log file.

        Returns:
            A list of all VALID matching log file paths that begin with the specified baseName.

        This function removes any files from a directory list that do not conform to a valid log-file naming format.
        """
        valid:int = 0

        for i in range(len(files)):
        
            # check each file to ensure it is a valid log file naming format.
            if (SIFileHelper._IsValidFile(baseName, files[i])):
                valid = valid + 1
            else:
                files[i] = ""       # See below

        # did we filter any files? if so, then no need to copy the list.
        if (valid == len(files)):
            return files            # No need to copy

        # copy the list, excluding filtered entries.
        filteredfiles:list[str] = [""] * valid
        j:int = 0
        for i in range(len(files)):
        
            if (files[i] != ""):    # See above
                filteredfiles[j] = files[i]
                j = j + 1

        return filteredfiles


    @staticmethod
    def DeleteFiles(baseName:str, maxParts:int) -> None:
        """
        Deletes existing log files that fall outside the maximum retention range.

        Args:
            baseName (str):
                Base name path of a log file (e.g. "C:\\logfile-hourly.txt").
            maxParts (int):
                Maximum number of files to keep for the base name path.
        """
        # get a list of all valid log files that exist in the base log file path.
        # note that this will return a sorted list of files, with oldest files listed first.
        files:list[str] = SIFileHelper._GetFiles(baseName)

        if (files == None):
            return;

        for i in range(len(files)):
        
            # stop deleting files after we reach the retention range.
            if (i + maxParts >= len(files)):
                break

            try:
            
                # try to delete the file.
                os.remove(files[i])
            
            except Exception as ex:
            
                # ignore exceptions, as we can't do anything about it.
                # we will try to delete it the next time this method is called.
                pass


    @staticmethod
    def GetFileDate(baseName:str, path:str) -> datetime:
        """ 
        Returns a datetime object of the timestamp portion of the filename path argument.

        Args:
            baseName (str):
                Base name path of a log file (e.g. "C:\\logfile-hourly.txt").
            path (str):
                Full name of a log file, which is comprised of the base name path and a timestamp before the extension (e.g. "C:\\logfile-hourly-2023-05-22-00-49-55.txt").

        Returns:
            A datetime object of the timestamp portion of the path argument filename.

        Raises:
            SmartInspectException:
                Thrown if the datetime object could not be created from the timestamp portion of the path argument filename.
        """
        fileDate:datetime
        fileDateFound:bool = False

        fileDateFound,fileDate = SIFileHelper._TryGetFileDate(baseName, path)
        if (not fileDateFound):
            raise SmartInspectException("Invalid filename in the path.")

        return fileDate


    @staticmethod
    def GetFileName(baseName:str, append:bool) -> str:
        """
        Returns a log file path.

        Args:
            baseName (str):
                Base name path of a log file (e.g. "C:\\logfile-hourly.txt").
            append (bool):
                True to append to the existing latest log file; otherwise, False to create 
                a new log file path from the specified base name path.

        Returns:
            A log file path that includes the base name path along with a 
            timestamp value (e.g. "C:\\logfile-hourly-2023-05-22-12-00-00.txt").

        If no rotating log file was found, or we are not appending
        to an existing file, then a new log file will be created.
        """
        # In rotating mode, we need to differentiate between
        # append and non-append mode. In append mode, we try
        # to use an already existing file. In non-append mode,
        # we just use a new file with the current time-stamp
        # appended. */

        if (append):
        
            # find the latest rotating log file that exists.
            fileName:str = SIFileHelper._FindFileName(baseName)

            if (fileName != None):
                return fileName

        # if no rotating log file was found, or we are not appending
        # to an existing file, then create a new log file.
        return SIFileHelper._ExpandFileName(baseName)
