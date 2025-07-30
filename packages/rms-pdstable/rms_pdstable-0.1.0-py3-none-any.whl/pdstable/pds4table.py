##########################################################################################
# pdstable/pds4table.py
# Store Pds4TableInfo and Pds4ColumnInfo
##########################################################################################
import julian
import numbers
import numpy as np
import os
import re

from collections import defaultdict
from pds4_tools.reader.label_objects import Label

PDS4_LBL_EXTENSIONS = {'.xml', '.lblx'}

def is_pds4_label(label_name):
    """Check if the given label is a PDS4 label."""

    for ext in PDS4_LBL_EXTENSIONS:
        if label_name.endswith(ext):
            return True

PDS4_BUNDLE_COLNAMES = (
    'Bundle Name',
)
# The mapping of a product tag to its corresponding file area tags
# The key is a product component tag, and the value is its corresponding file area tag,
# it could be just one (string) or multiple (tuple) file area tags
PDS4_PRODUCT_TO_FILE_AREA_TAGS_MAPPING = {
    'Product_Ancillary': 'File_Area_Ancillary',
    'Product_Browse': 'File_Area_Browse',
    'Product_Metadata_Supplemental': 'File_Area_Metadata',
    'Product_Observational': ('File_Area_Observational',
                              'File_Area_Observational_Supplemental'),
}

# The mapping of a table tag to its corresponding record and field tags
# The key is a table tag, and the value is a tuple of the record and field tags
PDS4_TABLE_TO_RECORD_FIELD_TAGS_MAPPING = {
    'Table_Binary': ('Record_Binary', 'Field_Binary'),
    'Table_Character': ('Record_Character', 'Field_Character'),
    'Table_Delimited': ('Record_Delimited', 'Field_Delimited'),
    'Table_Delimited_Source_Product_External': ('Record_Delimited', 'Field_Delimited'),
    'Table_Delimited_Source_Product_Internal': ('Record_Delimited', 'Field_Delimited'),
}

# PDS4 label tags under Special_Constants
PDS4_SPECIAL_CONSTANTS_TAGS = {
    'error_constant',
 	'high_instrument_saturation',
 	'high_representation_saturation',
 	'invalid_constant',
 	'low_instrument_saturation',
 	'low_representation_saturation',
 	'missing_constant',
 	'not_applicable_constant',
 	'saturated_constant',
 	'unknown_constant',
 	# 'valid_maximum',
 	# 'valid_minimum'
}

# This is an exhaustive tuple of string-like types
STRING_TYPES = (str, bytes, bytearray, np.str_, np.bytes_)

# Needed because the default value of strip is False
def tai_from_iso(string):
    return julian.tai_from_iso(string, strip=True)

def int_from_base2(string):
    return int(string, 2)

def int_from_base8(string):
    return int(string, 8)

def int_from_base16(string):
    return int(string, 16)

# Delimiter used to separate column values in the same row
# It's encoded by 'UTF-8'
PDS4_FIELD_DELIMITER = {
    'Carriage-Return Line-Feed': b'\r\n',
    'Comma': b',',
    'Horizontal Tab': b'\t',
    'Semicolon': b';',
    'Vertical Bar': b'|'
}

# key: PDS4 data type
# value: a tuple of (self.data_type, self.dtype2, self.scalar_func)
PDS4_CHR_DATA_TYPE_MAPPING = {
    'ASCII_Date_DOY': ('time', 'S', tai_from_iso),
    'ASCII_Date_Time_DOY': ('time', 'S', tai_from_iso),
    'ASCII_Date_Time_DOY_UTC': ('time', 'S', tai_from_iso),
    'ASCII_Date_Time_YMD': ('time', 'S', tai_from_iso),
    'ASCII_Date_Time_YMD_UTC': ('time', 'S', tai_from_iso),
    'ASCII_Date_YMD': ('time', 'S', tai_from_iso),
    'ASCII_Time': ('time', 'S', tai_from_iso),
    'ASCII_Integer': ('int', 'int', int),
    'ASCII_NonNegative_Integer': ('int', 'int', int),
    'ASCII_Real': ('float', 'float', float),
    'ASCII_AnyURI': ('string', 'U', None),
    'ASCII_Directory_Path_Name': ('string', 'U', None),
    'ASCII_DOI': ('string', 'U', None),
    'ASCII_File_Name': ('string', 'U', None),
    'ASCII_File_Specification_Name': ('string', 'U', None),
    'ASCII_LID': ('string', 'U', None),
    'ASCII_LIDVID': ('string', 'U', None),
    'ASCII_LIDVID_LID': ('string', 'U', None),
    'ASCII_MD5_Checksum': ('string', 'U', None),
    'ASCII_String': ('string', 'U', None),
    'ASCII_VID': ('string', 'U', None),
    'UTF8_String': ('string', 'U', None),
    'ASCII_Boolean': ('boolean', 'bool', None),
    'ASCII_Numeric_Base2': ('int', 'int', int_from_base2),
    'ASCII_Numeric_Base8': ('int', 'int', int_from_base8),
    'ASCII_Numeric_Base16': ('int', 'int', int_from_base16),
}

