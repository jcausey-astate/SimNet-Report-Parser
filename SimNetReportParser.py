# SimNetExamReportParser.py
#
# Jason L Causey  2009   jason.causey@cs.astate.edu
#
# Parses a SimNet exam report (.csv) file and produces a corresponding
# .csv file with one line per student, such that all exams and attempts for
# each exam are listed (grouped) on the student's row.
#
# Usage:
#  SimNetExamReportParser.py [inputfile | [-h | --help]] [outputfile] [padvalue]
#             Read the .csv file [inputfile], print output to the .csv
#             file [outputfile], using [padvalue] as a filler value for
#             any missing exam fields.
#             If [inputfile] or [outputfile] is missing, you will get
#             a dialog window.  [padvalue] defaults to empty.
#
#             -h or --help for first argument prints this usage message.
################################################################################


import sys
import csv
import os.path

from Tkinter import *
import tkMessageBox
from tkColorChooser import askcolor
from tkFileDialog   import askopenfilename, asksaveasfilename

# getInputFile will show a "File Open" dialog, returning the filename
# of the .csv file.
def getInputFile(prompt):
   print 'Please use the "Open" dialog to choose the input file.'
   print "NOTE:  The dialog may appear behind this terminal window."
   print
   mask = [('CSV Files', '.csv')]
   prompt = "Choose SimNet " + prompt
   filename = askopenfilename(title=prompt, filetypes=mask)
   return filename

# getOutputFile will show a "File Save" dialog, returning the filename
# of the .csv file.
def getOutputFile():
   print 'Please use the "Save As" dialog to choose the output file.'
   print "NOTE:  The dialog may appear behind this terminal window."
   print
   mask = [('CSV Files', '.csv')]
   filename = asksaveasfilename(title="Save Output File As", filetypes=mask)
   return filename

# Makes a good (easily sorted) key from a string by making it all lower-case,
# removing whitespace, and removing periods.
def cleanKey(key):
   key = key.lower().lstrip().replace(' ', '').replace('.','')
   return key

# Usage output:
def usage():
   print "\n"
   print "usage: SimNetExamReportParser.py [inputfile | [-h | --help]] [outputfile] [padvalue]"
   print "            Read the .csv file [inputfile], print output to the .csv"
   print "            file [outputfile], using [padvalue] as a filler value for"
   print "            any missing exam fields."
   print "            If [inputfile] or [outputfile] is missing, you will get"
   print "            a dialog window.  [padvalue] defaults to empty.\n"
   print "            -h or --help for first argument prints this usage message."
   print
   print
   return

def readLessonFile(file):
   lessonInfo = {}
   # If we got a filename (with a .csv extension), process it.
   if(file != '' and file.rfind('.csv') != -1):
      csvfile = open(file, "rU")
      ourDialect = csv.Sniffer().sniff(csvfile.read(2048))
      csvfile.seek(0)

      reader   = csv.reader(csvfile, dialect=ourDialect)
      lineNo   = 0   # Count lines
      records  = {}  # Full record for each item
      titles   = {}  # The titles themselves, keyed by a cleaned version.
      names    = {}  # To get a sorted list of names for output
      percent  = {}  # Stores percent by title and student ID.

      # We need to watch for each new lesson name and also find the largest
      # number of attempts for each.  This info will be used in creating the
      # output table later.
      for line in reader:
         # Ignore header line and put lines in a dict:
         # Lines are of the form:
         #StudentID,LastName,FirstName,Title,Minutes,Date,Date,NumberComplete,TotalTasks,PercentComplete
         #    0    ,   1    ,   2     ,  3  ,  4    , 5  , 6  ,      7       ,     8    ,     9
         if lineNo > 0:
            # Add this line to the proper student's record (by ID).
            if(not str(line[0]) in records.keys()):
               records[str(line[0])] = []
            records[str(line[0])].append(line)
            # Add this lesson title to the lesson's record:
            # Lessons only have one attempt...
            key = cleanKey(str(line[3]))
            if(not str(key) in titles.keys()):
               titles[key] = {}
            titles[key]['title'] = str(line[3])
            if(not str(line[0]) in percent.keys()):
               percent[str(line[0])] = {}
            percent[str(line[0])][key] = line[9]  # Store percent by ID and title.
            # Add this student's name to the names list as a key.  Value is
            # the ID number (used for alphabetical reverse-mapping).
            if(not str(line[1])+str(line[2]) in names.keys()):
               key = str(line[1])+str(line[2])
               #clean up the name to make a good alphabetize-able key:
               key = cleanKey(key)
               names[key] = str(line[0])
         else:
            # The first line is headers.
            headers = line
         lineNo = lineNo + 1

      csvfile.close()  # We're done with this file.
      lessonInfo['records']  = records
      lessonInfo['titles']   = titles
      lessonInfo['percent']  = percent
      lessonInfo['names']    = names
   return lessonInfo

