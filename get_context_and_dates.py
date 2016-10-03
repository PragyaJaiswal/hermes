#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import json
import re

from dateparser import parse
from practnlptools.tools import Annotator

text = ["Hi Carlos, can you give me the company website within 2 days?",
        "Hi Carlos, can you give me the company website in a day?",
        "Hey could you provide me with the documentation in a day?",
        "Give documents after 13th.",
        "I need the logo by tomorrow.",
        "Not really, we could modify the android application in various ways.",
        "Do it by 26-10-2016.",
        "Do it by 25 10 2016.",
        "Need the application by 8th November 2016.",
        "I would like to meet you tomorrow and give you the documents. However, the website could be provided by the 13th.",
        "Please give me the web application by Thursday",
        "Please give me the web application by next Thursday",
        "Please give me the application in the next 2 days",
        "Hey Pragya, due to some commitments, I need the work in the next 2 days."
        "I want the work in the first week of next month."
        ]

pattern = "(0?[1-9]|[12][0-9]|3[01])[-/. ](0?[1-9]|1[012])[-/. ]\d{4}"

annotator = Annotator()

class SRL(object):
  def __init__(self):
    pass

  def extract(self):
    dictionary = {}
    for ind, sentence in enumerate(text):
      srl = annotator.getAnnotations(sentence.lower())['srl']
      if len(srl) > 1:
        srl = [srl[-1]]
      dictionary[ind] = srl
    print(dictionary)

    self.process(dictionary)

  def process(self, dictionary):
    tasks = {}
    for each in dictionary:
      tasks[each] = {}
      each_srl = dictionary[each][0]
      for key in each_srl:
        if key == 'V' or key == 'A1' or 'TMP' in key or 'AM-ADV' in key or re.search(pattern, each_srl[key]):
          tasks[each][key] = each_srl[key]
      try:
        tasks[each]['final'] = '{0} {1}'.format(each_srl['V'], each_srl['A1'])
      except KeyError:
        raise
      tasks[each]['current_date'] = str(parse('today'))
    tasks_with_date = to_datetime_obj().convert(tasks)
    jsonify(tasks_with_date, 'tasks_with_temporal_using_srl.json', 'srl')


class to_datetime_obj(object):
  def __init__(self):
    pass

  def convert(self, tasks):
    tasks_with_date = tasks
    for sentence in tasks.keys():
      tasks_with_date[sentence]['final'] = tasks[sentence]['final']
      tasks_with_date[sentence]['current_date'] = tasks[sentence]['current_date']
      for each_tag in tasks[sentence].keys():
        if 'TMP' in each_tag or bool(re.search(pattern, tasks[sentence][each_tag])):
          tasks_with_date[sentence]['datetime'] = str(parse(tasks[sentence][each_tag])) if bool(parse(tasks[sentence][each_tag])) else tasks[sentence][each_tag]
          # Workaround for 'next'
          try:
            if bool(parse(tasks[sentence][each_tag])) and parse(tasks[sentence][each_tag]) < parse('now'):
              if not 'next' in tasks[sentence][each_tag]:
                tasks_with_date[sentence]['datetime'] = self.add_days(parse(tasks[sentence][each_tag]), 7)
              elif 'next' in tasks[sentence][each_tag]:
                tasks_with_date[sentence]['datetime'] = self.add_days(parse(tasks[sentence][each_tag]), 14)
          except Exception, e:
            raise
        else:
          pass
    return tasks_with_date

  def add_days(self, datetime, num_of_days):
    day = datetime.day + num_of_days
    if datetime.month in [1, 3, 5, 7, 8, 10, 12]:
      if day > 31:
        # Next month would have 30 days
        day = day - 30 + 1
        month = datetime.month + 1
    else:
      if day > 30:
        day = day - 31 + 1
        month = datetime.month + 1
    if month > 12:
      month = month - 12 + 1
      year = datetime.year + 1
    else:
      year = datetime.year
    return str(parse('{0}-{1}-{2}'.format(day, month, year)))


def jsonify(dictionary, filename, text='None'):
  a = json.dumps(dictionary, sort_keys=True, indent=2, separators=(',', ': '))
  with open(str(filename), 'w') as outfile:
    if text == 'None':
      outfile.write(a)
    else:
      outfile.write(text + ' = ')
      outfile.write(a)

if __name__ == '__main__':
  SRL().extract()