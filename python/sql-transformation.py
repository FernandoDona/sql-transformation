import argparse
from ast import If
from io import TextIOWrapper
from pathlib import Path

argParser = argparse.ArgumentParser(description='Converts a unformatted query resulted in pain text to a SQL command (INSERT/UPDATE).')

argParser.add_argument('type', help='Command type to be returned like INSERT or UPDATE.')
argParser.add_argument('table', help='The target table name.')
argParser.add_argument('path', help='The path of the file that contains the text to be converted.')

args = argParser.parse_args()
path = Path(args.path)

if path.is_file() == False:
    print(f'The file {args.path} doesnt exist!')
    exit()

if args.path.endswith('.csv') == False and args.path.endswith('.txt') == False:
    print(f'The file is in a invalid format. Accept only .csv or .txt')
    exit()

if args.type.upper() != 'UPDATE' and args.type.upper() != 'INSERT':
    print('The command type is invalid.')
    exit()

def format_field(field: str, isColumn: bool = False) -> str:
    field = field.replace('\n', '')
    field = field.strip()
    
    if isColumn:
        return field

    if field.upper() == 'NULL':
        return field
    
    chars = ':-,;'
    countAlpha = 0
    for char in field:
        if char.isalpha() or char in chars:
            countAlpha += 1
        if countAlpha >= 2 or (len(field) == 1 and char.isalpha()):
            return f'\'{field}\''
        if ('.' in chars) == False:
            chars = '.' + chars
    
    return field

def format_line_to_insert(line: str, separator: str, isHeader: bool, tableName: str) -> str:
    splittedValues = line.split(separator)
    if isHeader:
        return f'INSERT INTO {tableName} \n\t(' + ', '.join(format_field(value, True) for value in splittedValues) + ') \nVALUES \n'

    return '\t(' + ', '.join(format_field(value) for value in splittedValues) + '), \n'

def format_to_insert(filePath: str, tableName: str) -> str:
    separator = ';' if filePath.endswith('.csv') else '\t'
    formattedCommand = ''
    with open(filePath) as f:
        header = f.readline()
        formattedCommand += format_line_to_insert(header, separator, True, tableName)
        for line in f:
            formattedCommand += format_line_to_insert(line, separator, False, tableName)

    return formattedCommand

# def format_to_update(filePath: str, tableName: str) -> str:
#     separator = ';' if filePath.endswith('.csv') else '\t'
#     formattedCommand = f'UPDATE {tableName} \nSET \n'
#     with open(filePath) as f:
#         columns = f.readline().split(separator)
#         for line in f:
#             values = line.split(separator)
#             for i, column in enumerate(columns):
#                 formattedCommand += f'\t{format_field(column, True)} = {format_field(values[i])},\n'

#     return formattedCommand

if args.type.upper() == 'INSERT':
    print(format_to_insert(args.path, args.table))

# print(format_to_update(args.path, args.table))