def readExamFile(file):
   examInfo = {}
   # If we got a filename (with a .csv extension), process it.
   if(file != '' and file.rfind('.csv') != -1):
      csvfile = open(file, "rU")
      ourDialect = csv.Sniffer().sniff(csvfile.read(2048))
      csvfile.seek(0)

      reader   = csv.reader(csvfile, dialect=ourDialect)
      lineNo   = 0   # Count lines
      records  = {}  # Full record for each item
      attempts = {}  # To keep track of highest value of attempts per title
      titles   = {}  # The titles themselves, keyed by a cleaned version.
      names    = {}  # To get a sorted list of names for output

      # We need to watch for each new exam name and also find the largest
      # number of attempts for each.  This info will be used in creating the
      # output table later.
      for line in reader:
         # Ignore header line and put lines in a dict:
         # Lines are of the form:
         #StudentID,LastName,FirstName,Title,Attempt,Minutes,Date,ExamStarted,ExamSpan(d.hh:mm:ss),ExamEnded,NumberCorrect,TotalQuestions,PercentCorrect,NumberPoints,TotalPoints,PercentPoints,Status
         #    0    ,  1     ,    2    ,  3  ,  4    ,   5   ,  6 ,     7     ,         8          ,    9    ,      10     ,      11      ,     12       ,     13     ,    14     ,     15      ,  16
         
         # For now we ignore the "status"... it seems better to give students the
         # points they've "partially" earned instead of a zero...
         if lineNo > 0:
            # Add this line to the proper student's record (by ID).
            if(not str(line[0]) in records.keys()):
               records[str(line[0])] = []
            records[str(line[0])].append(line)
            # Add this exam title to the exam's record:
            if(not str(cleanKey(line[3])) in titles.keys()):
               key = cleanKey(str(line[3]))
               attempts[key] = 1
               titles[key] = str(line[3])
            # If we see a new highest attempt number, that is the new max
            # value stored at attempts[examname].
            if(int(line[4]) > int(attempts[cleanKey(str(line[3]))])):
               attempts[cleanKey(str(line[3]))] = int(line[4])
            # Add this student's name to the names list as a key.  Value is
            # the ID number (used for alphabetical reverse-mapping).
            if(not str(line[1])+str(line[2]) in names.keys()):
               key = str(line[1])+str(line[2])
               #clean up the name to make a good alphabetize-able key:
               key = cleanKey(key)
               names[key] = str(line[0])
         else:
            # The first line is headers.
            headers = line
         lineNo = lineNo + 1

      csvfile.close()  # We're done with this file.
      examInfo['records']  = records
      examInfo['attempts'] = attempts
      examInfo['titles']   = titles
      examInfo['names']    = names
   return examInfo

