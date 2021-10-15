'''==================================================
@IDE: PyCharm
@Time : 2021/9/10 14:14
@Author : wyp
@File : webapi_server.py
=================================================='''
from flask import Flask, request
from db_proxy import DbProxy
import datetime
import numpy as np
from flask_restful import Api
from common import make_new_response, get_geo
from settings import cfg

app = Flask(__name__)
# 用Api来绑定app
api = Api(app)

@app.route('/api/test', methods=['GET'])
def test_api():
    result = DbProxy.test(datetime.datetime.now())
    return {
        "username": "QQ",
        "age": 18,
        "result": result
    }


@app.route('/api/project/all', methods=['GET'])
def all_projects():
    ret = []
    # 查询数据
    objs = DbProxy.get_all_projects()
    for obj in objs:
        id, name, province, city, district, position, owner_company = obj
        # 拼接地址
        adress_detail = '%s%s%s' % (province, city, district)
        # 获取地理坐标
        lng = get_geo(adress_detail)
        a_project = {
            "id": id,
            "name": name,
            "adress_detail": adress_detail,
            "lnglat": lng,
            "position": position,
            "company": owner_company,
            # "link": "../details_page?projectid=%s" % id
            "link": "/user_manage/project/%s" % id
        }
        ret.append(a_project)
    print("项目信息: ", ret)
    # return HttpResponse(dct_projects)
    return make_new_response(ret)

@app.route('/api/project/info', methods=['GET'])
def project_info():
    # 获取参数
    lst_args = request.args.to_dict()
    project_id = lst_args.get('id', None)
    ret = None
    # 查询项目的详细信息
    objs = DbProxy.get_project_info(project_id)
    if len(objs) > 0:
        project_info = objs[0]
        project_name, abstract, monitor_results, map_loc = project_info

        lst_sub_project_table = []
        # 得到子项目列表
        lst_sub_id = DbProxy.get_sub_projects(project_id)
        for a_sub_id in lst_sub_id:
            lst_monitor_result = []
            sub_id = a_sub_id[0]
            sub_name = a_sub_id[1]
            # 得到子项目下的各个因素/监测结果
            lst_factors_id = DbProxy.get_monitor_factors(sub_id)
            if len(lst_factors_id) > 0:
                for a_factor_id in lst_factors_id:
                    factor_info = DbProxy.get_factor_info(a_factor_id[0])
                    # 筛选出字段
                    name, type, monitor_result, sensor_layout, monitor_conclusion = factor_info[0]
                    lst_monitor_result.append({
                        "type": type,
                        "monitor_result": monitor_result})
            lst_sub_project_table.append({
                "sub_id": sub_id,
                "sub_name": sub_name,
                "lst_monitor_result": lst_monitor_result
            })

        ret = {
            "project_id": project_id,
            "name": project_name,
            "abstract": abstract,   # 项目概况
            "monitor_results":  monitor_results,    # 监测成果
            "map_loc": map_loc,     # 地图
            "table": lst_sub_project_table  # 子项目列表
        }

    return make_new_response(ret)
        # return jsonify(ret)

@app.route('/api/subproject/info', methods=['GET'])
def sub_project_info():
    # 获取参数
    lst_args = request.args.to_dict()
    sub_id = lst_args.get('id', None)
    ret = None
    # 查询子项目的详细信息
    objs = DbProxy.get_sub_project_info(sub_id)
    if len(objs) > 0:
        project_info = objs[0]
        name, engine_cate, paper_time, detect_cate, data_analysis, analysis_by_synthesis,\
        sub_abstract,monitor_object,build_company,construct_company,supervise_company,detect_company,\
        general_layout = project_info
        ret = {
            "name": name,   # 子项目名称（隧道名）
            "engine_cate": engine_cate,   # 工程类别
            "paper_time":  str(paper_time),    # 报告时间
            "detect_cate": detect_cate,     # 检测类别
            "data_analysis": data_analysis,  # 数据分析和建议
            "analysis_by_synthesis": analysis_by_synthesis, # 综合分析

            "sub_abstract": sub_abstract,   # 子项目概况
            "monitor_object":  monitor_object,    # 监测对象
            "build_company": build_company,     # 建设单位
            "construct_company": construct_company,  # 施工单位
            "supervise_company": supervise_company, # 监理单位
            "detect_company": detect_company,   # 检测单位

            "general_layout":  general_layout,    # 子项目布置图
        }
    # return jsonify(ret)
    return make_new_response(ret)

