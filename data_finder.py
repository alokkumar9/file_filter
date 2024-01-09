# Import necessary modules
import spacy
import spacy_transformers
import pandas as pd
pd.set_option('display.max_colwidth', None)

import re

# nlp = spacy.load('en_core_web_lg')
nlp = spacy.load('en_core_web_trf')


def unwanted_data_removal(data_panda):
  data_panda=data_panda[~data_panda['text'].str.contains("EBC Publishing|Page 1|Printed For|SCC Online|Disclaimer:",case=False)]
  data_panda.reset_index(inplace=True)
  data_panda=data_panda[['page','path','text']]
  return data_panda

def particular_ner_type_find(variable_, ner_type):
  doc=nlp(variable_)
  data_trf=pd.DataFrame(columns=["text","label"])
  for ent in doc.ents:
    # print(ent.text, ent.start_char, ent.end_char, ent.label_)
    new_row = pd.DataFrame({"text": [ent.text], "label": [ent.label_]})
    data_trf=pd.concat([data_trf,new_row], ignore_index=True)

  if(data_trf['label'].str.contains(ner_type, case=False).any()):
    only_particular_ner_data=data_trf[data_trf['label'].str.contains(ner_type, case=False)]
    only_particular_ner_data.reset_index(inplace=True)
    return only_particular_ner_data
  else:
    return None

def is_with_ner(variable_, ner_type):
  doc=nlp(variable_)
  data_trf=pd.DataFrame(columns=["text","label"])
  for ent in doc.ents:
    # print(ent.text, ent.start_char, ent.end_char, ent.label_)
    new_row = pd.DataFrame({"text": [ent.text], "label": [ent.label_]})
    data_trf=pd.concat([data_trf,new_row], ignore_index=True)
  data_trf[data_trf['label'].str.contains(ner_type, case=False)]

  if(data_trf['label'].str.contains(ner_type, case=False).any()):
    return True
  else:
    return False

#Finds all NER and Returns a dataframe
def find_all_ner(variable_):
  doc =nlp(variable_)
  data_trf=pd.DataFrame(columns=["text","label"])
  for ent in doc.ents:
    # print(ent.text, ent.start_char, ent.end_char, ent.label_)
    new_row = pd.DataFrame({"text": [ent.text], "label": [ent.label_]})
    data_trf=pd.concat([data_trf,new_row], ignore_index=True)
  return data_trf


def find_judges(data_panda):
  try:
    # Your code here
    first_page=data_panda[data_panda['page']==0]
    maybe_judges_data=first_page[first_page['text'].str.contains("\(before|\( before",case=False)]
    maybe_judges_data.reset_index(inplace=True)
    if maybe_judges_data is None:
      print('judges name not found')
      return None
    for i in range(len(maybe_judges_data)):
      if (is_with_ner(maybe_judges_data.loc[i,'text'],'PERSON') and maybe_judges_data.loc[i,'page']==0):
        # judges=maybe_judges_data.loc[i,'text'].replace('(','').replace(')','').replace('BEFORE','')
        judges = maybe_judges_data.loc[i,'text']
        judges = re.sub(r'\(|\)|BEFORE', '', judges, flags=re.IGNORECASE)
        return judges
        break
      else:
        return None
        break
  except Exception as e:
    print("Error in finding judges", e)
    
def find_versus_match_type(text):
  try:
    text=text.strip()
    pattern1 = r"(.+)\s+(vs\.|v\.|versus)\s+(.+)"
    pattern2 = r"(.+)\s+(vs\.|v\.|versus)"
    pattern3 = r"(vs\.|v\.|versus)\s+(.+)"
    pattern4 = r"vs\.|v\.|versus"

    match1 = re.search(pattern1, text, flags=re.IGNORECASE)
    match2 = re.search(pattern2, text, flags=re.IGNORECASE)
    match3 = re.search(pattern3, text, flags=re.IGNORECASE)
    match4 = re.search(pattern4, text, flags=re.IGNORECASE)

    if match1:
      return 1, match1.group(0)
    if match2:
      return 2, match2.group(0)
    if match3:
      return 3, match3.group(0)
    if match4:
      return 4, match4.group(0)
    else:
      print("No matchtypefound")
  except Exception as e:
    print("Error in finding versus match type:  ", e)
    

def back_lookup_case_name(data,current_id):
  try:
    i=current_id-1
    pattern = r"\(Before|\( Before"
    while True:
      text=data.loc[i,'text']
      match = re.search(pattern, text, flags=re.IGNORECASE)
      if match:
        break
      i=i-1
    return i+1
  except Exception as e:
    print("Error in backlookup case name:  ", e)
    
