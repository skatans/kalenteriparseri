# -*- coding: utf-8 -*-
import time
import re
from datetime import date
from datetime import timedelta
import pprint
import copy
import io

{   'VCALENDAR': {   'CALSCALE': 'GREGORIAN',
                     'METHOD': 'PUBLISH',
                     'PRODID': '-//Google Inc//Google Calendar 70.9054//EN',
                     'VERSION': '2.0',
                     'VEVENT': [{   ' 7100000009B68E76AA7B59C4A813A749E2C309110': '',
                                       'CLASS': 'PUBLIC',
                                       'CREATED': '20180824T092123Z',
                                       'DESCRIPTION': '',
                                       'DTEND': '20180827T070000Z',
                                       'DTSTAMP': '20190414T180958Z',
                                       'DTSTART': '20180827T060000Z',
                                       'LAST-MODIFIED': '20180824T092123Z',
                                       'LOCATION': 'xxii',
                                       'SEQUENCE': '0',
                                       'STATUS': 'CONFIRMED',
                                       'SUMMARY': 'TKP2 Tutoriaali',
                                       'TRANSP': 'OPAQUE',
                                       'UID': '040000008200E00074C5B7101A82E00800000000ADAD725886753D4BA90B2A7B4586577',
                                       'VALARM': {   'ACTION': 'DISPLAY',
                                                     'DESCRIPTION': 'This is '
                                                                    'an event '
                                                                    'reminder',
                                                     'TRIGGER': '-P0DT0H15M0S'},
                                       'X-MICROSOFT-CDO-ALLDAYEVENT': 'FALSE',
                                       'X-MICROSOFT-DISALLOW-COUNTER': 'FALSE'},
                                   ],
                     'VTIMEZONE': {   'DAYLIGHT': {   'DTSTART': '19700326T235959',
                                                      'RRULE': 'FREQ=YEARLY;BYMONTH=3;BYDAY=-1TH',
                                                      'TZNAME': 'EEST',
                                                      'TZOFFSETFROM': '+0200',
                                                      'TZOFFSETTO': '+0300'},
                                      'STANDARD': {   'DTSTART': '19701030T010000',
                                                      'RRULE': 'FREQ=YEARLY;BYMONTH=10;BYDAY=-1FR',
                                                      'TZNAME': 'EET',
                                                      'TZOFFSETFROM': '+0300',
                                                      'TZOFFSETTO': '+0200'},
                                      'TZID': 'Asia/Amman',
                                      'X-LIC-LOCATION': 'Asia/Amman'},
                     'X-WR-CALNAME': '',
                     'X-WR-TIMEZONE': 'Europe/Helsinki'}}

START = "DTSTART"
END = "DTEND"
FILENAME = "basic (4).ics"

def getDay(datestr):
    if type(datestr) is type(date.today()):
        return datestr
    if "T" in datestr:
        datestr = datestr[:datestr.find("T")]
    t = time.strptime(datestr,'%Y%m%d')
    return date(t.tm_year,t.tm_mon, t.tm_mday)

def getDayName(wday):
    weekdays = {
    0:"Maanantai",
    1:"Tiistai",
    2:"Keskiviikko",
    3:"Torstai",
    4:"Perjantai",
    5:"Lauantai",
    6:"Sunnuntai",
    }
    return weekdays[wday];

def parse(file):
    result = {}
    for line in file:
        data = line.replace("\n","").split(":")
        data = (data[0],"".join(data[1:]))
        if line.startswith("END"):
            break
        if line.startswith("BEGIN"):
            event = parse(file)
            if data[1]=="VEVENT":
                result.setdefault("VEVENT", []).append(event)
            else:
                result[data[1]] = event
        else:        
            result[data[0].split(";")[0]] = data[1]
    return result
	
def expandRepeatingEvent(event):
    if 'RRULE' not in event:
        return [event]
    newEvents = []
    rule = {x.split("=")[0]: x.split("=")[1] for x in event['RRULE'].split(";")}
    repeatInterval = timedelta(days=7)
    if( rule['FREQ']=="DAILY"):
        repeatInterval = timedelta(days=1)
        
    if('COUNT' in rule):
        for i in range(int(rule['COUNT'])):
            copied = copy.deepcopy(event)
            copied[START] = getDay(copied[START])+repeatInterval*(i+1)
            newEvents.append(copied)
    if('UNTIL' in rule):
        currDate = getDay(event[START])
        while( getDay(rule['UNTIL']) >= currDate):
            copied = copy.deepcopy(event)
            copied[START] = currDate
            currDate = currDate+repeatInterval
            newEvents.append(copied)
    return newEvents

def getEvents(calendar):
    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(calendar)
    events = calendar['VCALENDAR']['VEVENT']
    expandedEvents = []
    [expandedEvents.extend(expandRepeatingEvent(event)) for event in events]

    rangeInput = int(input("int montako viikkoa: "))
    dayRange = 52
    if rangeInput < dayRange:
        dayRange = rangeInput
    nextWeek = date.today()+timedelta(weeks=dayRange)
    events = [event for event in expandedEvents if getDay(event[START]) < nextWeek and getDay(event[START]) > date.today()]
    events.sort(key=lambda a: getDay(a[START]))
    return events
    
def outputCalendar(events):

    def formatDate(d):
        dayStr = re.sub("\.0",".", day.strftime("%d.%m."))
        dayStr = re.sub("^0","", dayStr)
        return ("\n<b>" + getDayName(day.weekday())+" "+dayStr + "</b>")
    
    def formatTime(t):
        timeStr = t[9:11]
        if len(timeStr) != 0:
            timeInt = int(timeStr) + 3
            timeStr = str(timeInt)
            if len(timeStr) == 1:
                timeStr = "0" + timeStr
        return timeStr

    if len(events)==0:
        print ("Ei tapahtumia")
        return
    
    day = getDay(events[0][START])
    print(formatDate(day))
    for event in events:
        if day != getDay(event[START]):
            day = getDay(event[START])
            dayStr = re.sub("\.0",".", day.strftime("%d.%m."))
            dayStr = re.sub("^0","", dayStr)
            print("\n"+formatDate(getDay(event[START])))
        eventOutput = "- " + event["SUMMARY"]
        if ('RRULE' not in event) and len(event[START]) > 10:
            eventOutput += " klo " + formatTime(event[START]) + "-" + formatTime(event[END])
            
        if len(event["LOCATION"]) != 0:
            eventOutput += " @" + (event["LOCATION"].split("\\"))[0]
        print (eventOutput)
        
with io.open(FILENAME, "r", encoding='utf-8') as f:
    calendar = parse(f)

events = getEvents(calendar)
outputCalendar(events)