@app.route('/api/subproject/factors', methods=['GET'])
def sub_project_factors():
    # 获取参数
    lst_args = request.args.to_dict()
    sub_id = lst_args.get('id', None)
    ret_info = None
    # 查询子项目底下的监测因素
    lst_factors_id = DbProxy.get_monitor_factors(sub_id)
    # print("查询子项目底下的监测因素: ", lst_factors_id)
    if len(lst_factors_id) > 0:
        lst_factors_info = []
        # 遍历监测因素，组合出信息
        for a_factor_id in lst_factors_id:
            factor_id = a_factor_id[0]
            factor_info = DbProxy.get_factor_info(factor_id)
            factor_name, type, monitor_result, sensor_layout, monitor_conclusion = factor_info[0]
            # 查询监测因素下的点位
            lst_points_id = DbProxy.get_monitor_points(factor_id)
            # print("查询监测因素下的点位lst_points_id: ", lst_points_id)
            lst_point_info = []
            if len(lst_points_id) > 0:
                # 遍历监测点位，组合出信息
                for a_point_id in lst_points_id:
                    a_point_id = a_point_id[0]
                    point_info = DbProxy.get_point_info(a_point_id)
                    # 点位信息
                    point_name,device_sn,cumulative_change,average_rate_day,average_rate_7days,trend,\
                    point_id,section_layout,section_monitor_conclusion,related_info = point_info[0]
                    lst_point_info.append({
                        "point_name": point_name,
                        "point_id": point_id,
                        "device_sn": device_sn,
                        "cumulative_change": cumulative_change,
                        "average_rate_day": average_rate_day,
                        "average_rate_7days": average_rate_7days,
                        "trend": trend
                    })

            lst_factors_info.append(
                {"factor_name": factor_name,
                 "id": factor_id,
                 "type": type,
                 "monitor_result": monitor_result,
                 "sensor_layout": sensor_layout,
                 "monitor_conclusion": monitor_conclusion,
                 "lst_point_info": lst_point_info
                 })
        ret_info = lst_factors_info
    # return jsonify(ret_info)
    return make_new_response(ret_info)

@app.route('/api/point/info', methods=['GET'])
def point_info():
    # 获取参数
    lst_args = request.args.to_dict()
    point_id = lst_args.get('id', None)
    # print("============", point_id)
    ret = None
    # 查询一个point的详细信息
    point_info = DbProxy.get_point_info(point_id)
    if len(point_info) > 0:
        point_name, device_sn, cumulative_change, average_rate_day, average_rate_7days, trend, \
        point_id, section_layout, section_monitor_conclusion, related_info = point_info[0]
        ret = {
            "point_id": point_id,
            "device_sn": device_sn,
            "point_name": point_name,   # 点位名称
            "section_layout": section_layout,   # 单点断面布置图
            "section_monitor_conclusion":  section_monitor_conclusion,    # 断面监测结论描述
            "related_info": related_info,     # 备注信息
        }
        # 曲线数据
    # return jsonify(ret)
    return make_new_response(ret)

@app.route('/api/unity/list', methods=['GET'])
def get_unity_device():
    ret = []
    # 查询数据
    objs = DbProxy.get_unity_list()
    for obj in objs:
        ret.append(obj[0])
    # print("=========一体化设备列表: ", ret)
    return make_new_response(ret)

