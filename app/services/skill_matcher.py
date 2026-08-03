import re

SKILLS_DB = {

    # Programming Languages
    "python", "java", "c", "c++", "c#", "go", "golang",
    "rust", "swift", "kotlin", "scala", "r", "matlab",
    "perl", "php", "ruby", "dart", "typescript",
    "javascript", "objective-c", "bash", "shell scripting",

    # Web Development
    "html", "html5", "css", "css3", "bootstrap",
    "tailwind css", "jquery", "ajax", "react", "reactjs",
    "nextjs", "vue", "vuejs", "angular", "angularjs",
    "nodejs", "express", "expressjs", "flask", "django",
    "fastapi", "spring", "spring boot", "asp.net",
    "rest api", "graphql", "soap", "json", "xml",

    # Mobile Development
    "flutter", "react native", "android", "android studio",
    "ios", "xcode", "kotlin", "swift",

    # Databases
    "sql", "mysql", "postgresql", "sqlite", "oracle",
    "mongodb", "redis", "firebase", "mariadb",
    "nosql", "cassandra", "neo4j", "dynamodb",

    # Cloud
    "aws", "amazon web services", "azure",
    "google cloud", "gcp", "cloud computing",
    "heroku", "vercel", "netlify",

    # DevOps
    "git", "github", "gitlab", "bitbucket",
    "docker", "kubernetes", "jenkins",
    "terraform", "ansible", "ci/cd",
    "linux", "ubuntu", "unix",

    # AI / Machine Learning
    "machine learning", "deep learning",
    "artificial intelligence", "ai",
    "nlp", "natural language processing",
    "computer vision", "opencv",
    "tensorflow", "keras", "pytorch",
    "scikit-learn", "xgboost",
    "lightgbm", "huggingface",
    "transformers", "langchain",
    "llm", "generative ai",
    "prompt engineering",

    # Data Science
    "data science", "data mining",
    "data analysis", "data visualization",
    "statistics", "pandas", "numpy",
    "matplotlib", "seaborn",
    "plotly", "scipy", "jupyter",
    "excel", "power bi", "tableau",
    "etl", "data warehouse",

    # Cybersecurity
    "cybersecurity", "penetration testing",
    "ethical hacking", "network security",
    "cryptography", "wireshark",
    "metasploit", "nmap",
    "owasp", "firewall",

    # Networking
    "tcp/ip", "dns", "dhcp",
    "routing", "switching",
    "ccna", "vpn",

    # Operating Systems
    "windows", "linux", "macos",

    # Software Engineering
    "oop", "object oriented programming",
    "design patterns",
    "software architecture",
    "microservices",
    "multithreading",
    "concurrency",

    # Testing
    "unit testing",
    "integration testing",
    "selenium",
    "pytest",
    "junit",
    "postman",
    "automation testing",

    # Version Control
    "git", "github",
    "gitlab",

    # UI/UX
    "figma",
    "adobe xd",
    "photoshop",
    "illustrator",
    "canva",
    "ui design",
    "ux design",
    "wireframing",
    "prototyping",

    # Office Tools
    "ms office",
    "microsoft office",
    "word",
    "excel",
    "powerpoint",
    "outlook",
    "google docs",
    "google sheets",

    # Business
    "business analysis",
    "project management",
    "agile",
    "scrum",
    "kanban",
    "jira",
    "confluence",

    # Finance
    "accounting",
    "financial analysis",
    "bookkeeping",
    "quickbooks",
    "sap",
    "erp",

    # Marketing
    "digital marketing",
    "seo",
    "sem",
    "content writing",
    "copywriting",
    "social media marketing",
    "email marketing",
    "google analytics",

    # Design
    "graphic design",
    "video editing",
    "photography",
    "adobe premiere pro",
    "after effects",
    "blender",
    "autocad",
    "solidworks",

    # Soft Skills
    "communication",
    "leadership",
    "teamwork",
    "problem solving",
    "critical thinking",
    "analytical thinking",
    "decision making",
    "time management",
    "adaptability",
    "creativity",
    "presentation",
    "negotiation",
    "collaboration",
    "customer service",
    "public speaking",
    "mentoring",
    "conflict resolution",
    "attention to detail",
    "organizational skills",
    "multitasking",

    # Research
    "research",
    "technical writing",
    "documentation",

    # Languages
    "english",
    "hindi",
    "nepali",
    "french",
    "german",
    "spanish",
    "chinese",
    "japanese",

    # Miscellaneous
    "api",
    "oauth",
    "jwt",
    "socket programming",
    "web scraping",
    "beautifulsoup",
    "selenium",
    "streamlit",
    "opencv",
    "pymupdf",
    "regex",
    "rapidfuzz",
    "computer networks",
    "operating systems",
    "database management system",
    "dbms",
    "compiler design",
    "data structures",
    "algorithms",
    "object oriented design",
    "software development",
    "full stack development",
    "backend development",
    "frontend development"
    # Big Data
"apache spark", "spark", "hadoop", "hive", "pig",
"kafka", "airflow", "databricks", "hdfs", "sqoop",
"flume", "presto",

# Data Engineering
"data engineering", "etl", "elt", "apache beam",
"snowflake", "redshift", "bigquery", "azure synapse",
"data pipeline", "data modeling",

# Embedded Systems & IoT
"arduino", "raspberry pi", "embedded c",
"microcontrollers", "esp32", "esp8266",
"iot", "mqtt", "embedded systems",

# Robotics
"robotics", "ros", "gazebo",
"path planning", "slam", "robot operating system",

# Blockchain
"blockchain", "ethereum", "solidity",
"smart contracts", "web3", "hyperledger",
"cryptocurrency",

# Game Development
"unity", "unreal engine", "godot",
"game development", "opengl",
"directx", "shader programming",

# CAD / Engineering
"autocad", "solidworks", "catia",
"ansys", "fusion 360", "revit",
"civil 3d",

# Electrical Engineering
"pcb design", "proteus", "multisim",
"ltspice", "circuit design",
"electronics", "vlsi",

# Mechanical Engineering
"cad", "cam", "cnc",
"manufacturing", "thermodynamics",
"solid mechanics",

# Civil Engineering
"structural analysis", "surveying",
"construction management",
"quantity surveying",

# Healthcare
"medical coding", "ehr",
"patient care", "clinical research",
"pharmacology",

# Accounting & Finance
"tally", "quickbooks", "sap fico",
"financial reporting", "taxation",
"auditing", "budgeting",
"forecasting", "payroll",

# Human Resources
"recruitment", "talent acquisition",
"employee engagement", "onboarding",
"performance management",
"hr analytics",

# Sales
"sales", "lead generation",
"crm", "salesforce",
"business development",
"cold calling",
"customer relationship management",

# Customer Support
"customer support", "technical support",
"help desk", "ticketing",
"zendesk", "freshdesk",

# Digital Marketing
"google ads", "facebook ads",
"instagram marketing",
"linkedin marketing",
"content marketing",
"affiliate marketing",
"wordpress",

# Graphic Design
"adobe photoshop",
"adobe illustrator",
"indesign",
"coreldraw",
"figma",
"sketch",
"branding",

# Video Production
"video editing",
"davinci resolve",
"adobe premiere pro",
"after effects",
"cinematography",
"motion graphics",

# Cloud & Infrastructure
"vmware",
"virtualization",
"openstack",
"load balancing",
"nginx",
"apache server",

# Security
"identity management",
"iam",
"siem",
"soc",
"incident response",
"digital forensics",
"malware analysis",

# QA / Testing
"manual testing",
"black box testing",
"white box testing",
"performance testing",
"load testing",
"jmeter",
"cypress",
"playwright",

# ERP / CRM
"sap",
"sap hana",
"oracle erp",
"salesforce",
"dynamics 365",

# Office Productivity
"google workspace",
"microsoft teams",
"slack",
"zoom",
"trello",
"notion",
"asana",

# Research
"literature review",
"academic writing",
"scientific research",
"survey design",
"statistical analysis",

# Mathematics
"linear algebra",
"calculus",
"probability",
"optimization",
"numerical methods",

# Soft Skills
"self learning",
"fast learner",
"initiative",
"emotional intelligence",
"active listening",
"decision making",
"strategic planning",
"coaching",
"relationship building",
"cross-functional collaboration",

# Languages
"urdu",
"arabic",
"korean",
"tamil",
"telugu",
"bengali",
"marathi",
"punjabi",

# Office Administration
"data entry",
"record keeping",
"office administration",
"scheduling",
"calendar management",
"travel planning",

# Hospitality
"hotel management",
"food safety",
"restaurant management",
"housekeeping",
"event management",

# Education
"teaching",
"lesson planning",
"curriculum development",
"classroom management",
"online tutoring",

# Legal
"legal research",
"contract drafting",
"compliance",
"litigation support",

# Supply Chain
"logistics",
"inventory management",
"warehouse management",
"procurement",
"supply chain management",

# Manufacturing
"lean manufacturing",
"six sigma",
"quality assurance",
"quality control",
"production planning",

# Networking
"ccnp",
"network troubleshooting",
"lan",
"wan",
"wireless networking",
"cisco packet tracer",

# Computer Fundamentals
"computer architecture",
"computer organization",
"operating system",
"dbms",
"software engineering",
"compiler design",
"theory of computation",
"discrete mathematics",
"object oriented programming",
"data structures",
"algorithms"

"drawing",
"sketching",
"painting",
"watercolor painting",
"oil painting",
"acrylic painting",
"digital painting",
"portrait drawing",
"landscape painting",
"illustration",
"concept art",
"character design",
"comic art",
"manga drawing",
"anime illustration",
"cartooning",
"storyboarding",
"calligraphy",
"hand lettering",
"typography",
"graphic design",
"logo design",
"branding",
"visual design",
"print design",
"poster design",
"brochure design",
"packaging design",
"book cover design",
"layout design",
"color theory",
"composition",
"visual storytelling",
"creative thinking",
"art direction",
"sculpting",
"ceramics",
"pottery",
"wood carving",
"crafting",
"paper crafting",
"origami",
"jewelry design",
"fashion illustration",
"fashion design",
"textile design",
"embroidery",
"knitting",
"crochet",
"sewing",
"interior design",
"3d modeling",
"3d sculpting",
"animation",
"2d animation",
"3d animation",
"motion graphics",
"video editing",
"photography",
"photo editing",
"retouching",
"videography",
"film editing",
"cinematography",
"music production",
"audio editing",
"voice acting",
"singing",
"songwriting",
"music composition",
"piano",
"guitar",
"violin",
"drums",
"dance",
"choreography",
"acting",
"theatre",
"public performance",
"creative writing",
"poetry writing",
"script writing",
"story writing",
"adobe photoshop",
"adobe illustrator",
"adobe indesign",
"adobe premiere pro",
"after effects",
"lightroom",
"coreldraw",
"figma",
"canva",
"procreate",
"clip studio paint",
"blender",
"maya",
"zbrush",
"autodesk sketchbook",
"krita",
"gimp",
"inkscape",
"davinci resolve",
"final cut pro"
"final cut pro",
"languages",
"hindi",
"nepali",
"urdu",
"arabic",
"french",
"german",
"spanish",
"portuguese",
"italian",
"dutch",
"russian",
"ukrainian",
"polish",
"turkish",
"greek",
"swedish",
"norwegian",
"danish",
"finnish",
"icelandic",
"irish",
"welsh",
"scottish gaelic",
"czech",
"slovak",
"hungarian",
"romanian",
"bulgarian",
"serbian",
"croatian",
"bosnian",
"slovenian",
"albanian",
"macedonian",
"lithuanian",
"latvian",
"estonian",
"belarusian",
"chinese",
"mandarin",
"cantonese",
"japanese",
"korean",
"thai",
"vietnamese",
"indonesian",
"malay",
"filipino",
"tagalog",
"burmese",
"khmer",
"lao",
"mongolian",
"tibetan",
"sinhala",
"tamil",
"telugu",
"kannada",
"malayalam",
"marathi",
"gujarati",
"punjabi",
"bengali",
"assamese",
"odia",
"sanskrit",
"kashmiri",
"dogri",
"maithili",
"bhojpuri",
"konkani",
"sindhi",
"persian",
"farsi",
"pashto",
"hebrew",
"swahili",
"amharic",
"yoruba",
"igbo",
"hausa",
"zulu",
"xhosa",
"afrikaans",
"somali",
"latin",
"esperanto"
}


def extract_skills(text):
    text = text.lower()

    found_skills = []

    for skill in SKILLS_DB:
        if re.search(rf"\b{re.escape(skill)}\b", text):
            found_skills.append(skill)

    return sorted(list(set(found_skills)))
