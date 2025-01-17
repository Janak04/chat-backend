import csv

from pymilvus import db

from src.config.settings.const import UPLOAD_FILE_PATH
from src.repository.ai_models import ai_model
from src.repository.rag.base import BaseRAGRepository
from src.repository.vector_database import vector_db


class RAGChatModelRepository(BaseRAGRepository):

    async def load_model(self, session_id: int, model_name: str) -> bool:
        # Init model with input model_name
        try:
            ai_model.initialize_model(model_name)
            pass
        except Exception as e:
            print(e)
            return False
        return True

    def get_prompt(self, session_id: int, message: str, context: str) -> str:
        system_prompt = """"""
        # TODO get chat_history by session_id
        # chat_history: list[tuple[str, str]] = []
        # texts = [f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n"]

        # do_strip = False
        # for user_input, response in chat_history:
        #     user_input = user_input.strip() if do_strip else user_input
        #     do_strip = True
        #     texts.append(f"{user_input} [/INST] {response.strip()} </s><s>[INST] ")
        # message = message.strip() if do_strip else message
        messages = [
            {
                "role": "user",
                "content": message,
            },
            {"role": "assistant", "content": context},
        ]
        text = ai_model.tokenizer.apply_chat_template(messages, tokenize=False)
        return text

    def search_context(self, query, n_results=1):
        query_embeddings = ai_model.encode_string(query)
        print(query_embeddings.shape)
        return vector_db.search(data=query_embeddings, n_results=n_results)

    async def get_response(self, session_id: int, input_msg: str) -> str:
        context = self.search_context(input_msg)
        prompt = self.get_prompt(session_id, input_msg, context)
        answer = ai_model.generate_answer(prompt)
        # TODO stream output
        return answer

    async def load_csv_file(self, file_name: str, model_name: str) -> bool:
        # read file named file_name and convert the content into a list of strings @Aisuko
        print(file_name)
        print(model_name)
        data = []
        with open(UPLOAD_FILE_PATH + file_name, "r") as file:
            # Create a CSV reader
            reader = csv.reader(file)
            # Iterate over each row in the CSV
            for row in reader:
                # Add the row to the list
                data.extend(row)
        print(data)
        embedding_list = ai_model.encode_string(data)
        print(embedding_list)
        vector_db.insert_list(embedding_list, data)

        return True
