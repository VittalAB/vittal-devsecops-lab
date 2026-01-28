from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

load_dotenv()

llm = init_chat_model(
    "azure_openai:gpt-5-2025-08-07",
    api_key="",
    azure_endpoint="",
    api_version="2024-08-01-preview"
)

from langchain_community.utilities import SQLDatabase

db = SQLDatabase.from_uri("sqlite:///manufacture_data.db")

print(f"Dialect : {db.dialect}")
print(f"Tables : {db.get_usable_table_names()}")
print(db.get_table_info())
# print(f"Sample Query : {db.get_sample_query()}")



from langchain_community.agent_toolkits import SQLDatabaseToolkit

toolkit = SQLDatabaseToolkit(db=db, llm=llm)
tools = toolkit.get_tools()

for tool in tools: 
    print(f"Tool name: {tool.name}")
    print(f"Tool description: {tool.description}\n")



from langchain.agents import create_agent

system_prompt = """

you are an agent designed to interact with SQL database.
Given an user query or input , create syntactically correct {dialect} queries to run on the database to fetch the required information, then 
take a look at the results of the query and return the answer. Unless the user specifies a specific number of examples they wish to see, always 
limit query to at most {top_k} results.

you can order the results by relevant columns to get the most pertinent information. Never query for all the columns from a table, only ask for the columns that are relevant to the user's question.

you MUST double check your SQL queries for correctness before executing them. If you find any mistakes, correct them and re-execute.

DO NOT MAKE ANY DML (INSERT/UPDATE/DELETE) QUERIES. ONLY MAKE SELECT QUERIES.

To start you should ALWAYS look at the tables in the database to see what you can query. DO NOT skip this step 

then you should query scehma of the most relevant table although current scenairo is having one table only 

""".format(dialect=db.dialect, top_k=100)


agent = create_agent(
    model=llm, system_prompt=system_prompt, tools=tools)0


question = "hi hello namaskar heng ide maiyge?"

for step in agent.stream(
    {"messages": [{"role": "user", "content": question}]}, stream_mode="values",
):
    print(step["messages"][-1].pretty_print())