from pymongo import MongoClient
from langchain.chat_models import AzureChatOpenAI
class chatllm:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.azure_deployment = None
        self.openai_api_version = None
        print("chatllm object created")
    def chat(self,prompt,save=False):
        if save and self.client is None:
            print("No database connection established. Please set the database first to save entires.")
            return None
        else:
            if self.azure_deployment is None:
                print("No LLM setup. Please set the LLM first.")
                return None
            else:
                llm = AzureChatOpenAI(
                    azure_deployment=self.azure_deployment,
                    openai_api_version=self.openai_api_version,
                    azure_endpoint=self.azure_endpoint,
                    api_key=self.api_key,
                    temperature=self.temperature,
                )
                llm_response = llm.invoke(prompt)
                print(llm_response.content)
                if save:
                    self.collection.insert_one({"prompt": prompt, "response": llm_response.content})
                return llm_response.content

    def set_llm(self,azure_deployment,openai_api_version,azure_endpoint,api_key,temperature):
        self.azure_deployment = azure_deployment
        self.openai_api_version = openai_api_version
        self.azure_endpoint = azure_endpoint
        self.api_key = api_key
        self.temperature = temperature
        print("llm setup complete")
    def set_db(self,mongo_url,db_name,collection_name):
        self.client = MongoClient(mongo_url)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        print("Database setup complete")

    def show_entires(self):
        if self.collection is None:
            print("No collection set. Please set the collection first.")
            return None
        all_documents = self.collection.find()
        print("All documents in collection:")
        for document in all_documents:
            print(document)
        # Alternative: convert to list to see all at once
        all_docs_list = list(self.collection.find())
        print(all_docs_list)