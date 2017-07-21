import datetime
import os
import re
import zipfile

import py7zlib
import rarfile

import config
import loader_from_file
import my_log
import property

LOG = my_log.get_logger("sender_file")


def send_file(words):
    num = words[1]
    if re.compile(r'[0-9]').match(num):
        company = " ".join(words[2:])
    else:
        company = " ".join(words[1:])

    stock = loader_from_file.load_one_stock(company)
    if stock.files_name.__len__ == 0:
        return config.RSP_FILES_NOT_FOUND, list()
    else:
        list_file = list()
        for count, file in enumerate(stock.files_name):
            path_to_file = property.TYPE2_PATH + '/' + stock.trade_code + property.ARCHIVES + '/' + file
            if num and num != '' and int(num) == count:
                break
            for extracted in extractr_archive(path_to_file):
                not_valid, ext = validate_file_name(extracted)
                if not_valid:
                    if ext != '':
                        new_file_name = property.TMP_EXTRACT + '/' + stock.trade_code + '_File' + \
                                        str(datetime.datetime.now()) + '.' + ext
                        os.rename(extracted, new_file_name)
                        list_file.append(new_file_name)
                else:
                    list_file.append(extracted)

        if list_file.__len__() > 0:
            return format(config.RSP_FILES % list_file.__len__()), list_file
        else:
            return config.RSP_FILES_NOT_FOUND, list_file


def validate_file_name(filename):
    pattern = r"[a-zA-Z0-9-_а-яА-Я]"
    pure_name = filename.replace(property.TMP_EXTRACT + '/', '')
    try:
        point = str(pure_name).index('.')
    except ValueError:
        return True, ''
    name = pure_name[:point]
    ext = pure_name[point + 1:]
    findall = re.findall(pattern, name)
    return findall.__len__() < name.replace(' ', '').__len__(), ext


def extractr_archive(path_to_file):
    extracted = list()
    ext = re.findall(property.ZIP, path_to_file)
    if ext.__len__() > 0:
        zip = zipfile.ZipFile(path_to_file, 'r')
        for f in zip.filelist:
            zip.extract(f.filename, property.TMP_EXTRACT)
            path_extract = property.TMP_EXTRACT + '/' + f.filename
            extracted.append(str(path_extract))
        zip.close()
    ext = re.findall(property.RAR, path_to_file)
    if ext.__len__() > 0:
        try:
            rar = rarfile.RarFile(path_to_file)
            for f in rar.namelist():
                rar.extract(f, property.TMP_EXTRACT)
                path_extract = property.TMP_EXTRACT + '/' + f
                extracted.append(str(path_extract))
            rar.close()
        except rarfile.BadRarFile:
            LOG.error("Bad RarFile... path: %s" % path_to_file)

    ext = re.findall(property.SEVEN_Z, path_to_file)
    if ext.__len__() > 0:
        file = open(path_to_file, 'rb')
        seven_zip = py7zlib.Archive7z(file)
        for name in seven_zip.getnames():
            path_extract = os.path.join(property.TMP_EXTRACT, name)
            outdir = os.path.dirname(path_extract)
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            outfile = open(path_extract, 'wb')
            outfile.write(seven_zip.getmember(name).read())
            outfile.close()
            extracted.append(str(path_extract))
        file.close()
    return extracted
