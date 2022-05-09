from utils.errorHandler import APIException

class ServerError(APIException):
    code = 500
    msg = "系统错误"
    error_code = 9999
    success = False


class ClientTypeError(APIException):
    code = 400
    msg = "client is invalid"
    error_code = 1006
    success = False


class ParameterException(APIException):
    code = 400
    msg = 'invalid parameter'
    error_code = 1000
    success = False

class MissingTokenError(APIException):
    code = 401
    msg = '缺少token'
    error_code = 9998
    success = False

class AuthInsufficient(APIException):
    code = 401
    msg = '权限不足'
    error_code = 9997
    success = False

class TokenExpirationError(APIException):
    code = 401
    msg = 'token已过期'
    error_code = 9996
    success = False

class ValError(APIException):
    code = 404
    msg = '参数错误或缺失'
    error_code = 9995
    success = False

class ProjectDoesNotExist(APIException):
    code = 200
    msg = '项目不存在'
    error_code = 9994
    success = False

class FileDoesNotExist(APIException):
    code = 200
    msg = '文件不存在'
    error_code = 9993
    success = False

class DateCanNotNone(APIException):
    code = 200
    msg = '查询日期不能为空'
    error_code = 9992
    success = False

class ExistAssociatedApiModule(APIException):
    code = 200
    msg = '存在关联Api模块，无法删除'
    error_code = 9991
    success = False

class DoesNotChooseProjectEnv(APIException):
    code = 200
    msg = '未选择项目环境'
    error_code = 9990
    success = False

class ParentCannotBeItself(APIException):
    code = 200
    msg = '父模块不能选择自己'
    error_code = 9989
    success = False

class DoesNotChooseModule(APIException):
    code = 200
    msg = '未选择模块'
    error_code = 9988
    success = False

class ExistAssociatedApi(APIException):
    code = 200
    msg = '存在关联Api，无法删除'
    error_code = 9987
    success = False

class ExistSameProject(APIException):
    code = 200
    msg = '存在重复项目名称'
    error_code = 9986
    success = False

class ExistAssociatedProjectEnv(APIException):
    code = 200
    msg = '存在关联项目环境，无法删除'
    error_code = 9985
    success = False

class UsernameOrPwdIsNull(APIException):
    code = 200
    msg = '用户名和密码不能为空'
    error_code = 9984
    success = False

class UsernameOrPwdIsFailed(APIException):
    code = 200
    msg = '用户名或密码错误'
    error_code = 9983
    success = False

class UserDisabled(APIException):
    code = 200
    msg = '用户已被禁用'
    error_code = 9982
    success = False

class AuthFailed(APIException):
    code = 401
    msg = '认证失败'
    error_code = 9981
    success = False

class DeleteYourself(APIException):
    code = 200
    msg = '不允许删除自身账号'
    error_code = 9980
    success = False

class NewPwdNotEqualOldPwd(APIException):
    code = 200
    msg = '确认密码与新密码不一致'
    error_code = 9979
    success = False

class OldPwdError(APIException):
    code = 200
    msg = '原密码错误'
    error_code = 9978
    success = False

class TestcaseNotSave(APIException):
    code = 200
    msg = '请先保存'
    error_code = 9977
    success = False

class CannotDeleteProgressTask(APIException):
    code = 200
    msg = '不能删除执行中的任务'
    error_code = 9976
    success = False

class ExistSameEnvVar(APIException):
    code = 200
    msg = '同一环境下存在重复变量名'
    error_code = 9976
    success = False