def readProjectFile(file):
   projectInfo = {}
   # If we got a filename (with a .csv extension), process it.
   if(file != '' and file.rfind('.csv') != -1):
      csvfile = open(file, "rU")
      ourDialect = csv.Sniffer().sniff(csvfile.read(2048))
      csvfile.seek(0)

      reader   = csv.reader(csvfile, dialect=ourDialect)
      lineNo   = 0   # Count lines
      records  = {}  # Full record for each item
      attempts = {}  # To keep track of highest value of attempts per title
      titles   = {}  # The titles themselves, keyed by a cleaned version.
      names    = {}  # To get a sorted list of names for output
      percent  = {}  # Stores percent by title and student ID.
         
      # We need to watch for each new lesson name and also find the largest
      # number of attempts for each.  This info will be used in creating the
      # output table later.
      for line in reader:
         # Ignore header line and put lines in a dict:
         # Lines are of the form:
         #StudentID,LastName,FirstName,Title,Attempt,Minutes,Date,Points,TotalPoints,Percent,Status
         #    0    ,  1     ,    2    ,  3  , 4     ,   5   , 6  ,  7   ,     8     ,   9   ,  10
         if lineNo > 0:
            # Add this line to the proper student's record (by ID).
            if(not str(line[0]) in records.keys()):
               records[str(line[0])] = []
            records[str(line[0])].append(line)
            # Add this project title to the project's record:
            if(not str(cleanKey(line[3])) in titles.keys()):
               key           = cleanKey(str(line[3]))
               attempts[key] = 1
               titles[key]   = str(line[3])
            # If we see a new highest attempt number, that is the new max
            # value stored at attempts[projectname].
            if(int(line[4]) > int(attempts[cleanKey(str(line[3]))])):
               attempts[cleanKey(str(line[3]))] = int(line[4])
            if(not str(line[0]) in percent.keys()):
               percent[str(line[0])] = {}
            percent[str(line[0])][key] = line[9]  # Store percent by ID and title.
            # Add this student's name to the names list as a key.  Value is
            # the ID number (used for alphabetical reverse-mapping).
            if(not str(line[1])+str(line[2]) in names.keys()):
               key = str(line[1])+str(line[2])
               #clean up the name to make a good alphabetize-able key:
               key = cleanKey(key)
               names[key] = str(line[0])
         else:
            # The first line is headers.
            headers = line
         lineNo = lineNo + 1

      csvfile.close()  # We're done with this file.
      projectInfo['records']  = records
      projectInfo['titles']   = titles
      projectInfo['attempts'] = attempts
      projectInfo['percent']  = percent
      projectInfo['names']    = names
   return projectInfo

