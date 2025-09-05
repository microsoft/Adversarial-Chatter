# Adversarial Chatter Projects

1. Clone Repo

```text
https://MM-Dev-Org@dev.azure.com/MM-Dev-Org/DAI-POD/_git/Projects
```

## Table of Contents

- ## Adversarial-Chatter

- ## Psych-Agent

## Adversarial Chatter

**Description:**
Adversarial chatter is a project  that explores adversarial behavior in AI or cybersecurity contexts. FakBlogsAI simulates fake blog data and SocialAgent analyzes blog data from the context of elicitation to better train individuals against social engineering threats.

**Tech Stack:**
Python, Angular, Azure Search, Autogen

**Install and Run:**

- Manual Install

```text
1. Download and install VSCode
2. Download and install Python => 3.10
3. Download and install Python Extensions. 
    a."Python Debugger"
    b. "Python - Language Support"
    c. "Pylance"
4. install requirements file.  "pip install -r ADV_CHAT\requirements.txt"

Note: (Not Required) To get the power of AutoGen, with no-code GUI, install the AutogenStudio
    a.  pip install -U "autogenstudio"

5. Copy SocialAgent.py onto a local directory

6. Download GlitchyWeb Locally
    Note: 
        Make sure that there is no node_modules or package-lock.json, in either the root or server directory.
        If these exists you will need to run the command below in the GlitchyWeb directory from a PowerShell terminal  
        as admin. 

        Remove-Item -Recurse -Force .\node_modules, .\package-lock.json

        Remove-Item -Recurse -Force .\server\node_modules, .\server\package-lock.json

7. cd  to "GlitchyWeb" in terminal
    
    Run: npm install 

8. cd to "GlitchyWeb\server"  in terminal

    Run: npm install 
```

- Manual Run

```text
1. Launch three terminals
2. First terminal, cd \GlitchyWeb
    Run:  npx ng serve
3. Second terminal, cd \GlitchyWeb\server
    Run: node server.js
    Note: Once the server is running, open your browser and navigate to `http://localhost:4200/`.

4. Third Terminal, cd {Directory Containing Social Agent Script}
    Run: python AdversarialChatterAgent.py
5. You can now run prompts in the third terminal, examples included below.
    
    Prompt Examples: 
    
    "if someone where to socially engineer one of these individuals, from the information gleaned 
    what would be an approach, who would that be, what  method would you use and why?"

    "How could {Person Mentioned} defend against the previously identified weaknesses?"

    "Can you create a list of how {Person Mentioned} could defend and train against the previously identified weaknesses?"

```

- Docker Install and Run
docker run --env-file C:\Users\mimares\GITHUB\Adversarial-Chatter\.env -d --name adversarial-chatter-container -p 8080:80 adversarial-chatter

docker exec -it adversarial-chatter-container /bin/bash

## Support

`@DataAI-Consulting-Lab`

## Contributing

```text
    Reach out to the @DataAI-Consulting-Lab if you would like to join our project
```

## Acknowledgements

- `FED-CIV DAI POD`

- `@DataAI-Consulting-Lab`
