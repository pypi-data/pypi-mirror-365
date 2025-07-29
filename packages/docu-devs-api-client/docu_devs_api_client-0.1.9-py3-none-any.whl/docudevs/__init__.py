"""A client library for accessing DocuDevs API"""

from .client import AuthenticatedClient, Client
from .docudevs_client import DocuDevsClient, DocuDevsClientSync, UploadDocumentBody, UploadCommand, File, UploadFilesBody, TemplateFillRequest

__all__ = (
    "AuthenticatedClient",
    "Client",
    "DocuDevsClient",
    "DocuDevsClientSync",
    "UploadDocumentBody",
    "UploadCommand",
    "File",
    "UploadFilesBody",
    "TemplateFillRequest",
)