def writeCombinedFile(file, lessonInfo, examInfo, projectInfo, takeHighestExam, selectPointsOrCorrect, takeHighestProject, missingScoreMark = ""):
   # PRE-PROCESS:  Sort the student names list and exam names list:
      #First make sure we have the 'names' key in both examInfo and lessonInfo and projectInfo;
      if(not 'names' in lessonInfo.keys()):
         lessonInfo['names']  = {}
      if(not 'names' in examInfo.keys()):
         examInfo['names']    = {}
      if(not 'names' in projectInfo.keys()):
         projectInfo['names'] = {}
      #Now do the same for 'titles'
      if(not 'titles' in lessonInfo.keys()):
         lessonInfo['titles'] = {}
      if(not 'titles' in examInfo.keys()):
         examInfo['titles'] = {}
      if(not 'titles' in projectInfo.keys()):
         projectInfo['titles'] = {}
      # Merge names from exams and lessons into a single list of names:
      d = {}
      for k in examInfo['names'].keys(), lessonInfo['names'].keys(), projectInfo['names'].keys():
         for x in k:
            d[x] = 1
      sortedNames = d.keys()
      del d
      sortedNames.sort()
      sortedExamTitles    = examInfo['titles'].keys()
      sortedExamTitles.sort()
      sortedLessonTitles  = lessonInfo['titles'].keys()
      sortedLessonTitles.sort()
      sortedProjectTitles = projectInfo['titles'].keys()
      sortedProjectTitles.sort()

      # BEGIN OUTPUT PHASE:
      # Get the output file going and do output.
      if(file != ''):
         # Ensure a .csv extension.
         if(file.rfind('.csv') == -1):
            file = file + '.csv'

         # Open the output file:
         csvfile = csv.writer(open(file, 'w'), quoting=csv.QUOTE_ALL)

         # Input data order (exams)
         #StudentID,LastName,FirstName,Title,Attempt,Minutes,Date,ExamStarted,ExamSpan(d.hh:mm:ss),ExamEnded,NumberCorrect,TotalQuestions,PercentCorrect,NumberPoints,TotalPoints,PercentPoints,Status
         #    0    ,  1     ,    2    ,  3  ,  4    ,   5   ,  6 ,     7     ,         8          ,    9    ,      10     ,      11      ,     12       ,     13     ,    14     ,     15      ,  16
         # Data for lessons is all in lesson structure:
         # titles, names, percent
         # percent is stored by [ID][titleKey]
         useExamPctColumn = 12  # Use "percent correct" by default (instructor can edit this one)
         if(selectPointsOrCorrect == True):
            useExamPctColumn = 15  # Use "percent points" instead (instructor CANNOT edit this field)
         # Output to a new CSV file such that each student (by ID) has a single
         # row.  Each row has:
         # StudentID,LastName,FirstName,Lesson1....LessonN,Exam1attempt1...attamptN,...ExamNAttempt1...attemptN

         # The first line will be headers.  Build them.  The headers will
         # Depend on the lessons, exams, and number of attempts for each exam.
         outputHeaders    = []
         outputHeaders.append("Student ID")
         outputHeaders.append("Last Name")
         outputHeaders.append("First Name")

         # Lessons first
         for key in sortedLessonTitles:
            outputHeaders.append(str(lessonInfo['titles'][key]['title']))
         # Then projects
         for key in sortedProjectTitles:
            nAttempts = projectInfo['attempts'][key]
            currentAttempt = 0
            if(nAttempts > 1 and not takeHighestProject):
               while(currentAttempt < nAttempts):
                  outputHeaders.append(str(projectInfo['titles'][key]) + str(" [Attempt ") \
                                     + str(currentAttempt + 1) + "]")
                  currentAttempt += 1
            else:
               outputHeaders.append(str(projectInfo['titles'][key]))
         # Then exams
         for key in sortedExamTitles:
            nAttempts = examInfo['attempts'][key]
            currentAttempt = 0
            if(nAttempts > 1 and not takeHighestExam):
               while(currentAttempt < nAttempts):
                  outputHeaders.append(str(examInfo['titles'][key]) + str(" [Attempt ") \
                                     + str(currentAttempt + 1) + "]")
                  currentAttempt += 1
            else:
               outputHeaders.append(str(examInfo['titles'][key]))

         csvfile.writerow(outputHeaders)

         # For each student (in sorted order), create exactly 1 row:
         for name in sortedNames:
            outputrow = []
            SID       = ''
            # Each row has:
            # StudentID,LastName,FirstName,Lesson1...LessonN,Project1attempt1..attemptN...ProjectNattempt1,...attemptN,Exam1attempt1...attamptN,...ExamNAttempt1...attemptN
            if(len(examInfo) > 0 and name in examInfo['names'].keys()):
               outputrow.append(examInfo['records'][examInfo['names'][name]][0][0])
               outputrow.append(examInfo['records'][examInfo['names'][name]][0][1])
               outputrow.append(examInfo['records'][examInfo['names'][name]][0][2])
               SID = examInfo['records'][examInfo['names'][name]][0][0]
            elif(len(projectInfo) > 0 and name in projectInfo['names'].keys()):
               outputrow.append(projectInfo['records'][projectInfo['names'][name]][0][0])
               outputrow.append(projectInfo['records'][projectInfo['names'][name]][0][1])
               outputrow.append(projectInfo['records'][projectInfo['names'][name]][0][2])
               SID = projectInfo['records'][projectInfo['names'][name]][0][0]
            elif(len(lessonInfo) > 0):
               outputrow.append(lessonInfo['records'][lessonInfo['names'][name]][0][0])
               outputrow.append(lessonInfo['records'][lessonInfo['names'][name]][0][1])
               outputrow.append(lessonInfo['records'][lessonInfo['names'][name]][0][2])
               SID = lessonInfo['records'][lessonInfo['names'][name]][0][0]

            # For each lesson, output its percent points:
            for key in sortedLessonTitles:
               if(SID in lessonInfo['percent'].keys() and key in lessonInfo['percent'][SID].keys()):
                  outputrow.append(lessonInfo['percent'][SID][key])
               else:
                  outputrow.append(missingScoreMark)
            #StudentID,LastName,FirstName,Title,Attempt,Minutes,Date,Points,TotalPoints,Percent,Status
            #    0    ,  1     ,    2    ,  3  , 4     ,   5   , 6  ,  7   ,     8     ,   9   ,  10
            # Get the list of Percent Points in order for this Project title:
            if(len(projectInfo['titles']) > 0):
               ppts = {}
               for key in sortedProjectTitles:
                  ppts[key] = {}

               if(name in projectInfo['names'].keys()):
                  for record in projectInfo['records'][projectInfo['names'][name]]:
                     key = cleanKey(record[3])
                     attempt = record[4]
                     ppts[key][attempt] = record[9]

               # Now output the PercentPoints field for each project title:
               for key in sortedProjectTitles:
                  nAttempts = projectInfo['attempts'][key]
                  currentAttempt = 1
                  if(not takeHighestProject):
                     while(currentAttempt <= nAttempts):
                        if(str(currentAttempt) in ppts[key].keys()):
                           outputrow.append(ppts[key][str(currentAttempt)])
                        else:
                           outputrow.append(missingScoreMark)
                        currentAttempt += 1
                  else:
                     highest = -9999999999
                     currentAttempt = 1
                     if(str(currentAttempt) in ppts[key].keys()):
                        highest = ppts[key][str(currentAttempt)]
                     while(currentAttempt <= nAttempts):
                        if(str(currentAttempt) in ppts[key].keys()):
                           if(float(ppts[key][str(currentAttempt)]) > float(highest)):
                              highest = ppts[key][str(currentAttempt)]
                        currentAttempt += 1
                     if(highest > -9999999999):
                        outputrow.append(highest)
                     else:
                        outputrow.append(missingScoreMark)
            
            #StudentID,LastName,FirstName,Title,Attempt,Minutes,Date,ExamStarted,ExamSpan(d.hh:mm:ss),ExamEnded,NumberCorrect,TotalQuestions,PercentCorrect,NumberPoints,TotalPoints,PercentPoints,Status
            #    0    ,  1     ,    2    ,  3  ,  4    ,   5   ,  6 ,     7     ,         8          ,    9    ,      10     ,      11      ,     12       ,     13     ,    14     ,     15      ,  16
            # Get the list of Percent Points in order for this exam title:
            if(len(examInfo['titles']) > 0):
               ppts = {}
               for key in sortedExamTitles:
                  ppts[key] = {}

               if(name in examInfo['names'].keys()):
                  for record in examInfo['records'][examInfo['names'][name]]:
                     key = cleanKey(record[3])
                     attempt = record[4]
                     ppts[key][attempt] = record[useExamPctColumn]

               # Now output the PercentPoints field for each exam title:
               for key in sortedExamTitles:
                  nAttempts = examInfo['attempts'][key]
                  currentAttempt = 1
                  if(not takeHighestExam):
                     while(currentAttempt <= nAttempts):
                        if(str(currentAttempt) in ppts[key].keys()):
                           outputrow.append(ppts[key][str(currentAttempt)])
                        else:
                           outputrow.append(missingScoreMark)
                        currentAttempt += 1
                  else:
                     highest = -9999999999
                     currentAttempt = 1
                     if(str(currentAttempt) in ppts[key].keys()):
                        highest = ppts[key][str(currentAttempt)]
                     while(currentAttempt <= nAttempts):
                        if(str(currentAttempt) in ppts[key].keys()):
                           if(float(ppts[key][str(currentAttempt)]) > float(highest)):
                              highest = ppts[key][str(currentAttempt)]
                        currentAttempt += 1
                     if(highest > -9999999999):
                        outputrow.append(highest)
                     else:
                        outputrow.append(missingScoreMark)

            csvfile.writerow(outputrow)

         return True
      # If the user doesn't choose an output file, we can't continue.
      else:
         return False

