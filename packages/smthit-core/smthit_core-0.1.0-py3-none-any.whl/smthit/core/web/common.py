# !/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
@File   : http_common.py
@Author : bean
@Date   : 2024/9/5 11:28
@Desc   : 基于 flask web 相关扩展
"""
import importlib
import json
import logging
import os
import traceback
from json import JSONEncoder

from flask import jsonify
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def register_blueprints(app, package_name, package_path):
    rv = []
    logger.debug("begin to register blueprint...")
    fn = os.listdir(package_path)
    # for module_name in (fn[:-3] for fn in os.listdir(package_path) if fn.endswith('.py') and fn != '__init__.py'):
    fns = [fn[:-3] for fn in os.listdir(package_path) if fn.endswith('.py') and fn != '__init__.py']
    for module_name in fns:
        module_path = f"{package_name}.{module_name}"

    for module_name in fns:
        module_path = f"{package_name}.{module_name}"
        logger.debug(f"加载 {module_path}...")

        if not module_name.endswith("_view"):
            continue

        try:
            mod = importlib.import_module(module_path)
            blueprint_name = f"{module_name.split('_')[0]}_bp"
            blueprint = getattr(mod, blueprint_name)
            if blueprint is not None:
                app.register_blueprint(blueprint)
                rv.append(blueprint)
                logger.debug(f"注册蓝图 {blueprint_name}")
        except Exception as e:
            logger.warning(f"导入模块 {module_path}异常, 异常信息: {str(e)} \n {str(traceback.format_exc())}")
            continue
    else:
        pass

    logger.debug(f"has finished to register blueprint, total {len(rv)} blueprint views.")

    return rv


class Result(BaseModel):
    code: int = Field(description="返回码", nullable=False, default=0)
    msg: str = Field(description="返回信息", nullable=False, default='')
    data: object = Field(description="返回数据", nullable=True)

    @staticmethod
    def ok(msg='', data=None):
        return Result(code=0, msg=msg, data=data)

    @staticmethod
    def failed(code=500, msg='operation failed', data=None):
        return Result(code=code, msg=msg, data=data)

    def to_json(self):
        data = self.dict()
        return jsonify(data)

    def to_dict(self):
        return self.dict()

    def to_str(self):
        return json.dumps(self.dict(), ensure_ascii=False)


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()

        # 对于其他不支持的类型，可以调用父类的 default 方法
        return JSONEncoder.default(self, obj)