################################################################################
# Class Pds4TableInfo
################################################################################
class Pds4TableInfo(object):
    """The Pds4TableInfo class holds the attributes of a PDS4-labeled table."""

    def __init__(self, label_file_path, invalid={}, valid_ranges={}, table_file=None):
        """Loads a PDS4 table based on its associated label file.

        Input:
            label_file_path path to the PDS4 label file
            invalid         an optional dictionary keyed by column name. The
                            returned value must be a list or set of values that
                            are to be treated as invalid, missing or unknown.
            valid_ranges    an optional dictionary keyed by column name. The
                            returned value must be a tuple or list containing
                            the minimum and maximum numeric values in that
                            column.
            table_file      specify a table file to be read, if the provided table
                            doesn't exist in the label, an error will be raised.
        """

        # Parse PDS4 label, store the label dictionary from the pds4_tools Label object
        lbl = Label.from_file(label_file_path)
        lbl_dict = lbl.to_dict()
        self.label = lbl_dict

        # Get the file area (table file) info from the label dictionary
        file_area = None
        for prod_tag, file_area_tag in PDS4_PRODUCT_TO_FILE_AREA_TAGS_MAPPING.items():
            if prod_tag in lbl_dict.keys():
                prod_component = lbl_dict[prod_tag]
                if isinstance(file_area_tag, str):
                    file_area = prod_component[file_area_tag]
                elif isinstance(file_area_tag, tuple):
                    for tag in file_area_tag:
                        if tag in prod_component.keys():
                            file_area = prod_component[tag]
                            break
            if file_area:
                break

        self.table_file_name = None

        # The label file points to one table file
        if isinstance(file_area, dict):
            try:
                self.table_file_name = file_area['File']['file_name']
                self.table_file_li = [self.table_file_name]
            except:
                raise ValueError('Table file name was not found in PDS4 label')

            if table_file is not None and table_file not in self.table_file_li:
                raise ValueError("The provided table file name doesn't match the one" +
                                 'in the label. The label contains one table file ' +
                                 f'{self.table_file_name}')
        # The label file points to multiple table files
        elif isinstance(file_area, list):
            try:
                table_name_li = [f['File']['file_name'] for f in file_area]
            except:
                raise ValueError('Table file name was not found in PDS4 label')

            if table_file is None or table_file not in table_name_li:
                raise ValueError(f"The table file name '{table_file}' doesn't exist. " +
                                 f'The label contains {len(table_name_li)} table ' +
                                 f'files: {table_name_li}')
            else:
                self.table_file_name = table_file
                self.table_file_li = table_name_li
                # specify the table file that we want to read
                idx = table_name_li.index(table_file)
                file_area = file_area[idx]
        # The label file has no table file info
        else:
            raise ValueError(f'{label_file_path} does not contain any table file info.' )

        try:
            self.header_bytes = int(file_area['Header']['object_length'])
        except KeyError:
            # Some tables don't have header
            self.header_bytes = 0

        # Get the table/record/field info by searching the tags in the file area
        table_area = None
        record_area = None
        columns = None
        for table_tag, rec_field_tags in PDS4_TABLE_TO_RECORD_FIELD_TAGS_MAPPING.items():
            if table_tag in file_area.keys():
                record_tag, field_tag = rec_field_tags
                table_area = file_area[table_tag]
                record_area = table_area[record_tag]
                columns = record_area[field_tag]
                break

        if table_area is None or record_area is None or columns is None:
            raise ValueError(f'Missing the table/record/field info in {label_file_path}')

        self.rows = int(table_area['records'])
        self.columns = int(record_area['fields'])

        try:
            # for the table with fixed row length
            self.row_bytes = int(record_area['record_length'])
            self.fixed_length_row = True
            self.field_delimiter = None
        except:
            # for the case like .csv table, row length is not used
            self.row_bytes = int(record_area['maximum_record_length'])
            self.fixed_length_row = False
            self.field_delimiter = PDS4_FIELD_DELIMITER[table_area['field_delimiter']]

        # Save the key info about each column in a list and a dictionary
        self.column_info_list = []
        self.column_info_dict = {}

        # Construct the dtype0 dictionary
        self.dtype0 = {'crlf': ('|S2', self.row_bytes-2)}

        default_invalid = set(invalid.get('default', []))

        # Check all the column names, append the suffix _{num} to the duplicated names
        colname = defaultdict(list)
        for idx, col in enumerate(columns):
            name = col['name']
            colname[name].append(idx)

        for name, idx_li in colname.items():
            # append _{num} if there are duplicated names
            if len(idx_li) > 1:
                num = 1
                for i in idx_li:
                    columns[i]['name'] += f'_{num}'
                    num += 1

        for col in columns:
            name = col['name']
            field_num = int(col['field_number'])

            pdscol = Pds4ColumnInfo(col, field_num,
                                    invalid = invalid.get(name, default_invalid),
                                    valid_range = valid_ranges.get(name, None))

            self.column_info_list.append(pdscol)
            self.column_info_dict[pdscol.name] = pdscol
            self.dtype0[pdscol.name] = pdscol.dtype0


        self.table_file_path = os.path.join(os.path.dirname(label_file_path),
                                            self.table_file_name)


