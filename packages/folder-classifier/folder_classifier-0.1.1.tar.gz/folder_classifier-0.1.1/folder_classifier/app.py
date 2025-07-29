import logging

from fastapi import FastAPI
from ray import serve

from folder_classifier.dto import ModelConfig, FolderClassificationResponse, FolderClassificationRequest

web_api = FastAPI(title=f"Folder Classifier API")


@serve.deployment
@serve.ingress(web_api)
class FolderClassifierAPI:
    def __init__(self, model_config: ModelConfig):
        assert model_config, "model_config is required"
        assert model_config.app_name and model_config.deployment, "Invalid ModelConfig values"
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing model: {model_config}")
        #self.model_handle = serve.get_deployment_handle(app_name=model_config.app_name, deployment_name=model_config.deployment)
        self.logger.info(f"Successfully initialized Folder Classifier API")

    @web_api.post("/predict")
    async def predict(self, request: FolderClassificationRequest) -> FolderClassificationResponse:
        result = ("matter", 0.9)  #await self.model_handle.remote(request)
        self.logger.info(f"Received request: {request}")
        return FolderClassificationResponse(category=result[0], confidence=result[1])
