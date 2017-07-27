import os
import time
import sys

class Backup:
    TIME_FORMAT = "%Y_%m_%d_%a_%H_%M_%S"

    @staticmethod
    def encrypt(encryptedMethod, password, filename, outFilename):
        if not (os.path.exists(filename) and os.path.isfile(filename)):
            return False

        os.system("openssl enc -%s -in %s -out %s -k %s" % (encryptedMethod, filename, outFilename, password))
        return True

    @staticmethod
    def decrypt(decryptedMethod, password, filename, outFilename):
        if not (os.path.exists(filename) and os.path.isfile(filename)):
            return False

        os.system("openssl enc -d -%s -in %s -out %s -k %s" % (decryptedMethod, filename, outFilename, password))
        return True

    @staticmethod
    def backup(filename, backupDirectory):
        backupDirectory = backupDirectory.replace("~", os.environ['HOME'])
        if not os.path.exists(backupDirectory):
            os.system("mkdir " + backupDirectory)

        if not (os.path.exists(filename) and os.path.isfile(filename)):
            return None

        if backupDirectory[-1] != '/':
            backupDirectory += '/'

        outFilename = filename.split('/')[-1] + "." + time.strftime(Backup.TIME_FORMAT) + '.backup'
        os.system('cp %s %s' % (filename, backupDirectory + outFilename))
        return backupDirectory + outFilename

    @staticmethod
    def backup_number(filename, backupDirectory):
        if not (os.path.exists(backupDirectory)):
            return None

        result = 0
        for each in os.listdir(backupDirectory):
            if each.startswith(filename):
                result += 1

        return result

    @staticmethod
    def delete_oldest_backup(filename, backupDirectory):
        backupDirectory = backupDirectory.replace("~", os.environ['HOME'])
        backups = filter(lambda x: x.startswith(filename), os.listdir(backupDirectory))
        if len(backups) <= 0:
            return False

        length=len(filename.split('.'))

        def compare_time(filename1, filename2):
            return time.mktime(time.strptime(filename1.split('.')[length], Backup.TIME_FORMAT)) > time.mktime(time.strptime(filename2.split('.')[length], Backup.TIME_FORMAT))

        backups.sort(cmp=compare_time)
        if backupDirectory[-1] != '/':
            backupDirectory += '/'

        os.remove(backupDirectory + backups[0])
        return True

    @staticmethod
    def get_backup(filename, backupDirectory, serial):
        backupDirectory = backupDirectory.replace("~", os.environ['HOME'])
        backups = filter(lambda x: x.startswith(filename), os.listdir(backupDirectory))
        if len(backups) <= 0:
            return None
        if serial >= len(backups):
            return None

        length = len(filename.split('.'))

        def compare_time(filename1, filename2):
            return time.mktime(time.strptime(filename1.split('.')[length], Backup.TIME_FORMAT)) > time.mktime(
                time.strptime(filename2.split('.')[length], Backup.TIME_FORMAT))

        backups.sort(cmp=compare_time)
        if backupDirectory[-1] != '/':
            backupDirectory += '/'

        os.system("mv %s %s" % (backupDirectory + backups[serial], filename + '.backup'))
        return filename + ".backup"

    @staticmethod
    def parse_file_name(filename):
        allPatterns = filename.split('.')
        filename = '.'.join(allPatterns[0:-2])
        return [filename, allPatterns[-2]]

    @staticmethod
    def list(backupDirectory):
        backupDirectory = backupDirectory.replace("~", os.environ['HOME'])
        files = os.listdir(backupDirectory)
        files.remove(".DS_Store")

        resDict = {}
        for each in files:
            filename, backupTime = Backup.parse_file_name(each)
            if not filename in resDict.keys():
                resDict[filename] = []
            resDict[filename].append(backupTime)

        def compare_time(timestr1, timestr2):
            return time.mktime(time.strptime(timestr1, Backup.TIME_FORMAT)) > time.mktime(time.strptime(timestr2, Backup.TIME_FORMAT))

        # print the result
        for each in resDict.keys():
            print each
            # first sort the backup by the time
            resDict[each].sort(cmp=compare_time)
            for eachTime in resDict[each]:
                print "    %s" % eachTime

# constants
HELP_MESSAGE = "usage : backup filename password\n" \
               "        retrieve filename password [number]\n" \
               "        delete filename\n" \
               "        list"

BACKUP_DIR = "~/.BACKUP"
ENCRYPTED_METHOD = "aes-256-cfb"

if __name__ == "__main__":
    args = sys.argv
    try:
        if args[1] == "backup":
            filename = args[2]
            password = args[3]
            res = Backup.backup(filename, BACKUP_DIR)
            if res is not None:
                # encrypt the file
                Backup.encrypt(ENCRYPTED_METHOD, password, res, res+".tmp")
                os.remove(res)
                os.rename(res+".tmp", res)
                print "Successfully backup file [%s] to [%s]" % (filename, res)
            else:
                print "Backup failed, please check your parameters."

        elif args[1] == "retrieve":
            filename = args[2]
            password = args[3]
            number = int(args[4]) if len(args)==5 else 0
            res = Backup.get_backup(filename, BACKUP_DIR, number)
            if res is None:
                print "Get backup failed, make sure you have made the backup."
            else:
                # decrypt the file
                Backup.decrypt(ENCRYPTED_METHOD, password, res, res+".tmp")
                os.remove(res)
                os.rename(res+'.tmp', res)
                print "The backup file is stored in [%s]" % res

        elif args[1] == "list":
            Backup.list(BACKUP_DIR)
        elif args[1] == "delete":
            filename = args[2]
            Backup.delete_oldest_backup(filename, BACKUP_DIR)
        else:
            print HELP_MESSAGE

    except Exception, e:
        print "Exception : "
        print e
        print HELP_MESSAGE