################################################################################
# class Pds4ColumnInfo
################################################################################

class Pds4ColumnInfo(object):
    """The Pds4ColumnInfo class holds the attributes of one column in a PDS4
    label."""

    def __init__(self, node_dict, column_no, invalid=set(), valid_range=None):
        """Constructor for a Pds4Column.

        Input:
            node_dict   the dictionary associated with the column info obtained
                        from pds4_tools Label object.
            column_no   the index number of this column, starting at zero.
            invalid     an optional set of discrete values that are to be
                        treated as invalid, missing or unknown.
            valid_range an optional tuple or list identifying the lower and
                        upper limits of the valid range for a numeric column.
        """

        self.name = node_dict['name']
        self.colno = column_no

        try:
            self.start_byte = int(node_dict['field_location'])
            self.bytes      = int(node_dict['field_length'])
        except:
            # For .csv table, each column length is not fixed (row is not fixed), so
            # we don't have these info.
            self.start_byte = None
            self.bytes = None

        # Handle the case where one column stores multiple items, like EXPECTED_MAXIMUM
        # in casssini iss cruise
        self.description = node_dict.get('description', '')
        items = 1
        if '-valued' in self.description:
            try:
                items = int(re.match(r'.*(\d)-valued.*', self.description.strip())[1])
            except:
                items = 1

        if self.start_byte is not None and self.bytes is not None:
            self.items = node_dict.get('ITEMS', items)
            item_bytes = int((self.bytes-items+1)/items)

            self.item_bytes = node_dict.get('ITEM_BYTES', item_bytes)
            self.item_offset = node_dict.get('ITEM_OFFSET', item_bytes+1)

            # Define dtype0 to isolate each column in a record
            self.dtype0 = ('S' + str(self.bytes), self.start_byte - 1)

            # Define dtype1 as a list of dtypes needed to isolate each item
            if self.items == 1:
                self.dtype1 = None
            else:
                self.dtype1 = {}
                byte0 = 0
                for i in range(self.items):
                    self.dtype1['item_' + str(i)] = ('S' + str(self.item_bytes),
                                                    byte0)
                    byte0 += self.item_offset
        else:
            self.dtype0 = None
            self.dtype1 = None

        # PDS4 TODO: review the data type conversion
        # Define dtype2 as the intended dtype of the values in the column
        self.data_type = node_dict['data_type']
        # Convert PDS4 data_type
        try:
            (self.data_type,
             self.dtype2,
             self.scalar_func) = PDS4_CHR_DATA_TYPE_MAPPING[self.data_type]
        except:
            raise ValueError('unsupported data type: ' + self.data_type)

        # Handle the case like "START_TIME" with ASCII_String instead of ASCII_Time as
        # the data type
        if self.name.endswith("_TIME") or self.name.endswith("_DATE"):
            self.data_type = "time"
            self.dtype2 = 'S'
            self.scalar_func = tai_from_iso

        # Identify validity criteria
        invalid_set = set()
        if valid_range is not None:
            self.valid_range = valid_range
        else:
            valid_max = None
            valid_min = None
            # Search for 'Special_Constants' tag, if it exists, get the invalid values
            # from tags in PDS4_SPECIAL_CONSTANTS_TAGS and store them in invalid_set
            if 'Special_Constants' in node_dict.keys():
                special_const_area = node_dict['Special_Constants']
                for invalid_tag in PDS4_SPECIAL_CONSTANTS_TAGS:
                    invalid_val = special_const_area.get(invalid_tag, None)
                    if invalid_val:
                        if self.scalar_func:
                            try:
                                invalid_val = self.scalar_func(invalid_val)
                            except:
                                # if the invalid value can't be converted, we will keep
                                # its original value and data type
                                invalid_val = invalid_val

                        invalid_set.add(invalid_val)

                valid_max = special_const_area.get('valid_maximum', None)
                valid_min = special_const_area.get('valid_minimum', None)

                valid_max = self.scalar_func(valid_max) if valid_max else None
                valid_min = self.scalar_func(valid_min) if valid_min else None

            self.valid_range = (valid_min, valid_max) if valid_min or valid_max else None

        if isinstance(invalid, (numbers.Real,) + STRING_TYPES):
            invalid_set |= set([invalid])
        else:
            invalid_set |= invalid

        self.invalid_values = invalid_set
