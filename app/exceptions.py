class DocumentNotFoundError(Exception):
    def __init__(self, document_id: int):
        self.document_id = document_id