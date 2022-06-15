dic = {
    "in": "body",
    "name": "updateBo",
    "description": "更新实体",
    "required": True,
    "schema": {
        "$ref": "#/definitions/OrderDiaConfig类型"
    }
}

body = str(dic).replace('\'', '"')
print(body)
