from app.schemas.parse import ParseRequest, ResponseModel
from app.utils.app_exceptions import UnicornException, app_exception_handler
from app.schemas.const import MyErrorCode, GetErrMsg
from app.api.file_parser import FileParser
from app.core.config import Settings


class Service:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def parser(self, req: ParseRequest):
        fileParser = FileParser(req.path, req.is_local, self.settings)
        result = await fileParser.read_file()
        res = ResponseModel(success=False, data=result, code=0, message="")
        return res.get_dump()
