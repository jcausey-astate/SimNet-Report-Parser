# SimNet-Report-Parser
Parses Lesson, Exam, and Project reports from SimNet, produces more sane spreadsheet with one row per student and ability to take best score from repeated attempts.

## Data Preparation
To avoid requiring more libraries, I made the parser just use the CSV library -- but this means you have to open the report files from SimNet in Excel (or similar) and then re-save as CSV first, before running the parser.

## Required Packages
You must have `tkinter` installed to run the parser; it might be installed by default depending on your Python install.  If not, see https://tkinter.unpythonic.net/wiki/How_to_install_Tkinter.

## Disclaimer
This software was recently updated; verify that it has calculated things correctly --- don't blindly trust it yet!  Also, SimNet changes the report format occasionally, so that may cause unexpected errors as well.  Use at your own risk.

## License
**The MIT License (MIT)**

Copyright (c) 2009-2016 Jason L Causey, Arkansas State University

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