def forward_lookup_case_name(data, current_id):
  try:
    i=current_id+1
    pattern = r"Appeal No.|Appeals No.|Appeals No|IA No."
    while True:
      text=data.loc[i,'text']
      match = re.search(pattern, text, flags=re.IGNORECASE)
      if match:
        break
      i=i+1
    return i-1
  except Exception as e:
    print("Error in forwardlookup case name:  ", e)
    
def find_case_name_text(data_panda):
  try:
    first_page=data_panda[data_panda['page']==0]
    judges_name_at=first_page[first_page['text'].str.contains("\(Before|\( Before",case=False)].index[0]
    first_page=first_page[judges_name_at:]
    first_page.reset_index(inplace=True)
    current_id=first_page[first_page['text'].str.contains("versus|vs\.|v\.",case=False) & ~first_page['text'].str.contains("\( Before|\(Before",case=False)].index[0]
    back_till_id= back_lookup_case_name(first_page,current_id)
    forward_till_id= forward_lookup_case_name(first_page,current_id)
    j=back_till_id
    text=""
    while j<=forward_till_id:
      text=text+first_page.loc[j,'text']
      j=j+1
    return text
  except Exception as e:
    print("Error in finding case name:  ", e)
    
    
def find_decided_on_date(data_panda):
  try:
    # Your code here
    first_page=data_panda[data_panda['page']==0]
    first_page.reset_index(inplace=True)
    #checking that case_number mentioned
    if first_page['text'].str.contains("Decided on",case=False).any():
      decided_on_at_id=first_page[first_page['text'].str.contains("Decided on",case=False)].index[0]
      decided_on_text=first_page.loc[decided_on_at_id,"text"]

      only_date_data= particular_ner_type_find(decided_on_text,"DATE")

      pattern=r"^[a-zA-Z]"
      # date_pattern1="\\b\\w+\\s\\d{1,2},\\s\\d{4}\\b"
      # # date_pattern2="\\b\\w+\\s\\d{1,2}\\s\\d{4}\\b"
      # # date_pattern3="\\d{1,2}/\\d{1,2}/\\d{2,4}"
      # date_pattern4="\\d{1,2}-\\d{1,2}-\\d{2,4}"
      # date_pattern5="\\d{4}-\\d{2}-\\d{2}"
      # date_pattern6="\\d{1,2}\\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\\s+\\d{4}"
      # date_pattern7="\\d{1,2}\\s+(January|February|March|April|May|June|July|August|September|October|November|December)\\s+\\d{4}"
      # complete_pattern=date_pattern1+"|"+"|"+"|"+date_pattern4+"|"+date_pattern5+"|"+date_pattern6+"|"+date_pattern7
      for i in range(len(only_date_data)):
        text=only_date_data.loc[i,"text"]
        match=re.search(pattern,text,flags=re.IGNORECASE)
        if match:
            return "Decided on "+text
            break

      # required_date_at_id=only_date_data[only_date_data['text'].str.extract(date_pattern1)].index[0]
      # return only_date_data.loc[required_date_at_id,"text"]
    else:
      return None

  except Exception as e:
    print("Error in finding date: ", e)
    
    
def find_case_number_top(data_panda):
  try:
    # Your code here
    first_page=data_panda[data_panda['page']==0]
    first_page.reset_index(inplace=True)
    #checking that top case_number mentioned
    match_found=False
    pattern = r"SC \d+"
    for i in range(len(first_page)):
      text=first_page.loc[i,"text"]
      match = re.search(pattern, text, flags=re.IGNORECASE)
      if match:
        match_group=match.group(0)
        print("Match found:", match_group)
        match_found=True
        return first_page.loc[i,'text']
        break
    if not match_found:
      return None
      print("case number not mentioned explicitly")

  except Exception as e:
    print("Error in finding case number", e)
    
def find_case_number(data_panda):
  try:
    # Your code here
    first_page=data_panda[data_panda['page']==0]
    first_page.reset_index(inplace=True)
    #checking that case_number mentioned
    if first_page['text'].str.contains("Appeals No\.|Appeal No\.|Appeals Nos\.|Appeal No\.|Special Leave|SLP|IA No.|CA No.",case=False).any():
      case_number_id=first_page[first_page['text'].str.contains("Appeals No\.|Appeal No\.|IA No.",case=False)].index[0]
      case_number=first_page.loc[case_number_id,'text']
      return case_number
    else:
      print("case number not mentioned explicitly")

  except Exception as e:
    print("Error in finding case number", e)