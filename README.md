# DCS-Statstics-Processing
A Python script for processing JSON data from DCS World missions

## How to get JSON data from LUA data:
This is the process for how I have done it, though I will see if I can add a way to avoid this step in the future.  

1. Ensure you have a lua interpreter, and that you have a lua JSON library, e.g. [lunajson](https://github.com/grafi-tt/lunajson).  
2. Add the following to the bottom of your lua data, then execute the file with your lua interpreter.
```
local json = require('lunajson')  -- You can put a different JSON library here too, just replace .encode() if need be
local data = json.encode(misStats)  
local file = io.open('data.json', 'r')  
io.output(file)  
io.write(data)  
io.close(file)
```
This will output the JSON to *'data.json'*

## How to use once you have the JSON:
Use Python3 to execute *'parse_stats.py'*, along with the file name of the JSON data. For instance:
`python3 parse_stats.py data.json`
The output will be in *'stats_output.txt'*
