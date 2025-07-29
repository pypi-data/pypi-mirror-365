import json
import pathlib
from usdm4.rules.rules_validation import RulesValidation4
from usdm3.rules.rules_validation_results import RulesValidationResults
from usdm4.api.wrapper import Wrapper
from usdm4.convert.convert import Convert
from usdm4.builder.builder import Builder


class USDM4:
    def __init__(self):
        self.root = self._root_path()
        self.validator = RulesValidation4(self.root)

    def validate(self, file_path: str) -> RulesValidationResults:
        return self.validator.validate(file_path)

    def convert(self, file_path: str) -> Wrapper:
        with open(file_path, "r") as file:
            data = json.load(file)
        return Convert.convert(data)

    def builder(self) -> Builder:
        return Builder(self.root)

    def minimum(self, study_name: str, sponsor_id: str, version: str) -> Wrapper:
        return Builder(self.root).minimum(study_name, sponsor_id, version)

    def from_json(self, data: dict) -> Wrapper:
        return Wrapper.model_validate(data)

    def _root_path(self) -> str:
        return pathlib.Path(__file__).parent.resolve()
