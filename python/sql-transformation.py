import argparse
import os
from io import TextIOWrapper
from pathlib import Path

argParser = argparse.ArgumentParser(description='Converts a unformatted query resulted in pain text to a SQL command (INSERT/UPDATE).')

argParser.add_argument('type', help='Command type to be returned like INSERT or UPDATE.')
argParser.add_argument('table', help='The target table name.')
argParser.add_argument('--path', help='The path of the file that contains the text to be converted. If this parameter is empty then will be read the file in ../in/query-input.txt')
argParser.add_argument('--where', help='The where clause to use in the UPDATE command.')

args = argParser.parse_args()
fileDir = os.path.dirname(os.path.realpath(__file__))
outputPath = os.path.join(fileDir, '../out/sql-command-result.sql')
inputPath = args.path

if args.path is None or args.path == '':
    inputPath = os.path.join(fileDir, '../in/query-input.txt')
if args.where is None:
    args.where = ''

path = Path(inputPath)

if path.is_file() == False:
    print(f'The file {inputPath} doesnt exist!')
    exit()

if inputPath.endswith('.csv') == False and inputPath.endswith('.txt') == False:
    print(f'The file is in a invalid format. Accept only .csv or .txt')
    exit()

if args.type.upper() != 'UPDATE' and args.type.upper() != 'INSERT':
    print('The command type is invalid.')
    exit()

def get_value_separator(filePath: str):
    return ';' if filePath.endswith('.csv') else '\t'

def format_field(field: str, isColumn: bool = False) -> str:
    field = field.replace('\n', '')
    field = field.strip()
    
    if isColumn:
        return field

    if field.upper() == 'NULL':
        return field
    
    if field == '':
        return '\'\''
    
    hasDot = False
    numericChars = 0
    for char in field:
        if char.isnumeric():
            numericChars += 1
            continue
        if char.isalpha() or (char == '.' and hasDot):
            return f'\'{field}\''
        if char == '.' and hasDot == False:
            hasDot = True
            numericChars += 1

    if len(field) != numericChars:
        return f'\'{field}\''

    return field

def format_line_to_insert(line: str, separator: str, isHeader: bool, tableName: str) -> str:
    splittedValues = line.split(separator)
    if isHeader:
        return f'INSERT INTO {tableName} \n\t(' + ', '.join(format_field(value, True) for value in splittedValues) + ') \nVALUES \n'

    return '\t(' + ', '.join(format_field(value) for value in splittedValues) + '), \n'

def format_insert_to_file(filePath: str, outputPath: str, tableName: str):
    separator = get_value_separator(filePath)
    formattedCommand = ''
    with open(filePath) as f_in:
        with open(outputPath, 'w') as f_out:
            header = f_in.readline()
            f_out.write(format_line_to_insert(header, separator, True, tableName))
            for line in f_in:
                f_out.write(format_line_to_insert(line, separator, False, tableName))

def format_to_update(filePath: str, outputPath: str, tableName: str, where: str):
    separator = get_value_separator(filePath)
    with open(outputPath, 'w') as f_out:
        f_out.write(f'UPDATE {tableName} \nSET \n')
        with open(filePath) as f:
            columns = f.readline().split(separator)
            for line in f:
                values = line.split(separator)
                for i, column in enumerate(columns):
                    f_out.write(f'\t{format_field(column, True)} = {format_field(values[i])},\n')
        f_out.write(where)

if args.type.upper() == 'INSERT':
    format_insert_to_file(inputPath, outputPath, args.table)

if args.type.upper() == 'UPDATE':
    format_to_update(inputPath, outputPath, args.table, args.where)