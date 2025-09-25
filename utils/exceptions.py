# utils/exceptions.py
class RetrieveDBError(Exception):
    """Custom exception for errors during Firestore data retrieval."""
    def __init__(self, message="Error retrieving data from Firestore.", filename=None):
        super().__init__(message)
        self.filename = filename
        self.message = message

    def __str__(self):
        return f"{self.message} (File: {self.filename})"
    
class UpdateDBError(Exception):
    """Custom exception for errors during Firestore data update."""
    def __init__(self, message="Error updating data in Firestore.", filename=None):
        super().__init__(message)
        self.filename = filename
        self.message = message

    def __str__(self):
        return f"{self.message} (File: {self.filename})"
    
class FirestoreCredentialError(Exception):
    """Custom exception for Firestore credential errors."""
    def __init__(self, message="Firestore credential error.", filename=None):
        super().__init__(message)
        self.filename = filename
        self.message = message

    def __str__(self):
        return f"{self.message} (File: {self.filename})"
    
class FaceEmbeddingError(Exception):
    """Custom exception for errors related to face embeddings."""
    def __init__(self, message="Face embedding error.", filename=None):
        super().__init__(message)
        self.filename = filename
        self.message = message

    def __str__(self):
        return f"{self.message} (File: {self.filename})"
    
class InvalidSessionError(Exception):
    """Custom exception for invalid session errors."""
    def __init__(self, message="Invalid session error.", filename=None):
        super().__init__(message)
        self.filename = filename
        self.message = message

    def __str__(self):
        return f"{self.message} (File: {self.filename})"
    
class SpoofDetectionError(Exception):
    """Custom exception for spoof detection errors."""
    def __init__(self, message="Spoof detected in the given image.", filename=None):
        super().__init__(message)
        self.filename = filename
        self.message = message

    def __str__(self):
        return f"{self.message} (File: {self.filename})"
    
class APIError(Exception):
    """Custom exception for general API errors."""
    def __init__(self, message="API error.", filename=None):
        super().__init__(message)
        self.filename = filename
        self.message = message

    def __str__(self):
        return f"{self.message} (File: {self.filename})"