class SNRParser(Frame):
   def __init__(self, master=None):
      self.lessonFileName  = ""
      self.examFileName    = ""
      self.projectFileName = ""
      Frame.__init__(self, master)
      self.grid()
      self.createWidgets()

   def reInit(self):
      self.lessonFileName  = ""
      self.examFileName    = ""
      self.projectFileName = ""
      self.examNameBox.delete(0,END)
      self.lessonNameBox.delete(0,END)
      self.goButton.configure(state=DISABLED)

   def createWidgets(self):
      instText = "Choose Exam, Lesson, and/or Project reports below\n"
      instText += "then, click \"Generate!\" to create the output\n"
      instText += "workbook.\n"

      self.lessonFileName  = ""
      self.examFileName    = ""
      self.projectFileName = ""

      self.instructions = Label(self, text=instText, justify=LEFT)
      self.instructions.grid(columnspan=3, row=0)

      self.examNameLabel = Label(self, text="Exam Report:")
      self.examNameLabel.grid(column=0,row=1,sticky=W)
      self.examNameBox = Entry(self)
      self.examNameBox.grid(column=1,row=1)
      self.getExamNameButton = Button(self, text="Browse", command=self.getExamName)
      self.getExamNameButton.grid(column=2, row=1)

      self.examTakeHighestAttempt = IntVar()
      self.examTakeHighestAttemptCheckbox = Checkbutton(self, text="Keep only the best exam attempt.", variable=self.examTakeHighestAttempt)
      self.examTakeHighestAttemptCheckbox.grid(column=0,row=2,sticky=W,padx=25, columnspan=3)

      self.usePctPoints = BooleanVar()
      self.examUsePctPointsCheckbox = Checkbutton(self, text="Use % Points column not % Correct (DANGER).", variable=self.usePctPoints, command=self.warnPctPoints)
      self.examUsePctPointsCheckbox.grid(column=0,row=3,sticky=W,padx=25, columnspan=3)

      self.lessonNameLabel = Label(self, text="Lesson Report:")
      self.lessonNameLabel.grid(column=0,row=4,sticky=W)
      self.lessonNameBox = Entry(self)
      self.lessonNameBox.grid(column=1,row=4)
      self.getLessonNameButton = Button(self, text="Browse", command=self.getLessonName)
      self.getLessonNameButton.grid(column=2,row=4)

      self.projectNameLabel = Label(self, text="Project Report:")
      self.projectNameLabel.grid(column=0,row=5,sticky=W)
      self.projectNameBox = Entry(self)
      self.projectNameBox.grid(column=1,row=5)
      self.getProjectNameButton = Button(self, text="Browse", command=self.getProjectName)
      self.getProjectNameButton.grid(column=2, row=5)

      self.projectTakeHighestAttempt = IntVar()
      self.projectTakeHighestAttemptCheckbox = Checkbutton(self, text="Keep only the best project attempt.", variable=self.projectTakeHighestAttempt)
      self.projectTakeHighestAttemptCheckbox.grid(column=0,row=6,sticky=W,padx=25, columnspan=3)

      self.missingScoreValueBox = Entry(self, width=10)
      self.missingScoreValueBox.grid(column=2,row=7, sticky=W)
      self.missingScoreLabel = Label(self, text="Insert this value for missing scores:")
      self.missingScoreLabel.grid(column=0,row=7,sticky=W, columnspan=2)

      self.goButton = Button ( self, text="Generate!",command=self.generate, state=DISABLED)
      self.goButton.grid(columnspan=3, row=8, rowspan=2, sticky=S, pady=15)

   def warnPctPoints(self):
      if(self.usePctPoints.get() == True):
         tkMessageBox.showinfo("Percent Points Warning", "Due to a SimNet bug, using the \"Percent Points\" column may cause manually entered scores not to appear in the final report.")

   def getExamName(self):
      self.examFileName = getInputFile("Exam Report")
      if(self.examFileName != ''):
         self.goButton.configure(state=NORMAL)
         self.examNameBox.insert(0,os.path.basename(self.examFileName))
      else:
         self.examNameBox.delete(0,END)
      self.examNameBox.update()

   def getLessonName(self):
      self.lessonFileName = getInputFile("Lesson Report")
      if(self.lessonFileName != ''):
         self.goButton.configure(state=NORMAL)
         self.lessonNameBox.insert(0, os.path.basename(self.lessonFileName))
      else:
         self.lessonNameBox.delete(0, END)
      self.lessonNameBox.update()

   def getProjectName(self):
      self.projectFileName = getInputFile("Project Report")
      if(self.projectFileName != ''):
         self.goButton.configure(state=NORMAL)
         self.projectNameBox.insert(0, os.path.basename(self.projectFileName))
      else:
         self.projectNameBox.delete(0, END)
      self.projectNameBox.update()

   def generate(self):
      lessonInfo     = readLessonFile(self.lessonFileName)
      examInfo       = readExamFile(self.examFileName)
      projectInfo    = readProjectFile(self.projectFileName)
      outputFileName = getOutputFile()
      if(writeCombinedFile(outputFileName, lessonInfo, examInfo, projectInfo, self.examTakeHighestAttempt.get(), self.usePctPoints.get(), self.projectTakeHighestAttempt.get(), self.missingScoreValueBox.get())):
         self.msg = Message(self,text="Finished.  Output file generated OK.")
         #self.msg.grid()
      else:
         self.msg = Message(self,text="No output file specified.  Cannot continue.")
         #self.msg.grid()
      if(not tkMessageBox.askyesno("Finished", "Would you like to convert another file set?")):
         self.destroy()
         exit(0)
      else:
         self.reInit()




# Main execution:
if __name__ == "__main__":

   app = SNRParser()
   app.master.title("SimNet Report Parser")
   app.mainloop()
