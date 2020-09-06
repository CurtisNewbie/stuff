# How to use alias in Windows 10 

Sources: 
- https://stackoverflow.com/questions/20530996/aliases-in-windows-command-prompt
- https://docs.microsoft.com/en-us/windows/console/console-aliases
- https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_aliases
- https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_functions_advanced_parameters
- https://www.tenforums.com/tutorials/54585-change-powershell-script-execution-policy-windows-10-a.html

## 1. FOR CMD

### 1.1 Write script that declares aliases at cmd startup

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

## 2. For PowerShell

In powershell, we can declare aliases, but we must also declares a function to actually execute the commands. I.e., **alias** calls the **function**, and **function** does the job.

### 2.1  Add functions

Use the syntax below:

    Function funcName (){
        do something
    }

    e.g., 

    Function runJenkins { start CMD.exe "java -jar $env:JENKINS_PATH" }
    Function runRabbitmq { start $env:RABBITMQ_PATH}
    Function runNacos { start $env:NACOS_PATH}

### 2.2 Add aliases for functions

Then we declare aliases to call the functions. Note that we cannot run a series of commands directly from a aliase. E.g., `Set-Alias -Name run -Value " java -jar someJar.jar " won't work, we should use a function.

Use the syntax below:

    Set-Alias -Name aliasName -Value "dosomething..."

e.g., 

    Set-Alias -Name jenkins -Value runJenkins 
    Set-Alias -Name rabbitmq -Value runRabbitmq 
    Set-Alias -Name nacos -Value runNacos 

### 2.3 Add alias and functions to profile

Add above functions and aliases to your profile. Your profile is available at $Profile. Simply enter `$Profile`, then powershell will display where the profile file is.

Note that by default, powershell might disallow scripts execution, check such restriction by `Get-ExecutionPolicy` and change your policy by `Set-ExecutionPolicy`.
