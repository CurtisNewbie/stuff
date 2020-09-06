# How to use alias in Windows 10 

Sources: 
- https://stackoverflow.com/questions/20530996/aliases-in-windows-command-prompt
- https://docs.microsoft.com/en-us/windows/console/console-aliases

## 1. FOR CMD

### 1.1 Write script that declares alias at cmd startup

1. create .cmd or .bat script file (e.g., "alias.cmd") 
2. declare alias using following syntax: 

        doskey aliasName=.....
        
        e.g., 
    
        doskey jenkins=java -jar %JENKINS_PATH%
        doskey rabbitmq=%RABBITMQ_PATH%
        doskey nacos=%NACOS_PATH%

### 1.2 Add this script to registry 

Let say that, you want to use "AutoRun" as the variable name for the path of the script, we register the script as follows:

1. **Run** regedit
2. Go to **\HKEY_CURRENT_USER\Software\Microsoft\Command Processor**
3. Add a string named **AutoRun** (it can be anything, it's just a variable name)
4. For this string variable, we specify the path to the script, e.g., `"C:\Users\yongjie.zhuang\...\alias.cmd"`

Then everytime we open cmd, this script is run. Imagine it as adding `alias aliasName="..."` in .bashrc file in linux. 


