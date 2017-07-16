import loader_from_file
import property
import zipfile
import config
import re
import os


def send_file(words):
    company = " ".join(words[1:])
    stock = loader_from_file.load_one_stock(company)
    if stock.files_name.__len__ == 0:
        return config.RSP_FILES_NOT_FOUND, list()
    else:
        list_file = list()
        for file in stock.files_name:
            path_to_file = property.TYPE2_PATH + '/' + stock.trade_code + property.ARCHIVES + '/' + file
            for unzip_file in unzip(path_to_file):
                valid, ext = validate_file_name(unzip_file)
                if valid:
                    new_file_name = property.TMP_EXTRACT + '/' + 'File' + str(list_file.__len__() + 1) + '.' + ext
                    os.rename(unzip_file, new_file_name)
                    list_file.append(new_file_name)
                else:
                    list_file.append(unzip_file)

        return format(config.RSP_FILES % stock.files_name.__len__()), list_file


def validate_file_name(filename):
    pattern = r"[a-zA-Z0-9-_а-яА-Я]"
    pure_name = filename.replace(property.TMP_EXTRACT + '/', '')
    point = str(pure_name).index('.')
    name = pure_name[:point]
    ext = pure_name[point + 1:]
    findall = re.findall(pattern, name)
    return findall.__len__() < name.replace(' ', '').__len__(), ext


def unzip(path_to_file):
    extracted = list()
    zip = zipfile.ZipFile(path_to_file, 'r')
    for f in zip.filelist:
        zip.extract(f.filename, property.TMP_EXTRACT)
        path_extract = property.TMP_EXTRACT + '/' + f.filename
        extracted.append(str(path_extract))
    zip.close()
    return extracted