@app.route('/api/unity/data', methods=['GET'])
def unitfy_data():
    # 获取参数
    lst_args = request.args.to_dict()
    device_sn = lst_args.get('device_sn', None)
    start = lst_args.get('start', None)
    end = lst_args.get('end', None)
    print('====', device_sn, start, end)
    # 查询数据
    objs = DbProxy.get_unity_data_raw(device_sn, start, end)
    # 初始化
    lst_tm, lst_val, lst_type1, lst_type2, lst_performance = [], [], [], [], []
    device_rest_time = None
    # print(objs)
    # 区分测量类型
    for obj in objs:    # meas_type,meas_time,value
        if obj[0] == 0:
            lst_type1.append([obj[1], obj[2]])
            sorted(lst_type1, key=(lambda x: x[0]))    # 按时间排序
        elif obj[0] == 1:
            lst_type2.append([obj[1], obj[2]])
            sorted(lst_type2, key=(lambda x: x[0]))    # 按时间排序
        else: ...
    print("两种数据1：", len(lst_type1))
    print("两种数据2：", len(lst_type2))

    # 获取设备外键ID
    device_obj = DbProxy.get_device_id(device_sn)
    # 获取间隔时间,以便计算分段均方差
    if len(device_obj):
        device_id = device_obj[0][0]
        print("Device外键id:", device_id)
        device_rest_time = DbProxy.get_device_rest_time(device_id)
        if len(device_rest_time):
            device_rest_time = float(device_rest_time[0][0]) * 60   # 单位分钟
            print("一体化参数时间间隔:", device_rest_time)

    for a_lst_type in [lst_type1, lst_type2]:
        if a_lst_type:
            # lst_combine = data_denoising(lst_combine)     # 过滤奇点
            sub_var = []
            tm, vals = zip(*a_lst_type)  # 分解出时间串、值串
            # 原生数据
            lst_tm.append(tm)
            lst_val.append(vals)
            if device_rest_time:   # 计算分段均方差
                sub_lst_time, sub_lst_val = [], []
                for i in range(1, len(tm)):
                    diff_time = datetime.datetime.timestamp(tm[i]) - datetime.datetime.timestamp(tm[i - 1])
                    if diff_time > device_rest_time and sub_lst_time:
                        temp = [str(sub_lst_time[0]), str(sub_lst_time[-1]), '%.2f' % np.std(sub_lst_val)]
                        # temp = '%.2f' % np.std(sub_lst_val)
                        sub_var.append(temp)
                        sub_lst_time = []
                        sub_lst_val = []
                        continue
                    elif i == len(tm) - 1:    # 最后一个
                        sub_lst_time.append(tm[i])
                        sub_lst_val.append(vals[i])
                        temp = [str(sub_lst_time[0]), str(sub_lst_time[-1]), '%.2f' % np.std(sub_lst_val)]
                        # temp = '%.2f' % np.std(sub_lst_val)
                        sub_var.append(temp)
                    else:
                        sub_lst_time.append(tm[i-1])
                    sub_lst_val.append(vals[i-1])
            # 指标数据组合
            lst_performance.append({
                                'data_len': '%d' % len(a_lst_type),    # 数据点数
                                'max': '%.2f' % np.max(vals),
                                'min': '%.2f' % np.min(vals),
                                'avg': '%.2f' % round(np.mean(vals), 2),
                                'sub_var': sub_var,
                                'whole_std': '%.2f' % round(np.std(vals), 2),
            })
        else:
            lst_tm.append([])
            lst_val.append([])
            lst_performance.append({
                                'data_len': 0,    # 数据点数
                                'max': 0,
                                'min': 0,
                                'avg': 0,
                                'sub_var': [],
                                'whole_std': 0,
            })
    # 返回数据
    ret = {"lst_tm": lst_tm, "lst_val": lst_val,
                "lst_performance": lst_performance}

    return make_new_response(ret)

@app.route('/api/outline/data', methods=['GET'])
def outline_data():
    # 获取参数
    lst_args = request.args.to_dict()
    device_sn = lst_args.get('device_sn', None)
    start = lst_args.get('start', None)
    end = lst_args.get('end', None)
    # print("========outline data: ", device_sn, start, end)
    ret = []
    # 查询数据
    objs = DbProxy.get_outline_data(device_sn, start, end)
    for obj in objs:
        meas_time, result = obj
        ret.append([str(meas_time), result])
    # print("=========轮廓算法值: ", device_sn, ret)
    return make_new_response(ret)






if __name__ == '__main__':
    app.run(host=cfg.get('srv', 'host'),
            port=int(cfg.get('srv', 'port')))



