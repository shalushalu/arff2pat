#!/usr/bin/python

def read_file(filename):
  # Open the file. Room for improvement, but for now
  # remember to close it after reading.
  f = open(filename, 'r')
  return f

def write_file(filename, content):
  #Write file with correct headers
  f = open(filename, 'w')
  f.write("SNNS pattern definition file V3.2\n")
  f.write("generated at Mon Apr 25 15:58:23 1994\n")
  f.write("\n")
  f.write("No. of patterns : "+str(len(content['data']))+"\n")
  f.write("No. of input units : "+str(content['no_of_inputs'])+"\n")
  f.write("No. of output units : "+str(content['no_of_outputs'])+"\n")
  f.write("\n")
  for data in content['data']:
    data_string = convert_list_to_string(data)
    f.write(data_string+"\n")
  f.close()

def convert_list_to_string(list_raw):
  #Merge the list and replace the comma with a space
  list_string = ' '.join(map(str, list_raw))    
  return list_string

def parse_attributes(data_string_raw):
  #Clean the raw string for spaces
  data_string = data_string_raw.replace(' ', '')
  #Clean the raw string for newlines
  data_string = data_string.rstrip('\n')

  #The string can either be a real value or a touple
  if data_string.startswith('real'):
    return data_string
  else:
    #Get the values in the string by splitting between {} and split by ,
    s_touple = data_string.split('{', 1)[1].split('}')[0]
    s_array = s_touple.split(',')
    return s_array


def read_attribute_line(line_raw):
  #Split the line by the ' symbol.
  #Example of output
  #['@attribute ', 'age', ' real\n']
  #['@attribute ', 'sex', ' { female, male}\n']
  line_array = line_raw.split("\'",2)
  line_end = line_array[2]
  return parse_attributes(line_end)

def read_data_line(line_raw):
  #Clean the raw string for spaces
  data_string = line_raw.replace(' ', '')
  #Clean the raw string for newlines
  data_string = data_string.rstrip('\n')
  #Split by , and return
  data_array = data_string.split(',')
  return data_array

def substract_information_from_file(file_object):
  #An ordered list of attributes
  list_attributes = []
  #An ordered list of data
  list_data = []

  #Go through each line in the file and substract attributes and data
  for line in file_object:
    #Read attributes
    if line.startswith('@attribute'):
      attribute = read_attribute_line(line)
      list_attributes.append(attribute)

    #Read all data to the end of the file
    if line.startswith('@data'):
      for line_data_raw in file_object:
        data = read_data_line(line_data_raw)
        list_data.append(data)

  file_dict = {'list_attributes' : list_attributes, 'list_data' :list_data}
  return file_dict

def shuffle_list(list_raw):
  import random
  list_shuffled = random.shuffle(list_raw, random.random)
  return list_raw

def split_data(data_list_raw, split_sizes):
  #To get train, test and validation data split it in defined sizes
  #Update, we need to stratisfy the data and will do that with Weka
  train_list = data_list_raw[:split_sizes['train']:]

  test_from = split_sizes['train']
  test_to = split_sizes['train']+split_sizes['test']
  test_list = data_list_raw[test_from:test_to]

  validate_from = test_to
  validate_to = test_to+split_sizes['validate']
  validate_list = data_list_raw[validate_from: validate_to]

  data_split_dict = {'train' : train_list,
                     'test' : test_list, 
                     'validate' : validate_list}
  return data_split_dict

def find_touple_index(value, array):
  #Get the index value in an array
  return array.index(value)

def return_binary_array(true_index, in_array):
  #Translate and convert to binary array
  bin_array = []
  for index, val in enumerate(in_array):
    if index != true_index:
      bin_array.append(0)
    else:
      bin_array.append(1)
  return bin_array

def find_and_return_bin_array(value, in_array):
  #Get a binary value based on a value in an array
  array_index = find_touple_index(value, in_array)
  return return_binary_array(array_index, in_array)


def translate_list_to_binary(data_list_raw, array_list):
  data_list_translated = []
  for data_cur in data_list_raw:
    data_list_cur = []
    bad_line = False
    for i, att in enumerate(array_list):
      val = data_cur[i]

      #make sure the value is not a question mark
      #REMARK this is a decision based on the data
      if val == '?':
        # data_list_cur.append(val)
        # The line is invalid and should be skipped
        bad_line = True

      elif att == 'real':
        #Keep numeric values
        data_list_cur.append(float(val))

      else:
        #Convert attributes of arrays to binary values.
        #REMARK this can be done differently
        val_translated = find_and_return_bin_array(val, att)
        val_trans_clean = convert_list_to_string(val_translated)
        data_list_cur.append(val_trans_clean)
    #If something is wrong with the line, skip it...
    if bad_line:
      continue
    data_list_translated.append(data_list_cur)
  return data_list_translated



file_base_dir = '/home/emil/study/rmit/semester4/data_minig/assignments/ass2/'
file_base_dir_out  = '/home/emil/study/rmit/semester4/data_minig/assignments/ass2/data/out/'
file_name = 'heart-c.arff'
file_location = file_base_dir + file_name
file_raw = read_file(file_location)
file_dict = substract_information_from_file(file_raw)
file_raw.close()

data_list = file_dict['list_data']
attributes_list = file_dict['list_attributes']


#shuffle the data
shuffle_list(data_list)

#Translate the data to binary values
data_list_translated = translate_list_to_binary(data_list, attributes_list)

split_sizes = {'train' : 200, 'test' : 53, 'validate' : 50}
data_split = split_data(data_list_translated, split_sizes)
#As an excample print the test data:
#print data_split['test']

content_dict = {                 
                'no_of_inputs'   : 25,
                'no_of_outputs'  : 5
               }

#### TRAIN FILE ####
content_dict['no_of_patterns'] = split_sizes['train']
content_dict['data'] = data_split['train']
file_name_out = 'heart-c-train.pat'
file_location_out = file_base_dir_out + file_name_out
write_file(file_location_out, content_dict)

##### TEST FILE ####
content_dict['no_of_patterns'] = split_sizes['test']
content_dict['data'] = data_split['test']
file_name_out = 'heart-c-test.pat'
file_location_out = file_base_dir_out + file_name_out
write_file(file_location_out, content_dict)

#### VALIDATE FILE ####
content_dict['no_of_patterns'] = split_sizes['validate']
content_dict['data'] = data_split['validate']
file_name_out = 'heart-c-valid.pat'
file_location_out = file_base_dir_out + file_name_out
write_file(file_location_out, content_dict)
